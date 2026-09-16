from app.routes_back.essayDB_routes import getEssayByID, createEssay, updateEssay as updateEssayInDB
from app.routes_back.themeDB_routes import getRandomTheme, getThemeById
from fastapi import APIRouter, HTTPException
from app.schemas.question import QuestionSchema
from app.schemas.alternativa import AlternativaSchema
from app.schemas.chatmessage import ChatMessageSchema
from app.routes_back.questionDB_routes import getQuestionByID, getRandomQuestionByHabilidade
from app.routes_back.chatDB_routes import getChatByID
from app.routes_back.chatmessageDB_routes import createChatMessage
from app.routes_back.chatmessageDB_routes import getChatsMessagesByChat

router = APIRouter(prefix="/themes", tags=["themes"])

@router.get("/random/{chat_id}")
def randomTheme(chat_id: int):
    """
        Faz o bot "mandar uma mensagem" contendo um tema novo aleatório, dado o id do chat. Retorna uma lista de ChatMessagesSchemas da conversa inteira.

        Ex de uso: GET http://127.0.0.1:8000/themes/random/1

        Retorno: {"mensagens": [ChatMessageSchema1, ChatMessageSchema2, ...]}
    """
    chat = getChatByID(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    existing = getChatsMessagesByChat(chat_id) or []
    used_theme_ids = []

    print("Used Themes", used_theme_ids)
    for message in existing:
        if message.essay_id is None:
            continue
        essay = getEssayByID(message.essay_id)
        if essay:
            used_theme_ids.append(essay.theme)
    theme = getRandomTheme(exclude_ids=used_theme_ids)
    print("Theme", theme)

    if not theme:
        raise HTTPException(
            status_code=404,
            detail="Nenhum tema disponível a mais",
        )

    essay = createEssay(theme.id, "")
    print("Essay: ", essay)
    if not essay:
        raise HTTPException(status_code=500, detail="Erro ao criar redação")
    t = createChatMessage(chat_id, "llm", theme.name, essay_id=essay.id)
    
    print("chatMessage: ", t)

    chat_messages = getChatsMessagesByChat(chat_id)
    return chat_messages if chat_messages is not None else []

@router.get("/{id}")
def retrieveThemeByID(id: int):
    """
        Retorna um tema de redação.

        Ex de uso: GET http://127.0.0.1:8000/chat/themes/1
    """
    essay = getThemeById(id)
    if not essay:
        raise HTTPException(status_code=500, detail="Não existe tema com esse id")
    return essay



