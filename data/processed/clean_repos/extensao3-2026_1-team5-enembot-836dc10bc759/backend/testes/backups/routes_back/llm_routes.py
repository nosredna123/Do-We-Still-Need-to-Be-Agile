import asyncio

from app.services.llm_service import LLMService
from app.routes_back.chatmessageDB_routes import getMessagesRelatedToQuestion
from app.routes_back.chatDB_routes import getChatByID
from app.routes_back.habilcompDB_routes import getHabilidadeByID
from testes.llm_service.prompts import prompt1, prompt2


def getAnswertheQuery(chat_id: int, question_id: int, query: str, chat_status=0) -> str:
    """
    Chama a LLM (Gemini via LangChain) e retorna o texto completo da resposta.
    Usado por PUT /chat/prompt/{chat_id}/{question_id}/{texto}.
    """
    chat = getChatByID(chat_id)
    if not chat:
        return "Não foi possível encontrar este chat."

    knowledge_area = getHabilidadeByID(chat.habilidade) or "ENEM"

    history: list[tuple[str, str]] = []
    if question_id:
        question_message, history_messages = getMessagesRelatedToQuestion(chat_id, question_id)
        if question_message:
            question_text = question_message.texto
            history = [
                ("user" if msg.author == "user" else "assistant", msg.texto)
                for msg in history_messages[-6:]
            ]
        else:
            question_text = "Questão em andamento."
    else:
        question_text = "Sessão de estudos ENEM — o aluno ainda não abriu uma questão específica."

    if chat_status == 0:
        prompt = prompt1
    elif chat_status == 1:
        prompt = prompt2

    llm_service = LLMService("google", 0, prompt=prompt, history=history)

    async def collect() -> str:
        parts: list[str] = []
        async for token in llm_service.call_agent(
            knowledge_area=knowledge_area,
            question=question_text,
            query=query,
        ):
            if token:
                parts.append(str(token))
        return "".join(parts) if parts else "Não foi possível gerar uma resposta no momento."

    return asyncio.run(collect())
