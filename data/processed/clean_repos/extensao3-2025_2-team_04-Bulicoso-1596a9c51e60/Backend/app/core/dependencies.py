"""
Dependências globais da aplicação.

Este módulo gerencia instâncias compartilhadas que devem ser
reutilizadas em toda a aplicação, como:
- Cliente ChromaDB
- Cliente Google API
- Instâncias de serviços
"""

from functools import lru_cache
from app.db.chroma_client import get_chroma_client
from app.core.logger import setup_logger

logger = setup_logger()


@lru_cache()
def get_chroma_dependency():
    """
    Retorna a instância do cliente ChromaDB (singleton).
    
    Esta função usa lru_cache para garantir que apenas uma
    instância seja criada e reutilizada.
    """
    logger.info("Inicializando cliente ChromaDB...")
    return get_chroma_client()


# Outras dependências podem ser adicionadas aqui:
# - get_google_client()
# - get_llm_instance()
# etc.

