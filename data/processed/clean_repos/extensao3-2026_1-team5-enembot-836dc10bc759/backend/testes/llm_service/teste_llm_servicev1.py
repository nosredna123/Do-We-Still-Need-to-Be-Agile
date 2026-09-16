from testes.backups.llm_services.llm_servicev1 import LLMService

from testes.llm_service.prompts import prompt1
from testes.llm_service.questions import question2
from testes.llm_service.queries import query1


model = LLMService('meta')


# Dict para backup 1

call_dict = {
    'knowledge_area': 'Ciências da Natureza',
    'question': question2,
    # 'query': query1.format(item1 = 'B', item2 = 'E')
    'query': "Por que fluxo gênico é a resposta dessa questão?",
}

answer = model.call_agent(**call_dict)
print(answer)


