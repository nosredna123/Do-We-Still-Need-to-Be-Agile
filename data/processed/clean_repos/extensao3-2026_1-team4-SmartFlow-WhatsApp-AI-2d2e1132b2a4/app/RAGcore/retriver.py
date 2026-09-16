from langchain_core.documents import Document

from app.RAGcore.knowledge_service import KnowledgeService


class KnowledgeRetriever:

    def __init__(self, ia_id: int):

        self.ia_id = ia_id
        self.knowledge_service = KnowledgeService()

    def invoke(self, query: str):

        results = self.knowledge_service.similarity_search(
            ia_id=self.ia_id,
            query=query,
            k=3
        )

        documents = []

        for content in results:

            documents.append(
                Document(
                    page_content=content
                )
            )

        return documents