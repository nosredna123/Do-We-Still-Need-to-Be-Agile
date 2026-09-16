from datetime import datetime

from fastapi import APIRouter, HTTPException

from database import analyses_collection
from models import RelatedJob, RelatedJobsRequest, RelatedJobsResult
from services.search import search_related_jobs

router = APIRouter()


@router.post("/related-jobs", response_model=RelatedJobsResult)
async def get_related_jobs(request: RelatedJobsRequest):
    try:
        results = await search_related_jobs(
            request.titulo_vaga,
            request.habilidades_vaga,
            limit=5,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Falha na busca: {e}")

    vagas = [RelatedJob(**r) for r in results]

    try:
        await analyses_collection.insert_one({
            "type": "related_jobs",
            "titulo_vaga": request.titulo_vaga,
            "total": len(vagas),
            "vagas": [v.model_dump() for v in vagas],
            "created_at": datetime.utcnow(),
        })
    except Exception as e:
        print(f"[MongoDB] Falha ao salvar related_jobs (não crítico): {e}")

    return RelatedJobsResult(
        titulo_vaga=request.titulo_vaga,
        total=len(vagas),
        vagas=vagas,
    )
