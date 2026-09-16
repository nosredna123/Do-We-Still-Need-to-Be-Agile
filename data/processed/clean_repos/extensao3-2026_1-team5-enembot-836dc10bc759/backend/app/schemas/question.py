from pydantic import BaseModel, Field
from typing import List
from app.schemas.alternativa import AlternativaSchema
from typing import Optional

class QuestionSchema(BaseModel):
    id: int
    habilidade: int
    competencia: int
    enunciado: str = Field(max_length=15000)
    alternativas: List[AlternativaSchema]
    resposta_correta: str
    image: Optional[str] = None
    dificuldade: int