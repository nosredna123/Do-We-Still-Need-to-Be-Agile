import asyncio
import base64
import hashlib
import json
import re
import time
import os

from groq import Groq, RateLimitError
from fastapi import HTTPException
from .prompt import (
    build_compatibility_system_prompt,
    build_improvement_system_prompt,
)

# ─── Modelos ──────────────────────────────────────────────────────────────────

ANALYSIS_MODEL = "llama-3.3-70b-versatile"
VISION_MODEL   = "meta-llama/llama-4-maverick-17b-128e-instruct-fp8"

_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─── Cache de currículos ──────────────────────────────────────────────────────

_resume_cache: dict[str, str] = {}
_MAX_CACHE = 200

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_space = truncated.rfind(" ")
    return truncated[:last_space] if last_space > 0 else truncated


def _log(step: str, elapsed: float):
    print(f"[AGENTE] {step} concluído em {elapsed:.1f}s")


def _cache_set(key: str, value: str):
    if len(_resume_cache) >= _MAX_CACHE:
        _resume_cache.pop(next(iter(_resume_cache)))
    _resume_cache[key] = value


# ─── Cliente Groq (substitui _call_ollama) ────────────────────────────────────

async def _call_groq(
    messages: list,
    model: str = ANALYSIS_MODEL,
    json_mode: bool = False,
    temperature: float = 0.1,
    max_tokens: int = 1024,
) -> str:
    kwargs = dict(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    for attempt in range(3):
        try:
            loop = asyncio.get_event_loop()
            resp = await loop.run_in_executor(
                None,
                lambda: _groq.chat.completions.create(**kwargs)
            )
            return resp.choices[0].message.content
        except RateLimitError:
            wait = 2 ** attempt  # 1s, 2s, 4s
            print(f"[AGENTE] Rate limit atingido, aguardando {wait}s...")
            await asyncio.sleep(wait)
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Erro ao chamar Groq: {str(e)}")

    raise HTTPException(status_code=429, detail="Limite de requisições atingido. Tente em instantes.")


# ─── Tools ────────────────────────────────────────────────────────────────────

async def tool_extract_job(image_bytes: bytes) -> str:
    """Extrai informações da vaga a partir de uma imagem."""
    t = time.monotonic()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                },
                {
                    "type": "text",
                    "text": (
                        "Você está analisando uma imagem de vaga de emprego. "
                        "Extraia e liste em detalhes: título do cargo, habilidades técnicas exigidas, "
                        "nível de experiência requerido (anos) e principais responsabilidades. "
                        "Responda em português do Brasil."
                    )
                }
            ]
        }
    ]

    result = await _call_groq(messages, model=VISION_MODEL, temperature=0.1, max_tokens=1024)
    _log("tool_extract_job", time.monotonic() - t)
    return result


async def tool_extract_resume_profile(resume_text: str) -> str:
    """Extrai perfil resumido do currículo. Usa cache para evitar chamadas repetidas."""
    resume_hash = hashlib.md5(resume_text.encode()).hexdigest()
    if resume_hash in _resume_cache:
        print("[AGENTE] tool_extract_resume_profile: cache hit")
        return _resume_cache[resume_hash]

    t = time.monotonic()
    messages = [
        {
            "role": "system",
            "content": "Você é um especialista em análise de currículos. Responda sempre em português do Brasil."
        },
        {
            "role": "user",
            "content": f"""CURRÍCULO:
{_truncate(resume_text, 3000)}

Extraia e liste de forma objetiva:
- Cargo atual ou objetivo profissional
- Habilidades técnicas principais (máximo 10 itens)
- Total de anos de experiência profissional
- Nível de formação acadêmica
- Idiomas (se mencionado)"""
        }
    ]

    profile = await _call_groq(messages, temperature=0.1, max_tokens=512)
    _cache_set(resume_hash, profile)
    _log("tool_extract_resume_profile", time.monotonic() - t)
    return profile


