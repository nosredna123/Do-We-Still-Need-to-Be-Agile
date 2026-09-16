from app.routes_back.essayDB_routes import getEssayByID, createEssay, updateEssay as updateEssayInDB
from fastapi import APIRouter, HTTPException, Body


router = APIRouter(prefix="/essays", tags=["essays"])

@router.get("/{id}")
def retrieveEssayByID(id: int):
    """
        Retorna um tema de redação.

        Ex de uso: GET http://127.0.0.1:8000/chat/themes/1
    """
    essay = getEssayByID(id)
    if not essay:
        raise HTTPException(status_code=500, detail="Não existe redação com esse id")
    return essay

@router.put("/{id}")
def updateEssayText(id: int, text: str = Body()):
    """
        Atualiza o texto de uma redação existente.

        Ex de uso: PUT http://127.0.0.1:8000/essays/3/Texto da redação do aluno
    """
    essay = updateEssayInDB(id, text)
    if not essay:
        raise HTTPException(status_code=404, detail="Redação não encontrada")
    return essay