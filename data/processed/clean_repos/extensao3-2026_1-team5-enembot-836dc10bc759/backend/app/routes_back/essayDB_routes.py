from dotenv import load_dotenv
from supabase import create_client, Client
import os
import random
from app.schemas.essay import EssaySchema

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def getEssayByID(id: int):
    """
    Retorna uma redação como EssaySchema dado o seu id.
    """
    response = (
        supabase.table("Essay")
        .select("*")
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        essay = EssaySchema(
            id=rows[0].get('id'),
            theme=rows[0].get('theme'),
            text=rows[0].get('text'),
        )
        return essay
    else:
        return None

def createEssay(theme: int, text: str):
    response = (
        supabase.table("Essay")
        .insert({"theme": theme, "text": text})
        .execute()
    )

    rows = response.data

    if rows:
        essay = EssaySchema(
            id=rows[0].get('id'),
            theme=rows[0].get('theme'),
            text=rows[0].get('text')
        )

        return essay
    else:
        return None 

def updateEssay(id: int, text: str):
    """
    Atualiza o campo de texto de uma redação já criada.

    Retorna o EssaySchema atualizado em caso de sucesso, ou None se não encontrou a redação.
    """
    response = (
        supabase.table("Essay")
        .update({"text": text})
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        return EssaySchema(
            id=rows[0].get('id'),
            theme=rows[0].get('theme'),
            text=rows[0].get('text'),
        )
    return None
