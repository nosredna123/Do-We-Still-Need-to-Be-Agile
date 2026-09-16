import asyncio
import io

import PyPDF2


async def extract_text_from_pdf(file_bytes: bytes) -> str:
    return await asyncio.to_thread(_extract_sync, file_bytes)


def _extract_sync(file_bytes: bytes) -> str:
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    except Exception:
        raise ValueError("Arquivo inválido ou corrompido — envie um PDF válido")

    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"

    if not text.strip():
        raise ValueError("Não foi possível extrair texto do PDF")

    return text.strip()
