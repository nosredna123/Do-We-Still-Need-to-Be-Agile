import json
import re
import base64
import os

from groq import Groq
from .prompt import build_interview_system_prompt

# ─── Cliente ──────────────────────────────────────────────────────────────────

ANALYSIS_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL   = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"

_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _chat(messages: list, model: str = ANALYSIS_MODEL, json_mode: bool = False, max_tokens: int = 2048) -> str:
    """Wrapper síncrono para o Groq — usado pelas funções async via agent._call_groq."""
    kwargs = dict(model=model, messages=messages, max_tokens=max_tokens, temperature=0.1)
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    resp = _groq.chat.completions.create(**kwargs)
    return resp.choices[0].message.content


# ─── Helpers ──────────────────────────────────────────────────────────────────

def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


# ─── Extração de vaga (visão) ─────────────────────────────────────────────────

async def extract_job_from_image(image_bytes: bytes) -> str:
    """Extrai texto da imagem da vaga usando modelo multimodal do Groq."""
    from services.agent import tool_extract_job  # evita import circular
    return await tool_extract_job(image_bytes)


# ─── Análise de compatibilidade ───────────────────────────────────────────────

async def analyze_compatibility(job_description: str, resume_text: str) -> dict:
    """Analisa compatibilidade entre vaga e currículo."""
    from services.agent import tool_analyze_compatibility, tool_extract_resume_profile
    resume_profile = await tool_extract_resume_profile(resume_text)
    return await tool_analyze_compatibility(job_description, resume_profile, resume_text)


async def analyze_with_vision(resume_text: str, image_bytes: bytes) -> dict:
    """Pipeline completo: extrai vaga da imagem e analisa compatibilidade."""
    job_description = await extract_job_from_image(image_bytes)
    return await analyze_compatibility(job_description, resume_text)


# ─── Geração de perguntas de entrevista ───────────────────────────────────────

async def generate_interview_questions(analysis_result: dict) -> list[str]:
    """Gera 10 perguntas de entrevista com base na análise de compatibilidade."""
    import asyncio

    messages = [
        {
            "role": "system",
            "content": build_interview_system_prompt()
        },
        {
            "role": "user",
            "content": f"""Com base nessa análise de compatibilidade:

VAGA: {analysis_result.get('titulo_vaga')}
HABILIDADES DA VAGA: {', '.join(analysis_result.get('habilidades_vaga', []))}
PONTOS FORTES DO CANDIDATO: {', '.join(analysis_result.get('pontos_fortes', []))}
PONTOS FRACOS DO CANDIDATO: {', '.join(analysis_result.get('pontos_fracos', []))}
HABILIDADES FALTANTES: {', '.join(analysis_result.get('habilidades_faltantes', []))}
NÍVEL DE COMPATIBILIDADE: {analysis_result.get('nivel_compatibilidade')}%

Gere 10 perguntas que um entrevistador provavelmente fará para esse candidato.
Misture perguntas técnicas da área, perguntas sobre os pontos fracos e perguntas comportamentais.

Retorne SOMENTE este JSON:
{{
  "perguntas": [
    "<pergunta 1>",
    "<pergunta 2>",
    "<pergunta 3>",
    "<pergunta 4>",
    "<pergunta 5>",
    "<pergunta 6>",
    "<pergunta 7>",
    "<pergunta 8>",
    "<pergunta 9>",
    "<pergunta 10>"
  ]
}}"""
        }
    ]

    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(
        None,
        lambda: _chat(messages, json_mode=True, max_tokens=2048)
    )

    print("PERGUNTAS GERADAS:", raw[:300])

    raw = raw.strip()
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if not json_match:
        raise ValueError(f"Modelo não retornou JSON válido: {raw}")

    result = json.loads(json_match.group())
    return result.get("perguntas", [])