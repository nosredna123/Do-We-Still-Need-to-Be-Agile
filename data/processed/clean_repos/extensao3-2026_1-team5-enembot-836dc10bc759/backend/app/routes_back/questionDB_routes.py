from dotenv import load_dotenv
from supabase import create_client, Client
import os
import random
from app.schemas.question import QuestionSchema
from app.schemas.alternativa import AlternativaSchema

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def getQuestionByID(id: int):
    """
    Retorna uma questão como QuestionSchema dado o seu id.
    """
    response = (
        supabase.table("Question")
        .select("*")
        .eq("id", id)
        .execute()
    )
    rows = response.data
    if rows:
        image = rows[0].get('image')
        if image is None:
            image = ""

        alternativas = (rows[0].get('alternativas'))
        alternativas_em_schemas = [
            AlternativaSchema(letra="A", texto=str(alternativas["A"])),
            AlternativaSchema(letra="B", texto=str(alternativas["B"])),
            AlternativaSchema(letra="C", texto=str(alternativas["C"])),
            AlternativaSchema(letra="D", texto=str(alternativas["D"])),
            AlternativaSchema(letra="E", texto=str(alternativas["E"]))
        ]

        question = QuestionSchema(
            id=rows[0].get('id'),
            habilidade=rows[0].get('habilidade'),
            competencia=rows[0].get('competencia'),
            enunciado=rows[0].get('enunciado'),
            image=image,
            alternativas=alternativas_em_schemas,
            resposta_correta=rows[0].get('resposta_correta'),
            dificuldade=rows[0].get('dificuldade')
        )
        return question
    else:
        return None

def getRandomQuestionByHabilidade(habilidade_id: int, exclude_ids: list[int] | None = None):
    """
    Escolhe aleatoriamente uma questão da habilidade do chat.
    """
    response = (
        supabase.table("Question")
        .select("id")
        .eq("habilidade", habilidade_id)
        .execute()
    )
    rows = response.data or []
    excluded = set(exclude_ids or [])
    ids = [row["id"] for row in rows if row.get("id") is not None and row["id"] not in excluded]
    if not ids:
        return None
    return getQuestionByID(random.choice(ids))

def getUnsolvedQuestion(user_id: int, habilidade: str, competencia: str):
    """
    Retorna a primeira questão (QuestionSchema) de uma habilidade e competência específica
    que o usuário ainda não resolveu (não está na tabela Interaction).
    """
    # 1. Buscar os IDs de todas as questões que ESTE usuário já interagiu
    solved_responses = (
        supabase.table("Interaction")
        .select("question_id")
        .eq("user_id", user_id)
        .execute()
    )
    
    # Extrai os IDs em uma lista simples de inteiros
    solved_ids = [item["question_id"] for item in solved_responses.data if item.get("question_id")]

    # 2. Montar a query para buscar a nova questão
    query = (
        supabase.table("Question")
        .select("*")
        .eq("habilidade", habilidade)
        .eq("competencia", competencia)
    )
    
    # Se o usuário já resolveu alguma questão, filtramos para EXCLUIR esses IDs
    if solved_ids:
        query = query.not_.in_("id", solved_ids)
        
    # Executa a busca limitando a apenas 1 resultado (a "primeira" questão)
    response = query.limit(1).execute()
    rows = response.data

    # 3. Mapeamento para o QuestionSchema (idêntico ao seu método original)
    if rows:
        image = rows[0].get('image')
        if image is None:
            image = ""

        alternativas = rows[0].get('alternativas')
        alternativas_em_schemas = [
            AlternativaSchema(letra="A", texto=str(alternativas["A"])),
            AlternativaSchema(letra="B", texto=str(alternativas["B"])),
            AlternativaSchema(letra="C", texto=str(alternativas["C"])),
            AlternativaSchema(letra="D", texto=str(alternativas["D"])),
            AlternativaSchema(letra="E", texto=str(alternativas["E"]))
        ]

        question = QuestionSchema(
            id=rows[0].get('id'),
            habilidade=rows[0].get('habilidade'),
            competencia=rows[0].get('competencia'),
            enunciado=rows[0].get('enunciado'),
            image=image,
            alternativas=alternativas_em_schemas,
            dificuldade=rows[0].get('dificuldade')
        )
        return question
    else:
        return None