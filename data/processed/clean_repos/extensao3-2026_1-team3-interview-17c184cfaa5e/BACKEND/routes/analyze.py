from datetime import datetime
 
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
 
from database import analyses_collection
from models import AnalysisResult
from services.pdf import extract_text_from_pdf
from services.agent import run_agent, run_agent_from_text
 
router = APIRouter()
 
_MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB
 
 
# ─── Rota principal: descrição textual da vaga ────────────────────────────────
 
@router.post("/analyze", response_model=AnalysisResult)
async def analyze_resume(
    job_description: str = Form(..., description="Descrição textual da vaga"),
    resume_pdf: UploadFile = File(..., description="Currículo em PDF"),
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="job_description não pode ser vazio")
 
    if resume_pdf.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="resume_pdf deve ser um PDF")
 
    if resume_pdf.size and resume_pdf.size > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="resume_pdf muito grande (máx 20 MB)")
 
    pdf_bytes = await resume_pdf.read()
 
    try:
        resume_text = await extract_text_from_pdf(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
 
    try:
        # run_agent_from_text: recebe texto da vaga direto, sem imagem
        result = await run_agent_from_text(job_description, resume_text)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

 
    return AnalysisResult(**result)
 