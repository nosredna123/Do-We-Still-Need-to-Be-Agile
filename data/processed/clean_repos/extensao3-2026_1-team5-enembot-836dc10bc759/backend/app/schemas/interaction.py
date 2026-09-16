from pydantic import BaseModel, Field

class InteractionSchema(BaseModel):
    id: int
    user_id: int
    question_id: int
    tempo_gasto: int
    resposta_user: str
    acertou: bool
    n_dicas: int
