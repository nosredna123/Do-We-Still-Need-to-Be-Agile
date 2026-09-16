from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.RAGcore.knowledge_service import KnowledgeService
from app.RAGcore.File_loaders.txt_Loader import TXTLoader
from app.RAGcore.File_loaders.pdf_Loader import PDFLoader

class KnowledgeIngestor:

    def __init__(self):
        self.knowledge_service = KnowledgeService()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""]
        )

    def ingest_text(self, ia_id: int, text: str):
        """Aplica a limpeza, divide em chunks e envia para o service salvar."""
        cleaned_text = self._clean_text(text)
        chunks = self.splitter.split_text(cleaned_text)

        print(f"Chunks gerados: {len(chunks)}")

        for i, chunk in enumerate(chunks, start=1):
            print(f"\n--- Chunk {i} ---")
            print(chunk[:200])

            self.knowledge_service.add_chunk(
                ia_id=ia_id,
                chunk=chunk
            )

        print("\nTexto ingerido com sucesso.")

    def ingest_txt(self, ia_id: int, file_path: str):
        """Carrega o TXT usando o TXTLoader e faz a ingestão."""
        loader = TXTLoader()
        text = loader.load(file_path)
        self.ingest_text(ia_id=ia_id, text=text)

    def ingest_pdf(self, ia_id: int, file_path: str):
        """Carrega o PDF usando o PDFLoader e faz a ingestão."""
        loader = PDFLoader()
        full_text = loader.load(file_path)
        self.ingest_text(ia_id=ia_id, text=full_text)

    def _clean_text(self, text: str) -> str:
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            cleaned.append(line)
        return "\n".join(cleaned)