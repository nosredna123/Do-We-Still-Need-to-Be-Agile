"""
Configurações e variáveis de ambiente.

Este módulo carrega e gerencia todas as configurações da aplicação
a partir de variáveis de ambiente (arquivo .env).

Variáveis necessárias:
- GOOGLE_API_KEY: Chave da API do Gemini
- GOOGLE_CLIENT_ID: ID do cliente OAuth2 do Google
- GOOGLE_CLIENT_SECRET: Secret do cliente OAuth2
- GOOGLE_REDIRECT_URI: URI de redirecionamento OAuth2
- CHROMA_DB_PATH: Caminho para o banco de dados ChromaDB
- LOG_LEVEL: Nível de log (DEBUG, INFO, WARNING, ERROR)
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configurações da aplicação carregadas do arquivo .env"""
    
    # API Keys
    GOOGLE_API_KEY: str = ""
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"
    
    # ChromaDB
    CHROMA_DB_PATH: str = "./data/chroma_db"
    CHROMA_COLLECTION_NAME: str = "medication_bulas"
    
    # LangChain / RAG
    EMBEDDING_MODEL: str = "models/embedding-001"  # Gemini embedding model
    LLM_MODEL: str = "gemini-pro"  # Modelo Gemini para geração
    
    # Configurações de texto
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # Scraping
    SCRAPER_TIMEOUT: int = 10
    SCRAPER_USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # Aplicação
    APP_NAME: str = "Sistema de Adesão Medicamentosa"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Instância global de configurações
settings = Settings()

