from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from apscheduler.schedulers.background import BackgroundScheduler
from src.db.database.connection import SessionLocal
from src.services.recurrence_service import RecurrenceService
from src.core.logger import logger

from .api.v1.api import api_router

scheduler = BackgroundScheduler()

def run_recurrence_check():
    """Wrapper to run the service in a fresh session."""
    db = SessionLocal()
    try:
        service = RecurrenceService(db)
        service.process_daily_recurrences()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Application & Scheduler...")
    scheduler.add_job(run_recurrence_check, 'interval', hours=24)
    scheduler.start()
    run_recurrence_check()
    yield
    logger.info("Shutting down Scheduler...")
    scheduler.shutdown()

app = FastAPI(title="SofIA Backend", lifespan=lifespan)

origins = ["http://localhost", "http://localhost:5173", "http://localhost:3000", "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}

app.include_router(api_router, prefix="/api/v1")
add_pagination(app)