from dotenv import load_dotenv
from supabase import create_client, Client
import os

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def getHabilidadeByID(id: int):
    """Recebe o id da habilidade e retorna o seu nome."""
    response = (
        supabase.table("Habilidade")
        .select("*")
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        nome = rows[0].get('nome')
        return nome
    else:
        return None

def getCompetenciaByID(id_comp: int, id_habil: int):
    """
    Recebe o id da competência e o id da habilidade a qual ela pertence e retorna uma descrição da competência.

    Ex: o id_comp 1 (H1, na terminologia do INEP) com o id_habil 1 (Linguagens) retornarão a descrição oficial da competência H1 de linguagens.
    """
    response = (
        supabase.table("Competencia")
        .select("*")
        .eq("id", id_comp)
        .eq("id_habilidade", id_habil)
        .execute()
    )
    rows = response.data
    if rows:
        nome = rows[0].get('descricao')
        return nome
    else:
        return None