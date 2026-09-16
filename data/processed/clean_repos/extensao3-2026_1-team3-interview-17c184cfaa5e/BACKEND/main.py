import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv # 1. Importe o dotenv

# 2. Carregue as variáveis do arquivo .env antes de tudo
load_dotenv() 

#from database import client as mongo_client, db
from routes.analyze import router as analyze_router
from routes.improve import router as improve_router
from routes.interview import router as interview_router
from routes.jobs import router as jobs_router
from routes.related_jobs import router as related_jobs_router

app = FastAPI(title="Resume Analyzer API")

# 3. Pega a variável do .env. Se ela não existir, usa "*" como padrão de segurança.
origins_env = os.getenv("ORIGINS", "*")

# 4. Transforma a string do .env em uma lista do Python (FastAPI exige lista)
# Se no .env estiver: ORIGINS=http://localhost:3000,http://localhost:8000
# Ele transforma em: ["http://localhost:3000", "http://localhost:8000"]
origins = [origin.strip() for origin in origins_env.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Agora é garantido que isso é uma lista
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router, prefix="/api/v1/jobs")
app.include_router(analyze_router, prefix="/api/v1")
app.include_router(interview_router, prefix="/api/v1")
app.include_router(improve_router, prefix="/api/v1")
app.include_router(related_jobs_router, prefix="/api/v1")

'''
@app.get("/health")
async def health():
    try:
        await db.command("ping")
        db_status = "ok"
    except Exception:
        db_status = "error"
    return {"status": "ok", "database": db_status}


@app.on_event("shutdown")
async def shutdown():
    mongo_client.close()'''