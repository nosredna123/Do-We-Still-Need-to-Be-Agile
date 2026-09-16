import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from src.llm.interface import LLMInterface, LLMMessage
from src.core.logger import logger


class RemoteLLM(LLMInterface):
    """
    A pure wrapper for the Google Gemini API.
    Contains ZERO business logic - just API calls.
    """

    def __init__(
            self, api_key: str, model_name: str = "gemini-2.5-flash-lite",
    ):
        self.api_key = api_key
        self.model_name = model_name
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            logger.error("Failed to configure Gemini client", exc_info=True)
            raise ValueError(f"Failed to configure Gemini client: {e}")

    def _convert_to_gemini_history(
            self, messages: List[LLMMessage]
    ) -> List[Dict[str, Any]]:
        """
        Converts our internal message format to the Gemini format.
        """
        gemini_history = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else msg["role"]
            if role in ["user", "model"]:
                gemini_history.append({"role": role, "parts": [msg["content"]]})
        return gemini_history

    def get_chat_response(self, messages: List[LLMMessage]) -> str:
        """
        Generates a natural language response using the Gemini API.
        """
        system_prompt = next(
            (m["content"] for m in messages if m["role"] == "system"), None
        )
        chat_history = self._convert_to_gemini_history(messages)
        if not chat_history:
            return "Error: No user prompt provided."
        prompt = chat_history.pop()
        try:
            model_instance = self.model
            if system_prompt:
                model_instance = genai.GenerativeModel(
                    self.model_name, system_instruction=system_prompt
                )
            chat_session = model_instance.start_chat(history=chat_history)
            response = chat_session.send_message(prompt["parts"])
            return response.text
        except (google_exceptions.GoogleAPICallError, ValueError) as e:
            logger.error("Error communicating with Gemini API", exc_info=True)
            return f"Error communicating with Gemini API: {e}"
        except Exception as e:
            logger.error("Unexpected error in get_chat_response", exc_info=True)
            return f"An unexpected error occurred: {e}"

    def extract_structured_data(
            self,
            prompt: str,
            output_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Pure extraction wrapper. NO BUSINESS LOGIC.

        Takes:
        - prompt: A complete extraction prompt (caller builds this)
        - output_schema: The JSON schema to enforce

        Returns:
        - Parsed JSON matching the schema (or error dict)
        """
        logger.debug("Starting Structured Data Extraction")
        logger.info("=== PROMPT SENT TO GEMINI ===")
        logger.info(prompt)
        logger.info("=== SCHEMA ===")
        logger.info(json.dumps(output_schema, indent=2, ensure_ascii=False))
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.0,
            top_p=1,
        )
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            logger.info("Raw Gemini JSON Response", extra={"payload": {"text": response.text}})
            parsed = json.loads(response.text)
            return parsed
        except json.JSONDecodeError as e:
            logger.warning("JSON decode error", extra={"payload": response.text if 'response' in locals() else ""})
            return {"error": "invalid_json"}
        except Exception as e:
            logger.error("Unexpected error in extract_structured_data", exc_info=True)
            return {"error": "extraction_failed"}