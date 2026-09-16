import asyncio
import re

from app.routes_back.essayDB_routes import getEssayByID
from app.routes_back.themeDB_routes import getThemeById
from app.services.llm_service import LLMService
from app.routes_back.chatmessageDB_routes import getMessagesRelatedToEssay, getMessagesRelatedToQuestion
from app.routes_back.chatDB_routes import getChatByID
from app.routes_back.habilcompDB_routes import getHabilidadeByID
from app.routes_back.questionDB_routes import getQuestionByID

# from testes.llm_service.prompts import prompt4 as prompt1, prompt5 as prompt2, prompt6
from testes.llm_service.prompts import prompt1, prompt2, prompt6

def _is_hint_request(query: str) -> bool:
    normalized = query.strip().lower()
    return normalized in {'comando: give-hint', 'give-hint', '/dica', 'gerar dica discreta'} or normalized.startswith('comando: give-hint')


def _trim_hint_response(text: str) -> str:
    compact = ' '.join(text.replace('\n', ' ').split())
    sentences = re.split(r'(?<=[.!?])\s+', compact)
    short_text = ' '.join(sentences[:2]).strip()
    return short_text[:260].rstrip(' ,;:-')


def getAnswertheQuery(chat_id: int, question_id: int, query: str, chat_status: int = 0) -> str:
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
        question = getQuestionByID(question_id)
        if question:

            # Gerando o enunciado da questão + Alternativas + Resposta correta
            question_text = question.enunciado + "\n" + "\n".join([alternativa.letra + ") " + alternativa.texto for alternativa in question.alternativas])
            question_text = question_text + "\nAlternativa correta: " + str(question.resposta_correta)

            _, history_messages = getMessagesRelatedToQuestion(chat_id, question_id)

            history = [
                ("user" if msg.author == "user" else "assistant", msg.texto)
                for msg in history_messages[-6:]
            ]

        else:
            question_text = "Questão não encontrada"
    else:
        question_text = "Sessão de estudos ENEM — o aluno ainda não abriu uma questão específica."

    if _is_hint_request(query):
        hint_prompt = """
    ## # Papel

    Você é um Mentor Socrático que precisa dar apenas uma dica curta e discreta sobre {knowledge_area}.

    ---

    ## # Contexto da Questão

    {question}

    ---

    ## # Regras da Dica

    - Responda em no máximo 2 frases curtas.
    - Não revele gabarito, alternativa correta, resultado final ou passo a passo completo.
    - Não faça perguntas no final.
    - Foque em um único ponto de partida para o raciocínio.
    - Use linguagem simples e direta.
    - Seja realmente discreto: uma pista, não uma explicação.
    """
        llm_service = LLMService("google", 0, prompt=hint_prompt, history=history[-4:])
    else:
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
        answer = "".join(parts) if parts else "Não foi possível gerar uma resposta no momento."
        if _is_hint_request(query):
            return _trim_hint_response(answer)
        return answer

    return asyncio.run(collect())

def getAnswertheQueryEssay(chat_id: int, essay_id: int, query: str) -> str:
    """
    Chama a LLM (Gemini via LangChain) e retorna o texto completo da resposta.
    Usado por PUT /chat/prompt/redacao/{chat_id}/{essay_id}/{texto}.
    """
    chat = getChatByID(chat_id)
    if not chat:
        return "Não foi possível encontrar este chat."

    history: list[tuple[str, str]] = []
    theme = "Sessão de redação ENEM — o aluno ainda não abriu um tema específico."
    essay_text = "Sessão de estudos ENEM — o aluno ainda não inseriu uma redação."
    if essay_id:
        essay = getEssayByID(essay_id)
        if essay:
            theme_data = getThemeById(essay.theme)
            theme = theme_data.name if theme_data else "Tema não encontrado"
            essay_text = essay.text

            _, history_messages = getMessagesRelatedToEssay(chat_id, essay_id)

            history = [
                ("user" if msg.author == "user" else "assistant", msg.texto)
                for msg in history_messages[-6:]
            ]

        else:
            theme = "Redação não encontrada"
            essay_text = "Redação não encontrada"

    llm_service = LLMService("google", 0, prompt=prompt6, history=history)

    async def collect() -> str:
        parts: list[str] = []
        async for token in llm_service.call_agent_red(
            theme=theme,
            essay=essay_text,
            query=query,
        ):
            if token:
                parts.append(str(token))
        return "".join(parts) if parts else "Não foi possível gerar uma resposta no momento."

    return asyncio.run(collect())