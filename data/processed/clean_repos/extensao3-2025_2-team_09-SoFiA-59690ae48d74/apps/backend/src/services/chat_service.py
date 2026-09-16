import json
import difflib
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Tuple, Any

from src.llm.factory import get_llm_instance
from src.llm.interface import LLMInterface, LLMMessage
from src.llm.schemas import get_intent_schema
from src.db.crud import crud_chat, crud_user
from src.tools.base import BaseTool
from src.db.models.models import ChatRole
from src.db.schemas.chat import ChatResponse
from src.core.logger import logger
from src.utils.constants import APPLICATION_USER_ID
from src.utils.enums import UserIntent


class ChatService:
    def __init__(self, db: Session, tools: list[BaseTool]):
        self.db = db
        self.llm: Optional[LLMInterface] = None
        self.tools: dict[str, BaseTool] = {t.name: t for t in tools}

    def _setup_llm(self, model_preference: str, model_name: str) -> None:
        logger.info(f"Initializing LLM: {model_preference} ({model_name})")
        match model_preference:
            case "remote":
                user = crud_user.get_user(self.db, user_id=APPLICATION_USER_ID)
                if not user or not user.api_key:
                    raise HTTPException(status_code=503, detail="Chave da API do Gemini API não configurada.")
                self.llm = get_llm_instance("remote", model_name=model_name, apiKey=user.api_key)
            case "local":
                self.llm = get_llm_instance("local", model_name=model_name)
            case _:
                self.llm = get_llm_instance("dummy")

    def _ensure_dict(self, data: Any) -> dict:
        """
        Sanitizes LLM output. If the LLM returns a list (e.g. [result]),
        it extracts the first item. Returns an empty dict if invalid.
        """
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                return data[0]
            return {}
        if isinstance(data, dict):
            return data
        return {}

    def _detect_intent(self, message: str) -> UserIntent:
        """Detects user intent using classification."""
        logger.debug(f"Detecting intent for: '{message}'")
        schema = get_intent_schema()

        prompt = f"""You are an intent classifier for SoFiA, a personal finance assistant.

        USER MESSAGE: "{message}"

        YOUR JOB:
        Classify the user's intent into ONE category:
        - "expense": User wants to REGISTER a new spending transaction (bought, paid, spent).
        - "income": User wants to REGISTER money received (salary, gift).
        - "query": User wants to KNOW about past data (how much spent, list transactions, balance).
        - "chat": General conversation, greetings, or unclear intent.

        EXAMPLES:
        "Comprei um vestido" → {{"intent": "expense"}}
        "Gastei 50 reais no almoço" → {{"intent": "expense"}}
        "Quanto eu gastei esse mês?" → {{"intent": "query"}}
        "Assinei o Netflix por 40 reais todo dia 5" → {{"intent": "recurrence"}}
        "Meu salário é 5000 todo dia 1" → {{"intent": "recurrence"}}
        "Vou pagar aluguel todo mês" → {{"intent": "recurrence"}}
        "Me mostre minhas compras recentes" → {{"intent": "query"}}
        "Quanto gastei com Uber?" → {{"intent": "query"}}
        "Recebi meu pagamento" → {{"intent": "income"}}
        "Oi, tudo bem?" → {{"intent": "chat"}}

        OUTPUT ONLY VALID JSON: {{"intent": "expense"}}"""
        raw_result = self.llm.extract_structured_data(prompt, schema)
        result = self._ensure_dict(raw_result)
        intent_str = result.get("intent", UserIntent.CHAT.value)
        try:
            return UserIntent(intent_str.lower())
        except ValueError:
            return UserIntent.CHAT

    def _detect_cancellation(self, message: str) -> bool:
        schema = {"type": "object", "properties": {"wants_to_cancel": {"type": "boolean"}}, "required": ["wants_to_cancel"]}
        prompt = f"""Analyze: "{message}". Does user want to CANCEL/STOP? Output JSON."""
        raw_result = self.llm.extract_structured_data(prompt, schema)
        result = self._ensure_dict(raw_result)
        return result.get("wants_to_cancel", False)

    def _validate_and_clean_params(self, intent: UserIntent, params: dict[str, Any]) -> dict[str, Any]:
        cleaned = params.copy()
        if "category_name" in cleaned and intent in [UserIntent.EXPENSE, UserIntent.QUERY]:
            extracted_cat = cleaned["category_name"]
            if extracted_cat is None or not isinstance(extracted_cat, str):
                del cleaned["category_name"]
            else:
                tool = self.tools[intent.value]
                valid_categories = tool.schema["properties"]["category_name"]["enum"]
                if extracted_cat in valid_categories:
                    pass
                else:
                    matches = difflib.get_close_matches(extracted_cat, valid_categories, n=1, cutoff=0.6)
                    if matches:
                        logger.info(f"✨ Auto-corrected category '{extracted_cat}' to '{matches[0]}'")
                        cleaned["category_name"] = matches[0]
                    else:
                        logger.warning(f"❌ Validation Failed: '{extracted_cat}' is not a valid category. Removing it.")
                        del cleaned["category_name"]
        return cleaned

    def _check_missing_fields(self, params: dict[str, object], tool: BaseTool) -> list[str]:
        """
        Checks which required fields are still missing.
        Uses tool.required_fields (business logic) if available,
        otherwise falls back to schema 'required' (LLM strictness).
        """
        required = getattr(tool, "required_fields", tool.schema.get("required", []))
        missing = []
        for field in required:
            val = params.get(field)
            if val in (None, "") or (isinstance(val, (int, float)) and val == 0):
                missing.append(field)
        return missing

    def _execute_tool(self, intent: UserIntent, params: dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
        if intent.value in self.tools:
            try:
                return self.tools[intent.value].execute(params, APPLICATION_USER_ID)
            except Exception as e:
                logger.error(f"Tool Execution Error ({intent.value})", exc_info=True)
                return f"System: Error executing tool: {e}", "System Error"
        return None, None

    def _generate_response_with_context(self, session_id: int, system_context: str) -> str:
        history = crud_chat.get_history(self.db, session_id, limit=10)
        current_date = datetime.now().strftime("%Y-%m-%d (%A)")
        system_message = (
            f"Current Date: {current_date}. "
            "You are SoFiA, a personal finance assistant. "
            "Speak Portuguese (Brazil). "
            f"IMPORTANT CONTEXT FROM DATABASE/SYSTEM: {system_context}"
        )
        messages = [LLMMessage(role="system", content=system_message)]
        messages.extend([LLMMessage(role=m.role.value, content=m.content) for m in history])

        response_text = self.llm.get_chat_response(messages)
        crud_chat.add_message(self.db, session_id, ChatRole.ASSISTANT, response_text)
        return response_text

    def _handle_conversation_flow(
            self, session_id: int, message: str
    ) -> tuple[str, Optional[str]]:

        session_state = crud_chat.get_session_state(self.db, session_id)
        pending_tool = session_state.get("pending_tool") if session_state else None
        collected_params = session_state.get("collected_params", {}) if session_state else {}

        logger.info(f"Session {session_id} state: pending_tool={pending_tool}")
        crud_chat.add_message(self.db, session_id, ChatRole.USER, message, meta_data=collected_params)

        if pending_tool:
            if self._detect_cancellation(message):
                crud_chat.clear_session_state(self.db, session_id)
                self.db.flush()
                return self._generate_response_with_context(session_id, "System: User canceled operation."), None

            intent = UserIntent(pending_tool)
            tool = self.tools[intent.value]

            extraction_prompt = tool.get_extraction_prompt(message, partial=collected_params)
            raw_new_params = self.llm.extract_structured_data(extraction_prompt, tool.schema)
            new_params = self._ensure_dict(raw_new_params)
            logger.info(f"📥 Raw LLM Extraction (Flow): {json.dumps(new_params, ensure_ascii=False)}")
            merged_params = {**collected_params, **new_params}
            final_params = self._validate_and_clean_params(intent, merged_params)
            logger.info(f"🧹 Params after Validation: {json.dumps(final_params, ensure_ascii=False)}")
            was_category_rejected = "category_name" in merged_params and "category_name" not in final_params
            missing_fields = self._check_missing_fields(final_params, tool)
            if was_category_rejected:
                logger.warning("⚠️ Category was rejected during validation. Forcing user to re-select.")
                if "category_name" not in missing_fields:
                    missing_fields.append("category_name")
            if not missing_fields:
                logger.info(f"✅ All fields collected! Executing {intent.value}")
                description, action_type = self._execute_tool(intent, final_params)
                crud_chat.clear_session_state(self.db, session_id)
                self.db.flush()
                if intent == UserIntent.QUERY:
                    sys_ctx = (
                        f"System: The database query returned: '{description}'. "
                        "Answer the user's question based strictly on these findings. "
                    )
                else:
                    sys_ctx = (
                        f"System: SUCCESS. The transaction has been REGISTERED in the database: '{description}'. "
                        "Inform the user it is done. Do NOT ask for confirmation."
                    )

                return self._generate_response_with_context(session_id, sys_ctx), action_type
            else:
                crud_chat.update_session_state(
                    self.db, session_id=session_id, pending_tool=pending_tool, collected_params=final_params, missing_fields=missing_fields
                )
                self.db.flush()
                return self._generate_follow_up_question(session_id, intent, final_params, missing_fields), None

        logger.info("🆕 NO FLOW - detecting new intent")
        intent = self._detect_intent(message)
        logger.info(f"🧠 Detected Intent: {intent.value}")

        if intent in [UserIntent.EXPENSE, UserIntent.INCOME, UserIntent.QUERY]:
            tool = self.tools[intent.value]
            logger.info(f"🔍 Extracting data for tool: {tool.name}")
            extraction_prompt = tool.get_extraction_prompt(message)
            raw_params_from_llm = self.llm.extract_structured_data(extraction_prompt, tool.schema)
            raw_params = self._ensure_dict(raw_params_from_llm)
            logger.info(f"📥 Raw LLM Extraction (New): {json.dumps(raw_params, ensure_ascii=False)}")
            final_params = self._validate_and_clean_params(intent, raw_params)
            logger.info(f"🧹 Params after Validation: {json.dumps(final_params, ensure_ascii=False)}")

            was_category_rejected = "category_name" in raw_params and "category_name" not in final_params

            # UPDATED: Pass 'tool' instead of 'tool.schema'
            missing_fields = self._check_missing_fields(final_params, tool)

            if was_category_rejected:
                logger.warning("⚠️ Category was rejected during validation. Forcing user to re-select.")
                if "category_name" not in missing_fields:
                    missing_fields.append("category_name")

            if not missing_fields:
                logger.info(f"✅ Complete! Executing {intent.value}")
                description, action_type = self._execute_tool(intent, final_params)

                if intent == UserIntent.QUERY:
                    sys_ctx = (
                        f"System: The database query returned: '{description}'. "
                        "Answer the user's question based strictly on these findings. "
                        "Do NOT ask for dates or categories again, the search is done."
                    )
                else:
                    sys_ctx = (
                        f"System: SUCCESS. The transaction has been REGISTERED in the database: '{description}'. "
                        "Inform the user it is done. Do NOT ask for confirmation."
                    )

                return self._generate_response_with_context(session_id, sys_ctx), action_type
            else:
                logger.info(f"🚀 STARTING {intent.value} flow - missing {missing_fields}")
                crud_chat.update_session_state(
                    self.db, session_id=session_id, pending_tool=intent.value, collected_params=final_params, missing_fields=missing_fields
                )
                self.db.flush()
                return self._generate_follow_up_question(session_id, intent, final_params, missing_fields), None

        else:
            logger.info("💬 General chat")
            return self._generate_response_with_context(session_id, "System: General conversation."), None

    def _generate_follow_up_question(self, session_id: int, intent: UserIntent, current_params: dict, missing: list[str]) -> str:
        first_missing = missing[0]
        params_str = json.dumps(current_params, ensure_ascii=False)

        if first_missing == 'category_name' and intent in [UserIntent.EXPENSE, UserIntent.QUERY]:
            tool = self.tools[intent.value]
            all_categories = tool.schema["properties"]["category_name"]["enum"]
            category_list_str = "\n".join(f"- {cat}" for cat in all_categories)

            system_context = f"""System: The user tried to specify a category that doesn't exist.
            We successfully extracted: {params_str}.
            Ask them to pick from this EXACT list:
            {category_list_str}
            """
        else:
            system_context = (
                f"System: User is creating a '{intent.value}'. "
                f"We currently have these parameters: {params_str}. "
                f"The following field is MISSING and required: '{first_missing}'. "
                "Ask the user for this specific missing information."
            )
        # ------------------------------------------------

        return self._generate_response_with_context(session_id, system_context)

    def process_user_message(
            self, session_id: int, message: str, model_preference: str, model_name: str
    ) -> Tuple[str, Optional[str]]:
        self._setup_llm(model_preference, model_name)
        try:
            response_text, action_taken = self._handle_conversation_flow(session_id, message)
            self.db.commit()
            return response_text, action_taken
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def create_session_and_reply(self, message: str, model_preference: str, model_name: str) -> ChatResponse:
        self._setup_llm(model_preference, model_name)
        try:
            title = self._generate_title(message)
            session = crud_chat.create_session(self.db, user_id=APPLICATION_USER_ID, title=title)
            response_text, action_taken = self._handle_conversation_flow(session.id, message)
            self.db.commit()
            self.db.refresh(session)
            return ChatResponse(
                response=response_text,
                session_id=session.id,
                session_title=title,
                action_taken=action_taken,
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating session: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def _generate_title(self, first_message: str) -> str:
        if not self.llm: return "New Chat"
        try:
            prompt = LLMMessage(role="user", content=f"Summarize in 3-5 words for title (Portuguese): '{first_message}'")
            return self.llm.get_chat_response([prompt]).strip().strip('"')
        except Exception:
            return "New Chat"