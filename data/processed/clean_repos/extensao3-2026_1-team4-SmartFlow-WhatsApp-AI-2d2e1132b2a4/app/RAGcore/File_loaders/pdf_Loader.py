# app/RAGcore/loaders/pdf_loader.py

from pathlib import Path
from typing import List

from pypdf import PdfReader


class PDFLoader:

    def load(
        self,
        file_path: str
    ) -> str:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {file_path}"
            )

        if path.suffix.lower() != ".pdf":
            raise ValueError(
                "O arquivo precisa ser .pdf"
            )

        reader = PdfReader(str(path))

        pages: List[str] = []

        print(f"\nPDF carregado: {path.name}")
        print(f"Páginas: {len(reader.pages)}")

        for page_number, page in enumerate(
            reader.pages,
            start=1
        ):

            try:

                extracted = page.extract_text()

                if not extracted:
                    continue

                extracted = extracted.strip()

                if not extracted:
                    continue

                page_content = (
                    f"[PÁGINA {page_number}]\n"
                    f"{extracted}"
                )

                pages.append(page_content)

                print(
                    f"Página {page_number} extraída "
                    f"({len(extracted)} chars)"
                )

            except Exception as ex:

                print(
                    f"Erro ao extrair "
                    f"página {page_number}: {ex}"
                )

        if not pages:
            raise ValueError(
                "Nenhum texto pôde ser extraído do PDF."
            )

        return "\n\n".join(pages)