async def tool_analyze_compatibility(
    job_description: str,
    resume_profile: str,
    resume_text: str,
) -> dict:
    """Analisa compatibilidade entre vaga e candidato. Retorna dict normalizado."""
    messages = [
        {
            "role": "system",
            "content": build_compatibility_system_prompt()
        },
        {
            "role": "user",
            "content": f"""Analise a compatibilidade entre a vaga e o candidato.

DESCRIÇÃO DA VAGA:
{job_description}

PERFIL DO CANDIDATO (resumido):
{resume_profile}

CURRÍCULO COMPLETO (trecho):
{_truncate(resume_text, 2000)}

Retorne um objeto JSON com EXATAMENTE estes campos em português:
- "titulo_vaga": nome do cargo da vaga (string)
- "habilidades_vaga": lista de habilidades exigidas pela vaga (lista de strings)
- "nivel_compatibilidade": porcentagem de compatibilidade de 0 a 100 (número inteiro)
- "pontos_fortes": lista de pontos positivos do candidato para esta vaga (lista de strings)
- "pontos_fracos": lista de pontos negativos ou lacunas do candidato (lista de strings)
- "habilidades_faltantes": habilidades da vaga que o candidato não possui (lista de strings)
- "recomendacao": exatamente uma das três opções: "Aprovado para entrevista", "Requer desenvolvimento" ou "Não recomendado"
- "resumo": análise geral em 2 frases curtas (string)"""
        }
    ]

    for attempt in range(3):
        t = time.monotonic()
        raw = await _call_groq(
            messages,
            json_mode=True,
            temperature=round(0.1 + attempt * 0.05, 2),
            max_tokens=1024,
        )
        _log(f"tool_analyze_compatibility (tentativa {attempt + 1})", time.monotonic() - t)
        print(f"[AGENTE] resposta bruta:", raw[:400])

        try:
            data = json.loads(raw)
            return _normalize_and_coerce(data)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    return _normalize_and_coerce(data)
                except json.JSONDecodeError:
                    continue

    raise ValueError("Agente não conseguiu gerar JSON válido após 3 tentativas")


# ─── Normalização e coerção de tipos ──────────────────────────────────────────

def _normalize_and_coerce(data: dict) -> dict:
    aliases = {
        "titulo_vaga":           ["job_title", "title", "titulo", "vaga", "position"],
        "habilidades_vaga":      ["required_skills", "skills", "habilidades", "requisitos", "requirements"],
        "nivel_compatibilidade": ["compatibility_score", "score", "nivel", "compatibilidade", "compatibility", "percentage"],
        "pontos_fortes":         ["strengths", "strong_points", "fortes", "positives"],
        "pontos_fracos":         ["weaknesses", "weak_points", "fracos", "negatives"],
        "habilidades_faltantes": ["missing_skills", "gaps", "faltantes", "missing"],
        "recomendacao":          ["recommendation", "hiring_recommendation", "recomendação", "decision"],
        "resumo":                ["summary", "overview", "analysis"],
    }
    defaults = {
        "titulo_vaga": "Não identificado",
        "habilidades_vaga": [],
        "nivel_compatibilidade": 0,
        "pontos_fortes": [],
        "pontos_fracos": [],
        "habilidades_faltantes": [],
        "recomendacao": "Requer desenvolvimento",
        "resumo": "",
    }

    normalized = {}
    for field, alt_names in aliases.items():
        value = data.get(field)
        if value is None:
            for alt in alt_names:
                if alt in data:
                    value = data[alt]
                    break
        normalized[field] = value if value is not None else defaults[field]

    normalized["nivel_compatibilidade"] = _to_int(normalized["nivel_compatibilidade"])
    normalized["titulo_vaga"]  = str(normalized["titulo_vaga"])
    normalized["recomendacao"] = str(normalized["recomendacao"])
    normalized["resumo"]       = str(normalized["resumo"])
    for list_field in ["habilidades_vaga", "pontos_fortes", "pontos_fracos", "habilidades_faltantes"]:
        normalized[list_field] = _to_list(normalized[list_field])

    return normalized


def _to_int(value) -> int:
    try:
        v = int(float(str(value).replace("%", "").strip()))
        return max(0, min(100, v))
    except (ValueError, TypeError):
        return 0


def _to_list(value) -> list:
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str) and value:
        return [value]
    return []


# ─── Improvement Tool ─────────────────────────────────────────────────────────

