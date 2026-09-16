"""
Schemas para endpoints de medicamentos.

Define os modelos Pydantic para validação de requisições
e respostas relacionadas a medicamentos e bulas.
"""

from pydantic import BaseModel, Field
from typing import Optional


class MedicationSimplifyRequest(BaseModel):
    """Schema para requisição de simplificação de bula."""
    medication_name: str = Field(..., description="Nome do medicamento", example="Paracetamol")


class MedicationSimplifyResponse(BaseModel):
    """Schema para resposta de simplificação de bula."""
    medication_name: str
    simplified_text: str
    success: bool
    source: Optional[str] = Field(None, description="Origem da bula (chromadb, web, etc.)")


class MedicationSearchRequest(BaseModel):
    """Schema para requisição de busca de medicamento."""
    medication_name: str = Field(..., description="Nome do medicamento")


class MedicationSearchResponse(BaseModel):
    """Schema para resposta de busca de medicamento."""
    medication_name: str
    found: bool
    message: str
    details: Optional[dict] = None

