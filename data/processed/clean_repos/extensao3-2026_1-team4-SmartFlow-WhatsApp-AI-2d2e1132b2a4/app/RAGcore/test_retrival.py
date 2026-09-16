
from app.RAGcore.knowledge_service import KnowledgeService 
service = KnowledgeService()

resultado = service.similarity_search(
    ia_id=3,
    query="Qual a data de criacao do RU?"
)

print(resultado)