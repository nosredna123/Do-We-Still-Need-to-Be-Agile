import asyncio

from duckduckgo_search import DDGS


def _ddg_text(query: str, limit: int) -> list[dict]:
    with DDGS() as ddgs:
        return list(ddgs.text(query, max_results=limit, region="br-pt"))


async def search_related_jobs(
    titulo_vaga: str,
    habilidades: list[str],
    limit: int = 5,
) -> list[dict]:
    skills_part = " ".join(habilidades[:3]) if habilidades else ""
    query = f'vaga "{titulo_vaga}" {skills_part}'.strip()

    raw = await asyncio.to_thread(_ddg_text, query, limit)

    return [
        {
            "titulo": r.get("title", ""),
            "url": r.get("href", ""),
            "descricao": r.get("body", ""),
        }
        for r in raw
        if r.get("href")
    ]
