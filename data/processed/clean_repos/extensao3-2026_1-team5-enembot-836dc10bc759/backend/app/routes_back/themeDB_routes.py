from app.schemas.theme import ThemeSchema
from dotenv import load_dotenv
from supabase import create_client, Client
import os
import random

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def getThemeById(id: int):
    """
    Retorna o nome de um tema dado o seu id.
    """
    response = (
        supabase.table("Theme")
        .select("*")
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        theme = ThemeSchema(
            id=rows[0].get('id'),
            name=rows[0].get('name')
        )
        return theme
    else:
        return None    

def getRandomTheme(exclude_ids: list[int] | None = None):
    """
    Escolhe aleatoriamente um tema para o usuário fazer a redação.
    """
    response = (
        supabase.table("Theme")
        .select("id")
        .execute()
    )
    rows = response.data or []
    excluded = set(exclude_ids or [])
    ids = [row["id"] for row in rows if row.get("id") is not None and row["id"] not in excluded]
    if not ids:
        return None
    return getThemeById(random.choice(ids))


# def getUnsolvedTheme(user_id: int, habilidade: str, competencia: str):
#     """
#     Usar como modelo getUnsolvedQuestion
#     
#     """