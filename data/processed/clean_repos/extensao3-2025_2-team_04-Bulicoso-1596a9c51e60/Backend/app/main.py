import os
import pickle
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

# LangChain & Google
from langchain_google_genai import ChatGoogleGenerativeAI
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow  # <--- [IMPORTANTE] Para o fluxo Web

# NOSSOS MÓDULOS
from google_calendar_auth import get_calendar_service
from modules.rag_manager import RAGManager
from modules.intent_classifier import classify_intent, IntentResponse
import modules.calendar_manager as calendar

# Carregar .env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path, override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY não encontrada no .env!")

# CONFIGURAÇÕES DO OAUTH (AJUSTE A PORTA DO FRONTEND AQUI SE NECESSÁRIO)
# Se seu React roda na 3000, mude para 3000. Se for 5173 (Vite), mantenha.
FRONTEND_URL = "http://localhost:5173/chat"
BACKEND_REDIRECT_URI = "http://127.0.0.1:8000/auth/callback"
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'

# Estado global da aplicação
app_state: Dict[str, Any] = {}


# --- Gerenciamento do Ciclo de Vida ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("--- 🚀 Iniciando API ---")

    # 1. Carregar LLM
    print("[INIT] Carregando LLM principal (Gemini Flash)...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.5,
        google_api_key=GOOGLE_API_KEY
    )
    app_state["llm"] = llm

    # 2. RAG Manager
    print("[INIT] Carregando RAG Manager...")
    app_state["rag_manager"] = RAGManager(google_api_key=GOOGLE_API_KEY)

    # 3. Calendar Service
    # Tenta carregar se já existir token salvo, senão inicia como None
    print("[INIT] Verificando autenticação do Calendar...")
    if os.path.exists('token.pickle'):
        try:
            app_state["calendar_service"] = get_calendar_service()  # Tenta carregar do pickle existente
            print("✅ Calendar autenticado via token salvo.")
        except:
            app_state["calendar_service"] = None
            print("⚠️ Token inválido ou expirado. Login necessário.")
    else:
        app_state["calendar_service"] = None
        print("⚠️ Nenhum token encontrado. Login necessário.")

    yield
    print("--- 🛑 Encerrando API ---")
    app_state.clear()


# --- Dependências ---
def get_llm():
    return app_state["llm"]


def get_rag_manager():
    return app_state["rag_manager"]


def get_calendar_service_dep():
    # Se não estiver logado, lança erro para o front saber
    if not app_state.get("calendar_service"):
        raise HTTPException(status_code=401, detail="Google Calendar não autenticado. Faça login em /auth/login")
    return app_state["calendar_service"]


app = FastAPI(
    title="Assistente de Medicação API",
    description="API modular com RAG e Google Calendar.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Modelos Pydantic ---
class RagQueryRequest(BaseModel):
    original_query: str
    topic: str


class ChatQuery(BaseModel):
    query: str


class ScheduleRequest(BaseModel):
    instrucao: str
    start_time_str: str


class DeleteRequest(BaseModel):
    event_ids: List[str]


class EditRequest(BaseModel):
    new_start_time_str: str


# === ENDPOINTS DE NEGÓCIO (Mantidos iguais) ===

@app.post("/v1/chat/classify_intent")
async def handle_chat_query(query: ChatQuery, llm: ChatGoogleGenerativeAI = Depends(get_llm)):
    return classify_intent(query.query, llm)


@app.post("/v1/rag/query")
async def post_rag_query(request: RagQueryRequest, rag_manager: RAGManager = Depends(get_rag_manager)):
    result = rag_manager.query(request.original_query, request.topic)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@app.post("/v1/calendar/schedule")
async def schedule_treatment(request: ScheduleRequest, llm=Depends(get_llm), service=Depends(get_calendar_service_dep)):
    details = calendar.parse_instruction(request.instrucao, llm)
    if not details: raise HTTPException(status_code=400, detail="Erro no parse.")

    start_time = calendar.get_start_time_from_string(request.start_time_str)
    if not start_time: raise HTTPException(status_code=400, detail="Data inválida.")

    try:
        return calendar.create_calendar_events(service, details, start_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/calendar/events/{medicamento_nome}")
async def get_future_events(medicamento_nome: str, service=Depends(get_calendar_service_dep)):
    events = calendar.find_future_events_by_name(service, medicamento_nome)
    return {"medicamento": medicamento_nome, "events": events}


@app.post("/v1/calendar/delete")
async def delete_calendar_events(request: DeleteRequest, service=Depends(get_calendar_service_dep)):
    return calendar.delete_events(service, request.event_ids)


@app.put("/v1/calendar/edit/{event_id}")
async def edit_calendar_event(event_id: str, request: EditRequest, service=Depends(get_calendar_service_dep)):
    return calendar.edit_single_event(service, event_id, request.new_start_time_str)


# === NOVO FLUXO DE AUTENTICAÇÃO WEB ===

@app.get("/auth/login", summary="1. Iniciar Login (Redireciona para Google)")
async def login_google():
    """
    Gera a URL de autorização do Google e redireciona o navegador do usuário.
    """
    # Se token existe, apaga para forçar novo login (opcional, mas bom para garantir)
    if os.path.exists("token.pickle"):
        os.remove("token.pickle")

    # Configura o fluxo OAuth
    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE,
        scopes=SCOPES,
        redirect_uri=BACKEND_REDIRECT_URI
    )

    # Gera URL (offline access = refresh token)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    print(f"[AUTH] Redirecionando usuário para: {authorization_url}")
    # Retorna um 307 Redirect para o Frontend seguir automaticamente
    return RedirectResponse(authorization_url)


@app.get("/auth/callback", summary="2. Callback do Google")
async def auth_callback(request: Request):
    """
    O Google redireciona para cá com um código (?code=...).
    Trocamos o código pelo token, salvamos e mandamos para o Chat.
    """
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Código de autenticação não encontrado.")

    try:
        # Troca o código pelo token
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE,
            scopes=SCOPES,
            redirect_uri=BACKEND_REDIRECT_URI
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Salva o token.pickle (compatível com seu código antigo)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

        print("[AUTH] Token salvo com sucesso em token.pickle")

        # Atualiza o serviço na memória da API
        app_state["calendar_service"] = build('calendar', 'v3', credentials=creds)

        # REDIRECIONA O USUÁRIO DE VOLTA PARA O FRONTEND (PÁGINA DE CHAT)
        print(f"[AUTH] Login concluído. Redirecionando para {FRONTEND_URL}")
        return RedirectResponse(FRONTEND_URL)

    except Exception as e:
        print(f"[AUTH ERROR] {e}")
        raise HTTPException(status_code=500, detail="Falha na autenticação com Google.")


@app.post("/auth/logout")
async def logout_google():
    app_state["calendar_service"] = None
    if os.path.exists("token.pickle"):
        os.remove("token.pickle")
    return {"message": "Deslogado com sucesso."}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)