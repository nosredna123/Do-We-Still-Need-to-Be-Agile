from testes.backups.llm_services.llm_servicev3 import LLMService

from testes.llm_service.prompts import prompt1 as prompt
from testes.llm_service.questions import question2 as question
from testes.llm_service.queries import query1

# O histórico deve ser chamado no serviço?
history = None

model = LLMService(
    'google', 
    history = history
)


call_dict = {
    'knowledge_area': 'Ciências da Natureza',
    'question': question,
    'query': None,
 }


while True:
    print("\n" + "=" * 100 + "\n")
    call_dict['query'] = input("Digite a nova query: ")

    print("\n")
    # print(model.history)
    #print("\n")

    print(f"Resposta do modelo: {model.call_agent(**call_dict)}\n")
