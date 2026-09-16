"""
🔹 CLIENTE CHROMADB - Instância e conexão com ChromaDB

Este módulo gerencia a conexão com o ChromaDB, que armazena
os embeddings das bulas de medicamentos para busca semântica.

IMPLEMENTAÇÃO NECESSÁRIA:
- Criar instância persistente do ChromaDB
- Configurar diretório de persistência
- Retornar cliente reutilizável
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger()

# Cliente global (singleton)
_chroma_client = None


def get_chroma_client() -> chromadb.Client:
    """
    🔹 IMPLEMENTAR: Retorna instância do cliente ChromaDB (singleton).
    
    Cria ou retorna a instância existente do ChromaDB, garantindo
    que apenas uma conexão seja mantida.
    
    Returns:
        Cliente ChromaDB configurado
    """
    global _chroma_client
    
    if _chroma_client is None:
        try:
            # Criar diretório se não existir
            db_path = Path(settings.CHROMA_DB_PATH)
            db_path.mkdir(parents=True, exist_ok=True)
            
            # TODO: Inicializar cliente ChromaDB
            # _chroma_client = chromadb.PersistentClient(
            #     path=str(db_path),
            #     settings=Settings(
            #         anonymized_telemetry=False,
            #         allow_reset=True
            #     )
            # )
            
            # TODO: Criar ou obter collection
            # collection = _chroma_client.get_or_create_collection(
            #     name=settings.CHROMA_COLLECTION_NAME,
            #     metadata={"description": "Bulas de medicamentos vetorizadas"}
            # )
            
            logger.info(f"Cliente ChromaDB inicializado em: {db_path}")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar ChromaDB: {str(e)}")
            raise
    
    return _chroma_client


def get_collection():
    """
    🔹 IMPLEMENTAR: Retorna a collection de bulas.
    
    Returns:
        Collection do ChromaDB
    """
    client = get_chroma_client()
    # TODO: Retornar collection
    # return client.get_collection(settings.CHROMA_COLLECTION_NAME)
    return None

