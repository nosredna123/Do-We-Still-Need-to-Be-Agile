from dotenv import load_dotenv
from supabase import create_client, Client
import os
from app.schemas.interaction import InteractionSchema

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def getInteractionsByUser(user_id: int):
    """
    Retorna os InteractionSchemas dado o user id
    """
    response = (
        supabase.table("Interaction")
        .select("*")
        .eq("user_id", user_id)
        .execute()
    )
    rows = response.data
    if rows:
        interactions = []
        for row in rows:
            interaction = InteractionSchema(
                id=row.get('id'),
                user_id=row.get('user_id'),
                question_id=row.get('question_id'),
                tempo_gasto=row.get('tempo_gasto'),
                resposta_user=row.get('resposta_user'),
                acertou=row.get('acertou'),
                n_dicas=row.get('n_dicas')
            )
            interactions.append(interaction)
        return interactions
    else:
        return None

def createInteraction(user_id: int, question_id: int, tempo_gasto: int, resposta_user: str, acertou: bool, n_dicas: int):
    """
    Registra uma interação nova dado id de usuário, id de questão, tempo gasto (em segundos), o texto da resposta do usuário, se ele acertou e o número de dicas requisitadas.

    Retorna o InteractionSchema caso tenha tido sucesso.
    """
    response = (
        supabase.table("Interaction")
        .insert({"user_id": user_id, "question_id": question_id, "tempo_gasto": tempo_gasto, "resposta_user": resposta_user, "acertou": acertou, "n_dicas": n_dicas})
        .execute()
    )
    rows = response.data
    if rows:
        interaction = InteractionSchema(
            id=rows[0].get('id'),
            user_id=rows[0].get('user_id'),
            question_id=rows[0].get('question_id'),
            tempo_gasto=rows[0].get('tempo_gasto'),
            resposta_user=rows[0].get('resposta_user'),
            acertou=rows[0].get('acertou'),
            n_dicas=rows[0].get('n_dicas')
        )
        return interaction
    else:
        return None