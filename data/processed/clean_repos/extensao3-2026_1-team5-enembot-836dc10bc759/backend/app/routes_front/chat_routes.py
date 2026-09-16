from fastapi import APIRouter, HTTPException, Body
from app.schemas.user import UserSchema
from app.schemas.chat import ChatSchema
from app.schemas.chatmessage import ChatMessageSchema
from app.routes_back.chatDB_routes import getChatsByUser
from app.routes_back.chatDB_routes import createChat as createChatInDB
from app.routes_back.chatDB_routes import getChatByID
from app.routes_back.chatDB_routes import updateChat
from app.routes_back.chatDB_routes import deleteChat as deleteChatInDB
from app.routes_back.chatmessageDB_routes import getChatsMessagesByChat
from app.routes_back.chatmessageDB_routes import createChatMessage
from app.routes_back.llm_routes import getAnswertheQuery, getAnswertheQueryEssay

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/")
def retrieveAllChats():
    """
        Chama função que retorna a lista de todos os ChatSchemas do user ativo no formato {"chats": [ChatSchema1, ChatSchema2, ...]}.

         Ex de uso: POST http://127.0.0.1:8000/chat/
    """
    chats = getChatsByUser(4) #por enquanto usa o user 4 sempre
    return chats if chats is not None else []

@router.get("/{chat_id}")
def retrieveMessagesByChat(chat_id: int):
    """
            Retorna uma lista com todas as mensagens de um chat.

            Ex de uso: GET http://127.0.0.1:8000/chat/5

            Retorno:
            [
              {
                "id": 6,
                "chat_id": 5,
                "author": "user",
                "texto": "Que etapas eu devo seguir para resolver essa questão?",
                "timestamp": "2026-05-19T23:15:10.791427",
                "question_id": 2
              },
              ...
            ]
        """
    messages = getChatsMessagesByChat(chat_id)
    return messages if messages is not None else []

@router.post("/{habilidade_id}")
def createChat(habilidade_id: int, item: str = Body()):
    """
        Chama função que registra chat, dado habilidade e nome do chat. Retorna ChatSchema completo caso tenha sucesso.

        Ex de uso: POST http://127.0.0.1:8000/chat/2 (o nome é passada em json, como {"nome do chat"}
    """
    chat = createChatInDB(4, habilidade_id, item) #sempre cria no user 4 por enquanto
    if not chat:
        raise HTTPException(status_code=404, detail="Erro ao criar chat")
    return chat

@router.post("/update/{chat_id}")
def updateChatName(chat_id: int, chat_name: str = Body()):
    """
        Chama função que atualiza nome do chat, dado o id dele e o nome novo. Retorna mensagem de sucesso ou falha.

        Ex de uso: POST http://127.0.0.1:8000/chat/update/4 (o nome é passada em json, como {"nome novo!"}
    """
    chat_original = getChatByID(chat_id)
    if not chat_original:
        raise HTTPException(status_code=404, detail="Erro ao atualizar chat")
    chat = ChatSchema(id = chat_id, user_id=chat_original.user_id, habilidade=chat_original.habilidade, chat_name=chat_name, status=chat_original.status, criado_em=chat_original.criado_em, atualizado_em=chat_original.atualizado_em)
    chat_final = updateChat(chat)
    if not chat_final:
        raise HTTPException(status_code=404, detail="Erro ao atualizar chat")
    return {"message": "Chat atualizado com sucesso!"}

@router.post("/status/{chat_id}")
def updateChatStatus(chat_id: int, status: int = Body(..., embed=True)):
    """
        Atualiza o status de um chat (0 ou 1), dado o id dele.

        Ex de uso: PATCH http://127.0.0.1:8000/chat/status/4 body: {"status": 0}
    """
    if status not in (0, 1):
        raise HTTPException(status_code=400, detail="Status deve ser 0 ou 1")
    
    chat_original = getChatByID(chat_id)
    if not chat_original:
        raise HTTPException(status_code=404, detail="Chat não encontrado")
    
    chat = ChatSchema(
        id=chat_id,
        user_id=chat_original.user_id,
        habilidade=chat_original.habilidade,
        chat_name=chat_original.chat_name,
        status=status,
        criado_em=chat_original.criado_em,
        atualizado_em=chat_original.atualizado_em,
    )
    chat_final = updateChat(chat)
    if not chat_final:
        raise HTTPException(status_code=500, detail="Erro ao atualizar status do chat")
    
    return {"message": f"Status do chat {chat_id} atualizado para {status}"}

@router.delete("/{chat_id}")
def deleteChat(chat_id: int):
    """
        Chama função que remove o chat do banco de dados, retorna mensagem de sucesso caso tenha sido apagado.

        Ex de uso: DELETE http://127.0.0.1:8000/chat/5

        Retorno: {"message":"Chat 2 apagado com sucesso"}
    """
    apagado = deleteChatInDB(chat_id)
    if not apagado:
        raise HTTPException(status_code=404, detail="Nenhum chat com esse id foi achado")
    return {"message":f"Chat {chat_id} apagado com sucesso"}

@router.put("/prompt/{chat_id}/{question_id}")
def promptAI(chat_id: int, question_id: int, texto: str = Body(..., embed=True), status: int = Body(..., embed=True)):
    """
        Chama função que manda prompt no chat, requer id do chat, da questão e texto. Retorna a lista atualizada de ChatMessageSchemas desse chat caso tenha sucesso.

        Ex de uso: PUT http://127.0.0.1:8000/chat/prompt/4/34 body: {"texto": "Olá"}

        Retorno: {"mensagens": [ChatMessageSchema1, ChatMessageSchema2, ...]}
    """
    resposta = getAnswertheQuery(chat_id, question_id, texto, status)
    if not resposta:
        raise HTTPException(status_code=500, detail="Algum problema ocorreu ao processar o prompt")
    createChatMessage(chat_id, "user", texto, question_id)
    createChatMessage(chat_id, "llm", resposta, question_id)
    chat_messages = getChatsMessagesByChat(chat_id)
    return chat_messages if chat_messages is not None else []

@router.put("/prompt/{chat_id}/red/{essay_id}")
def promptAIred(chat_id: int, essay_id: int, texto: str = Body(..., embed=True)):
    """
        Chama função que manda prompt no chat, requer id do chat, da redacao e texto. Retorna a lista atualizada de ChatMessageSchemas desse chat caso tenha sucesso.

        Ex de uso: PUT http://127.0.0.1:8000/chat/prompt/4/34/red/12 body: {"texto": "Olá"}

        Retorno: {"mensagens": [ChatMessageSchema1, ChatMessageSchema2, ...]}
    """
    resposta = getAnswertheQueryEssay(chat_id, essay_id, texto)
    print(resposta)
    if not resposta:
        raise HTTPException(status_code=500, detail="Algum problema ocorreu ao processar o prompt")
    createChatMessage(chat_id, "user", texto, essay_id=essay_id)
    createChatMessage(chat_id, "llm", resposta, essay_id=essay_id)
    chat_messages = getChatsMessagesByChat(chat_id)
    return chat_messages if chat_messages is not None else []