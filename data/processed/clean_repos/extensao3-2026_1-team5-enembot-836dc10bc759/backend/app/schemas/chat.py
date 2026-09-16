from pydantic import BaseModel, Field

class ChatSchema(BaseModel):
    id: int
    user_id: int
    habilidade: int
    chat_name: str = Field(max_length=200)
    criado_em: str
    atualizado_em: str
    status: int