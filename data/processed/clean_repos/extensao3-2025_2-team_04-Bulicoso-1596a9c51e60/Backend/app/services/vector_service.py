"""
🔹 SERVIÇO DE VETORIZAÇÃO - Ingestão e processamento de bulas

Este serviço é responsável pelo processo offline de ingestão:

1. Carregar arquivos de texto da pasta batches
2. Fazer split em chunks com TextSplitter
3. Gerar embeddings usando HuggingFace Embeddings (all-MiniLM-L6-v2)
4. Armazenar no ChromaDB para busca semântica
"""

import os
from pathlib import Path
from typing import List, Optional
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from app.core.config import settings
from app.core.logger import setup_logger

logger = setup_logger()

# Configurações locais para garantir compatibilidade com rag_manager.py
# Configurações locais para garantir compatibilidade com rag_manager.py
# Resolve o caminho do banco relativo ao arquivo atual (vector_service.py está em app/services/)
# Queremos chegar em app/chroma_bulas_local
_current_dir = os.path.dirname(os.path.abspath(__file__)) # .../app/services
_app_dir = os.path.dirname(_current_dir) # .../app
DB_DIR = os.path.join(_app_dir, "chroma_bulas_local")
COLLECTION_NAME = "bulas_local"

class VectorService:
    """
    Serviço para vetorização e ingestão de bulas de medicamentos.
    """
    
    def __init__(self):
        """Inicializa o serviço de vetorização."""
        logger.info("Inicializando VectorService...")
        
        # Configurar embeddings (mesmo modelo do rag_manager.py)
        self.embedding_func = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Configurar text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Inicializar ChromaDB
        self.vectordb = Chroma(
            persist_directory=DB_DIR,
            collection_name=COLLECTION_NAME,
            embedding_function=self.embedding_func
        )
        
        logger.info("VectorService inicializado com sucesso.")
    
    async def process_text_file(self, file_path: str) -> bool:
        """
        Processa um arquivo de texto e adiciona ao ChromaDB.
        """
        try:
            # Carregar arquivo
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            # Adicionar metadados extras se necessário
            # O nome do arquivo pode ser usado como metadado
            filename = Path(file_path).name
            for doc in documents:
                doc.metadata["source"] = filename
                # Tentar extrair nome do medicamento do conteúdo (primeiras linhas) ou do nome do arquivo
                # Por enquanto, deixamos genérico
            
            # Dividir em chunks
            chunks = self.text_splitter.split_documents(documents)
            
            if not chunks:
                logger.warning(f"Nenhum chunk gerado para {file_path}")
                return False

            # Adicionar ao ChromaDB
            # O Chroma persiste automaticamente por padrão nas versões mais novas, 
            # mas o método add_documents gerencia isso.
            self.vectordb.add_documents(chunks)
            
            logger.info(f"Processado: {filename} - {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao processar {file_path}: {str(e)}")
            return False
    
    async def process_directory(self, directory_path: str) -> int:
        """
        Processa todos os arquivos .txt de um diretório.
        """
        logger.info(f"Iniciando processamento do diretório: {directory_path}")
        path = Path(directory_path)
        
        if not path.exists():
            logger.error(f"Diretório não encontrado: {directory_path}")
            return 0
            
        count = 0
        files = list(path.glob("*.txt"))
        total = len(files)
        
        logger.info(f"Encontrados {total} arquivos para processar.")
        
        for i, file_path in enumerate(files, 1):
            success = await self.process_text_file(str(file_path))
            if success:
                count += 1
            
            if i % 10 == 0:
                logger.info(f"Progresso: {i}/{total} arquivos processados.")
        
        logger.info(f"Processamento concluído. {count}/{total} arquivos ingeridos com sucesso.")
        return count


