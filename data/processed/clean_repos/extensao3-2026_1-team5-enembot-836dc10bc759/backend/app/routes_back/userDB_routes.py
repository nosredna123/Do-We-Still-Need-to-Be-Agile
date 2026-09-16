from dotenv import load_dotenv
from supabase import create_client, Client
import os
from app.schemas.user import UserSchema

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def getUserByID(id: int):
    """
    Retorna um usuário no formato UserSchema dado o seu id.
    """
    response = (
        supabase.table("User")
        .select("*")
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        user = UserSchema(
            id=rows[0].get('id'),
            username=rows[0].get('username'),
            email=rows[0].get('email'),
            password=rows[0].get('password')
        )
        return user
    else:
        return None

def createUser(username: str, email: str, password: str):
    """
    Cria um usuário novo dado o username, e-mail e senha.

    Retorna UserSchema do usuário novo caso tenha sido criado com sucesso.
    """
    response = (
        supabase.table("User")
        .insert({"username": username, "email": email, "password": password})
        .execute()
    )
    rows = response.data
    if rows:
        user = UserSchema(
            id=rows[0].get('id'),
            username=rows[0].get('username'),
            email=rows[0].get('email'),
            password=rows[0].get('password')
        )
        return user
    else:
        return None

def updateUser(user: UserSchema):
    """
    Atualiza um usuário no banco de dados dado um UserSchema do usuário modificado.

    Retorna o mesmo UserSchema caso tenha sido modificado com sucesso.
    """
    response = (
        supabase.table("User")
        .update({"username": user.username, "email": user.email, "password": user.password})
        .eq("id", user.id)
        .execute()
    )
    rows = response.data
    if rows:
        return user
    else:
        return None

def deleteUser(id: int):
    """
    Recebe um id de usuário e apaga o usuário, retornando True ou False dependendo do sucesso.
    """
    response = (
        supabase.table("User")
        .delete()
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        return True
    else:
        return False