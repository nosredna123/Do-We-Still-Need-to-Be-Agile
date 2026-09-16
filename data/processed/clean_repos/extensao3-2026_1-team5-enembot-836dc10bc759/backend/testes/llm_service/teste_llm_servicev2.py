from testes.backups.llm_services.llm_servicev2 import LLMService

from testes.llm_service.prompts import prompt1
from testes.llm_service.questions import question2
from testes.llm_service.queries import query1


model = LLMService('meta')

call_dict = {
    # Dict para backup 2

    'knowledge_area': 'Ciências da Natureza',
    'question': question2,
    # 'query': query1.format(item1 = 'B', item2 = 'E')
    'query': "Por que fluxo gênico é a resposta dessa questão?",
    'extra_messages': [
        ("system", "Por que os corredores permitem que seres vivos da mesma espécie em diferentes ambientes consigam se reproduzir"),
        ("user", "Pode dar exemplos reais de corredores gênicos?")
    ]
}


answer = model.call_agent(**call_dict)
print(answer)

