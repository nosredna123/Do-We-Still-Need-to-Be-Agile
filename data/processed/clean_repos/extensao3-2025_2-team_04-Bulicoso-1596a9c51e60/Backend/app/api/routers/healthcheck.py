"""
Router para healthcheck e status da aplicação.

Endpoint simples para verificar se a API está funcionando.
"""

from fastapi import APIRouter
from app.schemas.response_schema import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint de healthcheck.
    
    Retorna o status da aplicação.
    """
    return HealthResponse(status="ok", message="Sistema operacional")

