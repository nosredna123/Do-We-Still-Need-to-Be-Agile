# modules/intent_classifier.py
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import Optional


# 1. Atualizamos o modelo para incluir 'message'
class IntentResponse(BaseModel):
    intent: str = Field(description="A intenção do usuário.")
    medicamento: Optional[str] = Field(None, description="Nome do medicamento.")
    topic: Optional[str] = Field(None, description="Tópico da pergunta.")
    message: str = Field(..., description="Uma resposta curta e amigável para o usuário.")


# 2. Atualizamos o Prompt para pedir a mensagem
INTENT_PROMPT_TEMPLATE = """
Você é um assistente de saúde chamado 'Bulicoso'.
Analise o texto do usuário e retorne um JSON com a classificação e uma resposta amigável.

ESTRUTURA JSON:
{{
  "intent": "...", // 'schedule', 'cancel', 'edit', 'query_rag', 'unknown'
  "medicamento": "...", // null se não houver
  "topic": "...", // null se não houver, tente associar a "reações adversas" se ele perguntar as reações de um medicamento, se for algo relacionado a automedicação, coloque outra coisa, ou "agendamento"
  "message": "..." // Sua resposta textual para o usuário
}}

REGRAS PARA A MENSAGEM ('message'):
- Se for 'schedule': Pergunte os detalhes (qual remédio, frequência, dias) se não foram dados, ou confirme que entendeu.
- Se for 'cancel' ou 'edit': Diga que vai buscar os agendamentos.
- Se for 'query_rag': Diga algo como "Vou verificar na bula para você...".
- Se for 'unknown': Diga que não entendeu e dê exemplos do que pode fazer.

TEXTO DO USUÁRIO:
{user_query}

JSON:
"""

prompt_template = PromptTemplate(
    input_variables=["user_query"],
    template=INTENT_PROMPT_TEMPLATE
)


def classify_intent(query: str, llm: ChatGoogleGenerativeAI) -> IntentResponse:
    print(f"[Classifier] Classificando: '{query}'")
    prompt = prompt_template.format(user_query=query)

    try:
        response = llm.invoke(prompt)
        content = response.content

        # Limpeza básica do JSON
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            content = json_match.group(0)

        data = json.loads(content)
        return IntentResponse(**data)

    except Exception as e:
        print(f"[Classifier ERRO] {e}")
        # Fallback de erro
        return IntentResponse(
            intent="unknown",
            message="Desculpe, tive um erro interno. Pode repetir?"
        )