"""
Router para endpoints relacionados a lembretes de medicação.

Endpoints:
- POST /api/reminders/create: Cria lembretes no Google Calendar
- GET /api/reminders/list: Lista lembretes criados
- DELETE /api/reminders/{reminder_id}: Remove um lembrete
"""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.reminder_schema import (
    ReminderCreateRequest,
    ReminderCreateResponse,
    ReminderListResponse
)
from app.services.google_service import GoogleCalendarService
from app.core.logger import setup_logger

logger = setup_logger()
router = APIRouter()


@router.post("/create", response_model=ReminderCreateResponse)
async def create_reminder(request: ReminderCreateRequest):
    """
    Cria lembretes de medicação no Google Calendar.
    
    Fluxo:
    1. Valida os dados do lembrete
    2. Autentica com Google Calendar API (via google_service)
    3. Cria eventos recorrentes conforme a frequência
    4. Retorna IDs dos eventos criados
    
    Args:
        request: Dados do lembrete (medicamento, dosagem, frequência, duração)
        
    Returns:
        Informações dos eventos criados
    """
    try:
        logger.info(f"Criando lembrete para: {request.medication_name}")
        
        # Inicializar serviço do Google Calendar
        google_service = GoogleCalendarService()
        
        # Criar eventos no Google Calendar
        events = await google_service.create_medication_events(
            medication_name=request.medication_name,
            dosage=request.dosage,
            frequency=request.frequency,
            duration_days=request.duration_days,
            start_date=request.start_date
        )
        
        return ReminderCreateResponse(
            success=True,
            events_created=len(events),
            event_ids=[event.get("id") for event in events],
            message=f"Lembretes criados com sucesso para {request.medication_name}"
        )
        
    except Exception as e:
        logger.error(f"Erro ao criar lembrete: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao criar lembrete: {str(e)}"
        )


@router.get("/list", response_model=ReminderListResponse)
async def list_reminders():
    """
    Lista todos os lembretes criados.
    
    Returns:
        Lista de lembretes ativos
    """
    try:
        # TODO: Implementar listagem de lembretes
        google_service = GoogleCalendarService()
        reminders = await google_service.list_medication_events()
        
        return ReminderListResponse(
            reminders=reminders,
            total=len(reminders)
        )
        
    except Exception as e:
        logger.error(f"Erro ao listar lembretes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao listar lembretes: {str(e)}"
        )


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str):
    """
    Remove um lembrete do Google Calendar.
    
    Args:
        reminder_id: ID do evento no Google Calendar
        
    Returns:
        Confirmação de remoção
    """
    try:
        logger.info(f"Removendo lembrete: {reminder_id}")
        
        google_service = GoogleCalendarService()
        await google_service.delete_event(reminder_id)
        
        return {"success": True, "message": "Lembrete removido com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao remover lembrete: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao remover lembrete: {str(e)}"
        )

