from dotenv import load_dotenv
from supabase import create_client, Client
import os
from app.schemas.chat import ChatSchema

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def getChatByID(id: int):
    """
    Retorna um chat no formato ChatSchema dado o seu id.
    """
    response = (
        supabase.table("Chat")
        .select("*")
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        chat = ChatSchema(
            id=rows[0].get('id'),
            user_id=rows[0].get('user_id'),
            habilidade=rows[0].get('habilidade'),
            chat_name=rows[0].get('chat_name'),
            status=rows[0].get('status'), 
            criado_em=rows[0].get('criado_em'),
            atualizado_em=rows[0].get('atualizado_em'),
        )
        return chat
    else:
        return None

def getChatsByUser(user_id: int):
    """
    Retorna todos os chats de um usuário em formato ChatSchema, dado o user_id.
    """
    response = (
        supabase.table("Chat")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    rows = response.data
    if rows:
        chats = []
        for row in rows:
            chat = ChatSchema(
                id=row.get('id'),
                user_id=row.get('user_id'),
                habilidade=row.get('habilidade'),
                chat_name=row.get('chat_name'),
                status=row.get('status'),
                criado_em=row.get('criado_em'),
                atualizado_em=row.get('atualizado_em'),
            )
            chats.append(chat)
        return chats
    else:
        return None

def createChat(user_id: int, habilidade: int, chat_name: str):
    """
    Cria um chat novo dado o id de usuário, habilidade e nome do chat

    Retorna um chat no formato ChatSchema se obteve sucesso.
    """
    response = (
        supabase.table("Chat")
        .insert({"user_id": user_id, "habilidade": habilidade, "chat_name": chat_name})
        .execute()
    )
    rows = response.data
    if rows:
        chat = ChatSchema(
            id=rows[0].get('id'),
            user_id=rows[0].get('user_id'),
            habilidade=rows[0].get('habilidade'),
            chat_name=rows[0].get('chat_name'),
            status=rows[0].get('status'),
            criado_em=str(rows[0].get('criado_em')),
            atualizado_em=str(rows[0].get('atualizado_em')),
        )
        return chat
    else:
        return None

def updateChat(chat: ChatSchema):
    """
    Atualiza um chat no banco de dados dado um ChatSchema do chat modificado.

    Retorna o mesmo ChatSchema caso tenha sido modificado com sucesso.
    """
    response = (
        supabase.table("Chat")
        .update({"user_id": chat.user_id, "habilidade": chat.habilidade, "chat_name": chat.chat_name, "status": chat.status, "criado_em": chat.criado_em, "atualizado_em": chat.atualizado_em})
        .eq("id", chat.id)
        .execute()
    )
    rows = response.data
    if rows:
        return chat
    else:
        return None

def deleteChat(id: int):
    """
    Recebe um id de chat e apaga o chat, retornando True ou False dependendo do sucesso.
    """
    response = (
        supabase.table("Chat")
        .delete()
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        return True
    else:
        return False