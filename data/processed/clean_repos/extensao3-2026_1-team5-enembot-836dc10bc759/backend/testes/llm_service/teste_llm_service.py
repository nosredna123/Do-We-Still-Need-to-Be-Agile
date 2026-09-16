from app.services.llm_service import LLMService

from testes.llm_service.prompts import prompt3 as prompt
from testes.llm_service.questions import question2 as question
from testes.llm_service.queries import query1

# from app.essential_imports import *
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio


# O histórico deve ser chamado no serviço?
history = None

model = LLMService(
    'google', 
    history = history
)

app = FastAPI()

@app.get("/ask")
async def ask_question(knowledge_area: str, question: str, query: str):
    service = LLMService('google', history = history, prompt=prompt)

    async def event_generator():
        # Itera sobre o gerador assíncrono do service
        async for token in service.call_agent(knowledge_area, question, query):
            yield f"data: {token}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Testando o modelo

call_dict = {
    'knowledge_area': 'Ciências da Natureza',
    'question': question,
    'query': None,
 }


# Supondo que ask_question seja sua função assíncrona que faz o yield dos tokens
async def main():
    while True:
        print("\n" + "=" * 100 + "\n")
        user_input = input("Digite a query: ")
            
        call_dict['query'] = user_input

        print("\nResposta do modelo: ", end="", flush=True)

        # 1. Chama a função da rota (ela retorna um StreamingResponse)
        response = await ask_question(**call_dict)

        full_response = ""
        
        # 2. O StreamingResponse guarda o gerador em .body_iterator
        # É aqui que a "mágica" do streaming acontece no FastAPI
        async for chunk in response.body_iterator:
            # chunk vem como bytes ou string formatada em SSE: "data: token\n\n"
            # Vamos limpar para exibir apenas o texto no terminal
            token = chunk.replace("data: ", "").replace("\n\n", "")
            
            full_response += token
            print(token, end="", flush=True)

            await asyncio.sleep(0.4)

        # print(f"\n\n[RESPOSTA FINAL ARMAZENADA]: {full_response}")


# Ponto de entrada para rodar o código assíncrono
if __name__ == "__main__":
    # Query
    # O item B e o C estão errados com certeza. Estou achando que a resposta ou é o A ou o D, mas não sei se isso realmente implica em aumento da população dos individuos.

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nEncerrado pelo usuário.")

