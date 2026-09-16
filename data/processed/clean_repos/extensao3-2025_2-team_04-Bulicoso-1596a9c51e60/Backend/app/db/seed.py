"""
🔹 SCRIPT DE SEED - Popular banco vetorial inicial

Este script é executado para popular o ChromaDB com bulas iniciais.
Pode ser executado manualmente ou como parte do setup.

IMPLEMENTAÇÃO NECESSÁRIA:
- Ler PDFs de bulas de um diretório
- Processar via vector_service
- Armazenar no ChromaDB
"""

import asyncio
from pathlib import Path
from app.services.vector_service import VectorService
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger()


async def seed_database(bulas_directory: str = "./data/bulas"):
    """
    🔹 IMPLEMENTAR: Popula o ChromaDB com bulas iniciais.
    
    Args:
        bulas_directory: Diretório contendo PDFs de bulas
    """
    logger.info("Iniciando seed do banco de dados...")
    
    try:
        # Verificar se diretório existe
        bulas_path = Path(bulas_directory)
        if not bulas_path.exists():
            logger.warning(f"Diretório não encontrado: {bulas_directory}")
            logger.info("Criando diretório...")
            bulas_path.mkdir(parents=True, exist_ok=True)
            logger.info("Adicione PDFs de bulas no diretório e execute novamente.")
            return
        
        # Inicializar serviço de vetorização
        vector_service = VectorService()
        
        # TODO: Processar todos os PDFs do diretório
        # pdf_files = list(bulas_path.glob("*.pdf"))
        # 
        # if not pdf_files:
        #     logger.warning("Nenhum PDF encontrado no diretório.")
        #     return
        # 
        # logger.info(f"Encontrados {len(pdf_files)} arquivos PDF")
        # 
        # for pdf_file in pdf_files:
        #     medication_name = pdf_file.stem
        #     logger.info(f"Processando: {medication_name}")
        #     await vector_service.process_pdf(str(pdf_file), medication_name)
        
        logger.info("Seed concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro no seed: {str(e)}")
        raise


if __name__ == "__main__":
    """
    Executar seed manualmente:
    python -m app.db.seed
    """
    asyncio.run(seed_database())

