from fastapi import APIRouter, HTTPException
from app.schemas.question import QuestionSchema
from app.schemas.alternativa import AlternativaSchema
from app.schemas.chatmessage import ChatMessageSchema
from app.routes_back.questionDB_routes import getQuestionByID, getRandomQuestionByHabilidade
from app.routes_back.chatDB_routes import getChatByID
from app.routes_back.chatmessageDB_routes import createChatMessage
from app.routes_back.chatmessageDB_routes import getChatsMessagesByChat

router = APIRouter(prefix="/questions", tags=["questions"])

@router.get("/{id}")
def retrieveQuestionByID(id: int):
    """
        Retorna um QuestionSchema da questão correspondente a um id.

        Ex de uso: GET http://127.0.0.1:8000/chat/questions/3
    """
    questions = getQuestionByID(id)
    if not questions:
        raise HTTPException(status_code=500, detail="Não existe questão com esse id")
    return questions

@router.get("/random/{chat_id}")
def randomQuestion(chat_id: int):
    """
        Faz o bot "mandar uma mensagem" contendo uma questão nova aleatória, dado o id do chat. Retorna uma lista de ChatMessagesSchemas da conversa inteira.

        Ex de uso: GET http://127.0.0.1:8000/questions/random/5

        Retorno: {"mensagens": [ChatMessageSchema1, ChatMessageSchema2, ...]}
    """
    chat = getChatByID(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    existing = getChatsMessagesByChat(chat_id) or []
    used_ids = [m.question_id for m in existing if m.question_id is not None]
    question = getRandomQuestionByHabilidade(chat.habilidade, exclude_ids=used_ids)
    if not question:
        raise HTTPException(
            status_code=404,
            detail="Nenhuma questão disponível para esta matéria no momento",
        )
    question_text = question.enunciado + "\n"
    for alt in question.alternativas:
        question_text += "\n" + str(alt.letra) + ") " + str(alt.texto)
    id_aleatorio = question.id
    createChatMessage(chat_id, "llm", question_text, id_aleatorio)
    chat_messages = getChatsMessagesByChat(chat_id)
    return chat_messages if chat_messages is not None else []