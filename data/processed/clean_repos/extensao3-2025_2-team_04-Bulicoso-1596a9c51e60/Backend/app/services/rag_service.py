"""
🔹 SERVIÇO RAG - Pipeline de Recuperação e Geração Aumentada

Este é o núcleo de IA do sistema. Implementa o pipeline RAG completo:

1. Busca contexto relevante no ChromaDB (vetorização)
2. Recupera chunks relacionados ao medicamento
3. Envia contexto + prompt ao Gemini API
4. Retorna texto simplificado e acessível

IMPLEMENTAÇÃO NECESSÁRIA:
- Configurar LangChain retriever com ChromaDB
- Implementar busca semântica de chunks
- Criar prompts otimizados para simplificação
- Integrar com Gemini API via LangChain
- Tratamento de erros e fallback para web scraping
"""

from typing import Optional
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from app.core.config import settings
from app.core.logger import setup_logger
from app.services.scraper_service import ScraperService

logger = setup_logger()


class RAGService:
    """
    Serviço RAG para simplificação de bulas de medicamentos.
    
    Responsabilidades:
    - Buscar bulas no ChromaDB
    - Recuperar contexto relevante
    - Gerar texto simplificado via Gemini
    """
    
    def __init__(self, chroma_client=None):
        """
        Inicializa o serviço RAG.
        
        Args:
            chroma_client: Cliente ChromaDB (opcional)
        """
        self.chroma_client = chroma_client
        self.scraper_service = ScraperService()
        
        # TODO: Inicializar LangChain components
        # - Vector store (Chroma)
        # - LLM (ChatGoogleGenerativeAI)
        # - Retriever
        # - Chain (RetrievalQA)
        
        logger.info("RAGService inicializado")
    
    
    async def simplify_medication_info(self, medication_name: str) -> str:
        """
        🔹 IMPLEMENTAR: Simplifica a bula de um medicamento.
        
        Fluxo:
        1. Buscar no ChromaDB usando embedding do nome do medicamento
        2. Se não encontrar, buscar na web via scraper_service
        3. Recuperar chunks relevantes (top-k)
        4. Construir prompt com contexto + instruções de simplificação
        5. Chamar Gemini API para gerar texto simplificado
        6. Retornar resultado
        
        Args:
            medication_name: Nome do medicamento
            
        Returns:
            Texto simplificado da bula
        """
        logger.info(f"Simplificando bula para: {medication_name}")
        
        try:
            # TODO: Passo 1 - Buscar no ChromaDB
            # vector_store = Chroma(
            #     client=self.chroma_client,
            #     collection_name=settings.CHROMA_COLLECTION_NAME,
            #     embedding_function=embedding_function
            # )
            # retriever = vector_store.as_retriever(search_kwargs={"k": 5})
            # docs = retriever.get_relevant_documents(medication_name)
            
            # TODO: Passo 2 - Se não encontrar, buscar na web
            # if not docs:
            #     logger.info("Bula não encontrada no ChromaDB, buscando na web...")
            #     web_content = await self.scraper_service.fetch_medication_info(medication_name)
            #     # Vetorizar e adicionar ao ChromaDB para próximas buscas
            #     # await vector_service.add_document(medication_name, web_content)
            
            # TODO: Passo 3 - Construir prompt de simplificação
            # prompt_template = PromptTemplate(
            #     input_variables=["context", "medication_name"],
            #     template="""
            #     Você é um assistente especializado em simplificar bulas de medicamentos
            #     para idosos. Simplifique o seguinte texto técnico, tornando-o claro e
            #     acessível, mantendo informações essenciais sobre:
            #     - Para que serve
            #     - Como tomar
            #     - Cuidados e efeitos colaterais importantes
            #     - Quando não tomar
            #     
            #     Medicamento: {medication_name}
            #     Bula original: {context}
            #     
            #     Texto simplificado:
            #     """
            # )
            
            # TODO: Passo 4 - Chamar Gemini API
            # llm = ChatGoogleGenerativeAI(
            #     model=settings.LLM_MODEL,
            #     google_api_key=settings.GOOGLE_API_KEY,
            #     temperature=0.7
            # )
            # chain = RetrievalQA.from_chain_type(
            #     llm=llm,
            #     chain_type="stuff",
            #     retriever=retriever,
            #     return_source_documents=True
            # )
            # result = chain({"query": f"Simplifique a bula de {medication_name}"})
            
            # Por enquanto, retorna placeholder
            return f"""
            [IMPLEMENTAR] Bula simplificada para {medication_name}
            
            Esta função deve:
            1. Buscar a bula no ChromaDB
            2. Se não encontrar, buscar na web
            3. Usar LangChain + Gemini para simplificar
            4. Retornar texto acessível
            """
            
        except Exception as e:
            logger.error(f"Erro no RAG service: {str(e)}")
            raise
    
    
    async def search_medication_context(self, medication_name: str, top_k: int = 5):
        """
        🔹 IMPLEMENTAR: Busca contexto relevante sobre um medicamento.
        
        Args:
            medication_name: Nome do medicamento
            top_k: Número de chunks a retornar
            
        Returns:
            Lista de documentos relevantes
        """
        # TODO: Implementar busca semântica no ChromaDB
        pass

