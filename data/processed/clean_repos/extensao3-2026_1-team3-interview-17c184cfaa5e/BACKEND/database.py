from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

MONGO_URL = os.getenv("MONGO_URL", "")
DB_NAME   = os.getenv("DB_NAME", "interview_prep_ai")

# Conexão opcional — não trava o servidor se MONGO_URL estiver vazia
if MONGO_URL:
    client = AsyncIOMotorClient(MONGO_URL)
    db     = client[DB_NAME]
else:
    print("[MongoDB] MONGO_URL não configurada — banco desativado")
    client = None
    db     = None

jobs_collection     = db["jobs"]     if db is not None else None
resumes_collection  = db["resumes"]   if db is not None else None
analyses_collection = db["analyses"]  if db is not None else None