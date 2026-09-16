import os
import re
import time
import numpy as np
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings  # <-- CORREÇÃO 3
from langchain_chroma import Chroma  # <-- CORREÇÃO 2
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

# ==========================
# CONFIGURAÇÕES
# ==========================
DB_DIR = "./chroma_bulas_local"
COLLECTION_NAME = "bulas_local"  # <-- CORREÇÃO 1
load_dotenv(".env", override=True)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
TOP_K = 5
SUBCHUNK_SIZE = 1000
MIN_CONFIDENCE_THRESHOLD = 0.6  # Limite para fallback


# ==========================
# FUNÇÕES AUXILIARES
# ==========================
def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()


def compute_confidence(scores):
    if not scores:
        return 0.0
    # Scores são 1.0 - distância, então a média é a confiança
    return round(float(np.mean(scores)), 3)


# ==========================
# CONFIGURAÇÃO DO GEMINI
# ==========================
llm_rag = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    temperature=0.5,
    google_api_key=GOOGLE_API_KEY
)

PROMPT_TEMPLATE = """
Você é um assistente especialista em bulas de medicamentos.
Responda à pergunta do usuário usando APENAS os trechos de contexto abaixo.

Contexto:
{context_chunks}

Pergunta:
{question}

Instruções para a resposta (formato JSON):

1.  **answer (string)**:
    * Extraia a resposta diretamente do contexto para responder à pergunta, pense e fale algo que faz sentido de acordo com o contexto.
    * **Se o contexto contiver qualquer informação relevante** (mesmo que parcial, como uma menção em 'Interações'), **apresente essa informação.**
    * Se o contexto não contiver NENHUMA informação relevante para a pergunta, responda EXATAMENTE: "NOT_FOUND"

2. **confidence**:
    * Quero o nível de confiança de 0 a 1.

Responda APENAS com o objeto JSON.
"""

prompt_template = PromptTemplate(
    input_variables=["context_chunks", "question"],
    template=PROMPT_TEMPLATE
)

# ==========================
# CARREGAR ChromaDB EXISTENTE
# ==========================
print("[INFO] Carregando ChromaDB local existente...")
embedding_func = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # <-- Nome completo
)
vectordb = Chroma(
    persist_directory=DB_DIR,
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_func
)


# ==========================
# FUNÇÃO RAG (Otimizada)
# ==========================
def query_rag(query):
    start_time = time.time()

    # [OTIMIZAÇÃO 4] Usar 'similarity_search_with_relevance_scores'
    # Isso busca os docs E já retorna o score de similaridade (distância)
    # Não precisamos recalcular embeddings!
    docs_with_scores = vectordb.similarity_search_with_relevance_scores(
        query, k=TOP_K
    )

    context_blocks = []
    scores = []  # Similaridade (1.0 = bom)
    sources = set()  # Usar um set para evitar títulos duplicados

    for d, score in docs_with_scores:
        # Chroma/HuggingFace retorna Distância L2 (0.0 = idêntico).
        # Convertemos para "Similaridade" (1.0 = idêntico) para nossa confiança.
        # Esta é uma boa heurística para vetores normalizados.
        similarity = 1.0 - score
        scores.append(similarity)

        snippet = d.page_content[:SUBCHUNK_SIZE]
        title = d.metadata.get('title', 'unknown')
        sources.add(title)
        context_blocks.append(f"[{title}] {snippet}")

    confidence = compute_confidence(scores)
    context_str = "\n\n".join(context_blocks) if context_blocks else "NOT_FOUND"

    # Se não encontrar ou confiança baixa, fallback para Gemini
    if confidence < MIN_CONFIDENCE_THRESHOLD or context_str == "NOT_FOUND":
        print(f"[INFO] Confiança baixa ({confidence:.2f}) ou NOT_FOUND. Fallback direto ao Gemini...")
        try:
            resp = llm_rag.invoke(f"""
Você é um especialista em medicamentos. Responda com segurança, apenas o necessário.
Pergunta: {query}
Responda em JSON com:
- answer: texto da resposta
- confidence: 0.5 (fallback)
- sources: []
            """)
            raw_text = resp.content if hasattr(resp, "content") else str(resp)
            confidence = 0.5  # Marcamos como confiança de fallback
        except Exception as e:
            raw_text = f"Erro no fallback Gemini: {e}"
            confidence = 0.0
    else:
        # Usando RAG com Chroma
        try:
            prompt = prompt_template.format(context_chunks=context_str, question=query)
            resp = llm_rag.invoke(prompt)
            raw_text = resp.content if hasattr(resp, "content") else str(resp)
            # O LLM pode retornar um JSON que *inclui* a confiança.
            # Se não, usamos a confiança da busca.
            # (Para simplificar, vamos apenas usar a confiança da busca)
        except Exception as e:
            raw_text = f"Erro no RAG: {e}"
            confidence = 0.0  # Erro no RAG

    elapsed = round(time.time() - start_time, 2)
    return {"query": query, "response": raw_text, "confidence": confidence, "time_sec": elapsed}


# ==========================
# TESTE DE CONSULTA
# ==========================
queries = [
    "Quais são as reações adversas da DIPIRONA SÓDICA?",
    "Dormec Dose Adultos",
    "Dormec Interação"
]

for q in queries:
    result = query_rag(q)
    print("\n" + "=" * 80)
    print(f"[QUERY] {result['query']}")
    print(f"[TEMPO] {result['time_sec']}s | Confiança: {result['confidence']}")
    print(f"[RESPOSTA]\n{result['response']}")