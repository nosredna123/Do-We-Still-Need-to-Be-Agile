from dotenv import load_dotenv
from supabase import create_client, Client
import os
from app.schemas.chatmessage import ChatMessageSchema

MAX_CHATMESSAGE_TEXTO_LEN = 5000


def _normalize_message_text(texto: str | None) -> str:
    if texto is None:
        return ""
    text = str(texto)
    if len(text) <= MAX_CHATMESSAGE_TEXTO_LEN:
        return text
    return text[:MAX_CHATMESSAGE_TEXTO_LEN]

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def getChatsMessagesByChat(chat_id: int):
    """
    Retorna todas as mensagens de um chat em formato ChatMessageSchema, dado o chat_id.
    """
    response = (
        supabase.table("ChatMessage")
        .select("*")
        .eq("chat_id", chat_id)
        .order("timestamp", desc=False)  # asc, do mais antigo ao mais recente
        .execute()
    )
    rows = response.data
    if rows:
        messages = []
        for row in rows:
            message = ChatMessageSchema(
                id=row.get('id'),
                chat_id=row.get('chat_id'),
                author=row.get('author'),
                texto=_normalize_message_text(row.get('texto')),
                timestamp=row.get('timestamp'),
                question_id=row.get('question_id'),
                essay_id=row.get('essay_id')
            )
            messages.append(message)
        return messages
    else:
        return None

def createChatMessage(chat_id: int, author: str, texto: str, question_id: int | None = None, essay_id: int | None = None):
    """
    Registra uma nova mensagem dado o id de chat, autor (system/user/llm) e id de questão ou redação associada.

    Retorna o ChatMessageSchema se obteve sucesso.
    """
    texto_normalizado = _normalize_message_text(texto)

    payload = {"chat_id": chat_id, "author": author, "texto": texto_normalizado}

    if question_id is not None:
        payload["question_id"] = question_id
    elif essay_id is not None:
        payload["essay_id"] = essay_id

    response = (
        supabase.table("ChatMessage")
        .insert(payload)
        .execute()
    )

    rows = response.data
    if rows:
        message = ChatMessageSchema(
            id=rows[0].get('id'),
            chat_id=rows[0].get('chat_id'),
            author=rows[0].get('author'),
            texto=_normalize_message_text(rows[0].get('texto')),
            timestamp=str(rows[0].get('timestamp')),
            question_id=rows[0].get('question_id'),
            essay_id=rows[0].get('essay_id')
        )
        return message
    else:
        return None

def updateChatMessage(message: ChatMessageSchema):
    """
    Atualiza uma mensagem no banco de dados dado um ChatMessageSchema da mensagem modificada.

    Retorna o mesmo ChatMessageSchema caso tenha sido modificada com sucesso.
    """
    response = (
        supabase.table("ChatMessage")
        .update({"id": message.id, "chat_id": message.chat_id, "author": message.author, "texto": message.texto, "timestamp": message.timestamp, "question_id": message.question_id, "essay_id": message.essay_id})
        .eq("id", message.id)
        .execute()
    )
    rows = response.data
    if rows:
        return message
    else:
        return None

def deleteChatMessage(id: int):
    """
    Recebe um id de mensagem e apaga a mensagem, retornando True ou False dependendo do sucesso.
    """
    response = (
        supabase.table("ChatMessage")
        .delete()
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        return True
    else:
        return False

def getMessagesRelatedToQuestion(chat_id: int, question_id: int) -> tuple[ChatMessageSchema, list[ChatMessageSchema]]:
    """
        Retorna os chat_messages de um chat considerando apenas o id de uma questão
    """
    response = supabase.table("ChatMessage") \
        .select("*") \
        .eq("chat_id", chat_id) \
        .eq("question_id", question_id) \
        .order("timestamp", desc=True) \
        .execute()

    rows = response.data
    if not rows:
        return None, []

    messages = []
    for row in rows:
        message = ChatMessageSchema(
            id=row.get('id'),
            chat_id=row.get('chat_id'),
            author=row.get('author'),
            texto=_normalize_message_text(row.get('texto')),
            timestamp=row.get('timestamp'),
            question_id=row.get('question_id'),
            essay_id=row.get('essay_id')
        )
        messages.append(message)

    messages = list(reversed(messages))  # ordem cronológica

    question_message = messages[0]       # primeiro = texto da questão
    history_messages = messages[1:]      # restante = histórico normal

    return question_message, history_messages

def getMessagesRelatedToEssay(chat_id: int, essay_id: int) -> tuple[ChatMessageSchema, list[ChatMessageSchema]]:
    """
        Retorna os chat_messages de um chat considerando apenas o id de um essay
    """
    response = supabase.table("ChatMessage") \
        .select("*") \
        .eq("chat_id", chat_id) \
        .eq("essay_id", essay_id) \
        .order("timestamp", desc=True) \
        .execute()

    rows = response.data
    if not rows:
        return None, []

    messages = []
    for row in rows:
        message = ChatMessageSchema(
            id=row.get('id'),
            chat_id=row.get('chat_id'),
            author=row.get('author'),
            texto=row.get('texto'),
            timestamp=row.get('timestamp'),
            question_id=row.get('question_id'),
            essay_id=row.get('essay_id')
        )
        messages.append(message)

    messages = list(reversed(messages))  # ordem cronológica

    essay_message = messages[0:2]          # primeiro = texto do tema/redação
    history_messages = messages[2:]      # restante = histórico normal

    return essay_message, history_messages