from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.routes_front.user_routes import router as user_router
from app.routes_front.chat_routes import router as chat_router
from app.routes_front.question_routes import router as question_router
from app.routes_front.essay_routes import router as essay_router
from app.routes_front.theme_routes import router as theme_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

@router.get("/")
def get_root():
    return {"message": "Hello World"}

app.include_router(router)
app.include_router(user_router)
app.include_router(chat_router)
app.include_router(question_router)
app.include_router(essay_router)
app.include_router(theme_router)