async def tool_improve_resume(resume_text: str) -> dict:
    """Analisa o currículo e retorna sugestões de melhoria detalhadas."""
    messages = [
        {
            "role": "system",
            "content": build_improvement_system_prompt()
        },
        {
            "role": "user",
            "content": f"""Analise o currículo abaixo e retorne sugestões de melhoria detalhadas.

CURRÍCULO:
{_truncate(resume_text, 4000)}

Retorne um objeto JSON com EXATAMENTE estes campos em português:
- "pontuacao_geral": pontuação geral do currículo de 0 a 100 (número inteiro)
- "resumo_diagnostico": diagnóstico geral do currículo em 2 a 3 frases (string)
- "melhorias_por_secao": lista de objetos, cada um com:
    - "secao": nome da seção analisada (ex: "Objetivo", "Experiência", "Habilidades", "Educação", "Formatação")
    - "problemas": lista de problemas encontrados nessa seção (lista de strings)
    - "sugestoes": lista de sugestões concretas para melhorar essa seção (lista de strings)
- "habilidades_recomendadas": lista de habilidades relevantes que o candidato deveria adicionar (lista de strings)
- "palavras_chave_faltantes": lista de palavras-chave importantes para o mercado que estão ausentes (lista de strings)
- "acoes_prioritarias": lista de 3 a 5 ações prioritárias mais importantes a tomar imediatamente (lista de strings)"""
        }
    ]

    for attempt in range(3):
        t = time.monotonic()
        raw = await _call_groq(
            messages,
            json_mode=True,
            temperature=round(0.1 + attempt * 0.05, 2),
            max_tokens=2048,
        )
        _log(f"tool_improve_resume (tentativa {attempt + 1})", time.monotonic() - t)
        print(f"[AGENTE] resposta bruta:", raw[:400])

        try:
            data = json.loads(raw)
            return _normalize_improvement(data)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                    return _normalize_improvement(data)
                except json.JSONDecodeError:
                    continue

    raise ValueError("Agente não conseguiu gerar JSON válido após 3 tentativas")


def _normalize_improvement(data: dict) -> dict:
    return {
        "pontuacao_geral":        _to_int(data.get("pontuacao_geral", 0)),
        "resumo_diagnostico":     str(data.get("resumo_diagnostico", data.get("summary", ""))),
        "melhorias_por_secao":    _normalize_sections(data.get("melhorias_por_secao", data.get("sections", []))),
        "habilidades_recomendadas": _to_list(data.get("habilidades_recomendadas", data.get("recommended_skills", []))),
        "palavras_chave_faltantes": _to_list(data.get("palavras_chave_faltantes", data.get("missing_keywords", []))),
        "acoes_prioritarias":     _to_list(data.get("acoes_prioritarias", data.get("priority_actions", []))),
    }


def _normalize_sections(secoes) -> list:
    if not isinstance(secoes, list):
        return []
    normalized = []
    for item in secoes:
        if not isinstance(item, dict):
            continue
        normalized.append({
            "secao":     str(item.get("secao", item.get("section", ""))),
            "problemas": _to_list(item.get("problemas", item.get("problems", []))),
            "sugestoes": _to_list(item.get("sugestoes", item.get("suggestions", []))),
        })
    return normalized


# ─── Agent Orchestrator ────────────────────────────────────────────────────────

async def run_agent(image_bytes: bytes, resume_text: str) -> dict:
    """Orquestra as tools com imagem da vaga + currículo."""
    t_total = time.monotonic()

    job_description, resume_profile = await asyncio.gather(
        tool_extract_job(image_bytes),
        tool_extract_resume_profile(resume_text),
    )

    result = await tool_analyze_compatibility(job_description, resume_profile, resume_text)

    _log("run_agent TOTAL", time.monotonic() - t_total)
    return result


async def run_agent_from_text(job_description: str, resume_text: str) -> dict:
    """Orquestra as tools com descrição textual da vaga + currículo.
    Usado pela rota /analyze que recebe job_description como Form field.
    """
    t_total = time.monotonic()

    resume_profile = await tool_extract_resume_profile(resume_text)
    result = await tool_analyze_compatibility(job_description, resume_profile, resume_text)

    _log("run_agent_from_text TOTAL", time.monotonic() - t_total)
    return result