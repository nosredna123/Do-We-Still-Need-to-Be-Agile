# modules/rag_manager.py
import os
import re
import time
import numpy as np
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import json

# Suas configurações globais do RAG
# Resolve o caminho do banco relativo ao arquivo atual (rag_manager.py está em app/modules/)
# Queremos chegar em app/chroma_bulas_local
DB_DIR = "modules/chroma_bulas_local"
COLLECTION_NAME = "bulas_local"
RAG_TOP_K = 5
MIN_CONFIDENCE_THRESHOLD = 0.6

# Seu template de prompt RAG
RAG_PROMPT_TEMPLATE = """
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
    * Se o contexto não contiver NENHUMA informação relevante para a pergunta, responda EXATAMENTE sobre as reações alérgicas do medicamento com seus conhecimentos gerais

2. **confidence**:
    * Quero o nível de confiança de 0 a 1.

Responda APENAS com o objeto JSON.
"""


class RAGManager:
    def __init__(self, google_api_key: str):
        print("[RAG] Inicializando RAG Manager...")
        try:
            self.embedding_func = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            self.vectordb = Chroma(
                persist_directory=DB_DIR,
                collection_name=COLLECTION_NAME,
                embedding_function=self.embedding_func
            )
            self.llm_rag = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.5,
                google_api_key=google_api_key
            )
            self.prompt_template = PromptTemplate(
                input_variables=["context_chunks", "question"],
                template=RAG_PROMPT_TEMPLATE
            )
            print("[RAG] RAG Manager carregado.")
        except Exception as e:
            print(f"[RAG ERRO CRÍTICO] Falha ao carregar ChromaDB: {e}")
            self.vectordb = None

    def _compute_confidence(self, scores):
        if not scores: return 0.0
        return round(float(np.mean(scores)), 3)

    def query(self, medicamento: str, topic: str) -> dict:
        """
        Executa a consulta RAG com o guardrail.
        """
        start_time = time.time()

        # === O GUARDRAIL QUE VOCÊ PEDIU ===
        if topic != "reações adversas":
            print(f"[RAG Guardrail] Tópico bloqueado: '{topic}'.")
            return {
                "query": f"Consulta sobre {medicamento} ({topic})",
                "response": json.dumps({
                    "answer": "Desculpe, como assistente de saúde, só posso fornecer informações sobre 'reações adversas' para evitar o risco de automedicação. Para outras dúvidas, consulte seu médico.",
                    "confidence": 0.0
                }),
                "confidence": 0.0,
                "time_sec": 0.01
            }

        if self.vectordb is None:
            return {"error": "Banco RAG não inicializado."}

        query = medicamento
        print(f"[RAG] Executando consulta: '{query}'")

        docs_with_scores = self.vectordb.similarity_search_with_relevance_scores(
            query, k=RAG_TOP_K
        )

        context_blocks, scores = [], []
        for d, score in docs_with_scores:
            similarity = 1.0 - score
            scores.append(similarity)
            context_blocks.append(d.page_content)

        confidence = self._compute_confidence(scores)
        context_str = "\n\n".join(context_blocks) if context_blocks else "NOT_FOUND"

        #
        # --- INÍCIO DO BLOCO LÓGICO (IF/ELSE) ---
        #
        if confidence < MIN_CONFIDENCE_THRESHOLD or context_str == "NOT_FOUND":
            print(f"[RAG] Confiança baixa ({confidence:.2f}). Fallback ao Gemini (conhecimento geral).")

            # Criar um prompt de fallback
            fallback_prompt = f"""
            Você é um especialista em medicamentos. A bula local não foi encontrada.
            Responda à pergunta do usuário usando seu conhecimento geral, mas no formato JSON.

            Pergunta:
            {query}

            Responda APENAS com o objeto JSON (formato: {{"answer": "Sua resposta aqui...", "confidence": 0.5}}).
            Se você não sabe a resposta, responda: {{"answer": "NOT_FOUND", "confidence": 0.2}}
            """

            try:
                resp = self.llm_rag.invoke(fallback_prompt)
                raw_text = resp.content

                # Limpar markdown code blocks se houver
                raw_text = raw_text.strip()
                if raw_text.startswith("```"):
                    # Remove primeira linha (```json) e última (```)
                    raw_text = re.sub(r"^```[a-zA-Z]*\n", "", raw_text)
                    raw_text = re.sub(r"\n```$", "", raw_text)

                # Tentar limpar a resposta do LLM para garantir que é só o JSON
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    raw_text = json_match.group(0)
                    # Tenta parsear para garantir que o JSON é válido e pegar a confiança
                    parsed_json = json.loads(raw_text)
                    confidence = parsed_json.get("confidence", 0.5)  # Pega a confiança que o LLM retornou
                else:
                    # Se o LLM não retornar JSON, forçamos o formato
                    raw_text = json.dumps({"answer": "NOT_FOUND", "confidence": 0.2})
                    confidence = 0.2

            except Exception as e:
                print(f"[RAG ERRO] Erro no fallback do Gemini: {e}")
                raw_text = json.dumps({"answer": f"Erro no fallback do Gemini: {e}", "confidence": 0.0})
                confidence = 0.0

        else:
            # Este bloco (RAG com contexto) estava correto
            print(f"[RAG] Confiança alta ({confidence:.2f}). Usando RAG com ChromaDB.")
            try:
                prompt = self.prompt_template.format(context_chunks=context_str, question=query)
                resp = self.llm_rag.invoke(prompt)
                raw_text = resp.content

                # Limpar markdown code blocks se houver
                raw_text = raw_text.strip()
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```[a-zA-Z]*\n", "", raw_text)
                    raw_text = re.sub(r"\n```$", "", raw_text)

                # Injetar a confiança calculada (RAG score) no JSON de resposta
                try:
                    # Tenta encontrar o JSON na string (caso haja texto antes/depois)
                    json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                    if json_match:
                        clean_json_str = json_match.group(0)
                        response_json = json.loads(clean_json_str)
                        response_json["confidence"] = confidence # Sobrescreve com a confiança do RAG
                        raw_text = json.dumps(response_json, ensure_ascii=False)
                    else:
                        # Se não achar JSON, tenta parsear tudo ou mantém como está
                        response_json = json.loads(raw_text)
                        response_json["confidence"] = confidence
                        raw_text = json.dumps(response_json, ensure_ascii=False)
                except Exception as json_err:
                    print(f"[RAG AVISO] Falha ao injetar confiança no JSON: {json_err}")
                    # Se falhar o parse, mantemos o raw_text original do LLM,
                    # mas a confiança externa (do return) estará correta.

            except Exception as e:
                raw_text = json.dumps({"answer": f"Erro no RAG: {e}", "confidence": 0.0})
                confidence = 0.0  # Sobrescreve a confiança em caso de erro

        #
        # --- FIM DO BLOCO LÓGICO (IF/ELSE) ---
        #

        # Este 'return' é o único no final da função
        # e é executado após o 'if' ou o 'else' terminarem.
        elapsed = round(time.time() - start_time, 2)
        return {"query": query, "response": raw_text, "confidence": confidence, "time_sec": elapsed}

if __name__ == "__main__":
    load_dotenv(".env", override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Erro: GOOGLE_API_KEY não encontrada no .env")
    else:
        rag = RAGManager(google_api_key=api_key)
        # Teste com um medicamento comum
        result = rag.query("Quais são as reações da ACICLOVIR", "reações adversas")
        print(json.dumps(result, indent=2, ensure_ascii=False))