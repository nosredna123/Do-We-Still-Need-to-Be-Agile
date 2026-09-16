from datetime import datetime

from fastapi import APIRouter, HTTPException

from database import analyses_collection
from models import ImproveRequest, ResumeImprovementResult
from services.agent import tool_improve_resume

router = APIRouter()


@router.post("/improve", response_model=ResumeImprovementResult)
async def improve_resume(request: ImproveRequest):
    try:
        result = await tool_improve_resume(request.resume_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

    try:
        await analyses_collection.insert_one({
            "tipo": "melhoria_curriculo",
            "resultado": result,
            "modelo_usado": "llama3.2 (agente)",
            "created_at": datetime.utcnow(),
        })
    except Exception as e:
        print(f"[MongoDB] Falha ao salvar melhoria (não crítico): {e}")

    return ResumeImprovementResult(**result)
