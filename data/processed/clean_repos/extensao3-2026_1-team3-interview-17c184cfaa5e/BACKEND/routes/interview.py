from datetime import datetime
 
from fastapi import APIRouter, HTTPException
 
from database import analyses_collection
from models import InterviewQuestionsRequest, InterviewQuestionsResult
from services.llm import generate_interview_questions
 
router = APIRouter()
 
 
@router.post("/interview-questions", response_model=InterviewQuestionsResult)
async def get_interview_questions(request: InterviewQuestionsRequest):
 
    try:
        perguntas = await generate_interview_questions(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
 
    # Salva no MongoDB (opcional — não trava se banco estiver desativado)
    if analyses_collection is not None:
        try:
            await analyses_collection.insert_one({
                "type": "interview_questions",
                "titulo_vaga": request.titulo_vaga,
                "perguntas": perguntas,
                "model_used": "llama-3.3-70b-versatile (groq)",
                "created_at": datetime.utcnow(),
            })
        except Exception as e:
            print(f"[MongoDB] Falha ao salvar perguntas (não crítico): {e}")
 
    return InterviewQuestionsResult(
        titulo_vaga=request.titulo_vaga,
        total_perguntas=len(perguntas),
        perguntas=perguntas,
    )
 