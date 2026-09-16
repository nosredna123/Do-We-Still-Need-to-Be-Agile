"""
Schemas para endpoints de lembretes.

Define os modelos Pydantic para validação de requisições
e respostas relacionadas a lembretes de medicação.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class ReminderCreateRequest(BaseModel):
    """Schema para requisição de criação de lembrete."""
    medication_name: str = Field(..., description="Nome do medicamento", example="Paracetamol")
    dosage: str = Field(..., description="Dosagem", example="500mg")
    frequency: str = Field(..., description="Frequência", example="a cada 8 horas")
    duration_days: int = Field(..., description="Duração do tratamento em dias", example=7)
    start_date: Optional[datetime] = Field(None, description="Data de início (padrão: hoje)")


class ReminderCreateResponse(BaseModel):
    """Schema para resposta de criação de lembrete."""
    success: bool
    events_created: int
    event_ids: List[str]
    message: str


class ReminderItem(BaseModel):
    """Schema para item de lembrete."""
    id: str
    medication_name: str
    dosage: str
    frequency: str
    start_date: datetime
    end_date: Optional[datetime] = None


class ReminderListResponse(BaseModel):
    """Schema para resposta de listagem de lembretes."""
    reminders: List[ReminderItem]
    total: int

