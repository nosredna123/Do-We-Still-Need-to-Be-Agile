"""
Schemas genéricos para respostas da API.

Define modelos comuns de resposta e tratamento de erros.
"""

from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    """Schema para resposta de healthcheck."""
    status: str
    message: str = "Sistema operacional"


class ErrorResponse(BaseModel):
    """Schema para respostas de erro."""
    error: bool = True
    message: str
    details: Optional[str] = None

