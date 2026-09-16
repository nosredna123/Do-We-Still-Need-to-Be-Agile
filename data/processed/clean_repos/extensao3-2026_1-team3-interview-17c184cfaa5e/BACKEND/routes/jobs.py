from fastapi import APIRouter, HTTPException
from bson import ObjectId
from models import JobPosting
from database import jobs_collection

router = APIRouter()

@router.post("/")
async def create_job(job: JobPosting):
    result = await jobs_collection.insert_one(job.model_dump())
    return {"id": str(result.inserted_id), "message": "Vaga criada com sucesso"}

@router.get("/")
async def list_jobs():
    jobs = []
    async for job in jobs_collection.find():
        job["_id"] = str(job["_id"])
        jobs.append(job)
    return jobs