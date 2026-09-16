"""
Router para endpoints relacionados a medicamentos e bulas.

Endpoints:
- POST /api/meds/simplify: Simplifica a bula de um medicamento usando RAG
- GET /api/meds/search: Busca informações sobre um medicamento
"""

from fastapi import APIRouter, HTTPException, Depends
from app.schemas.medication_schema import (
    MedicationSimplifyRequest,
    MedicationSimplifyResponse,
    MedicationSearchRequest,
    MedicationSearchResponse
)
from app.services.rag_service import RAGService
from app.core.dependencies import get_chroma_dependency
from app.core.logger import setup_logger

logger = setup_logger()
router = APIRouter()


@router.post("/simplify", response_model=MedicationSimplifyResponse)
async def simplify_medication(
    request: MedicationSimplifyRequest,
    chroma_client=Depends(get_chroma_dependency)
):
    """
    Simplifica a bula de um medicamento.
    
    Fluxo:
    1. Busca a bula no ChromaDB (vetorizado)
    2. Se não encontrar, busca na web via scraper_service
    3. Usa RAG (LangChain + Gemini) para simplificar o texto
    4. Retorna a versão simplificada
    
    Args:
        request: Dados do medicamento (nome)
        chroma_client: Cliente ChromaDB (injetado)
        
    Returns:
        Texto simplificado da bula
    """
    try:
        logger.info(f"Simplificando bula para: {request.medication_name}")
        
        # Inicializar serviço RAG
        rag_service = RAGService(chroma_client=chroma_client)
        
        # Simplificar bula
        simplified_text = await rag_service.simplify_medication_info(
            medication_name=request.medication_name
        )
        
        return MedicationSimplifyResponse(
            medication_name=request.medication_name,
            simplified_text=simplified_text,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Erro ao simplificar bula: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar bula: {str(e)}"
        )


@router.get("/search", response_model=MedicationSearchResponse)
async def search_medication(
    medication_name: str,
    chroma_client=Depends(get_chroma_dependency)
):
    """
    Busca informações sobre um medicamento.
    
    Args:
        medication_name: Nome do medicamento
        chroma_client: Cliente ChromaDB (injetado)
        
    Returns:
        Informações encontradas sobre o medicamento
    """
    try:
        logger.info(f"Buscando informações para: {medication_name}")
        
        # TODO: Implementar busca no ChromaDB
        # Por enquanto, retorna placeholder
        return MedicationSearchResponse(
            medication_name=medication_name,
            found=False,
            message="Busca ainda não implementada"
        )
        
    except Exception as e:
        logger.error(f"Erro na busca: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro na busca: {str(e)}"
        )

