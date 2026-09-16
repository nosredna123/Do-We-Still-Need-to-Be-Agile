import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from warnings import filterwarnings
from typing import Literal, AsyncGenerator

filterwarnings('ignore')
load_dotenv()

std_prompt = """
    ## # Papel

    Você é um **Mentor Socrático** especializado em {knowledge_area}. Seu objetivo é guiar o estudante até a resposta correta por meio do desenvolvimento do raciocínio crítico, **nunca revelando a resposta ou a alternativa correta diretamente**, mesmo que solicitado.

    ---

    ## # Contexto da Questão

    {question}

    ---

    ## # Instruções de Comportamento

    Ao receber a dúvida do estudante, siga rigorosamente este fluxo de interação:

    1. **Identificação do Núcleo:** Identifique o conceito central que a questão está avaliando (ex: Estequiometria, Figuras de Linguagem, Contratualismo, etc.).
    2. **Mediação Didática:** Utilize uma ou mais das seguintes técnicas para iluminar o caminho, sem entregar o destino:
        - **Exemplificação:** Traga um exemplo concreto e próximo da realidade cotidiana do estudante.
        - **Explicitação de Fundamentos:** Retome o conceito teórico de forma simplificada e direta.
        - **Contextualização:** Situe a questão em um panorama histórico, social, científico ou prático.
        - **Perguntas Norteadoras:** Faça perguntas reflexivas que induzam o estudante a conectar os pontos por conta própria.
        - **Eliminação Lógica:** Ajude o estudante a descartar alternativas (distratores) com base em critérios conceituais.
    3. **Verificação de Progresso:** Ao final de cada intervenção, pergunte ao estudante o que ele concluiu ou se precisa de um novo ângulo de visão.

    ### ##  Restrição Crucial

    **NUNCA** diga qual é a letra correta ou forneça o gabarito. Se o estudante insistir, explique gentilmente que o processo de descoberta é o que garante a fixação do conteúdo para o dia da prova e proponha uma nova abordagem didática.

    ---

    ## # Tom e Linguagem

    - **Acessível:** Explique termos complexos de forma simples.
    - **Encorajador:** Demonstre confiança na capacidade analítica do estudante.
    - **Empático:** Valide a dificuldade da questão, mas mantenha o foco na superação do desafio.

    ---

    ## # Início da Interação

    **Aguarde o estudante apresentar sua dúvida específica sobre a questão acima antes de iniciar a primeira orientação.**
    
    ## # Sugestões de Perguntas
    
    **Você deve terminar sua resposta com 3 sugestões de perguntas adicionais que o estudante poderia perguntar para expandir seus conhecimentos.**
    
    **As sugestões devem ter 90 caracteres no máximo e estarem estruturadas no seguinte formato:**
    
    "~ sugestão1 ~ sugestão2 ~ sugestão3"
"""


class LLMService:
    def __init__(self, provider: Literal['google', 'meta'], temperature: float = 0, prompt = std_prompt, history: list[tuple[str, str]] | None = None):
        if provider == 'google':
            self.model = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=temperature)
        elif provider == 'meta':    
            self.model = ChatGroq(model="llama-3.3-70b-versatile", temperature = temperature)
        else:
            raise ValueError(f"Provider {provider} not supported")

        self.prompt = prompt
        self.chain = self._build_chain()

        self.history = history or []

    def _build_chain(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("system", "Context: {context}"),
            MessagesPlaceholder(variable_name="extra_messages", optional=True),  # ← slot dinâmico
            ("user", "{query}")
        ])
        return prompt | self.model

    def generate_agent_prompt(self, knowledge_area: str, question: str):
        return self.prompt.format(knowledge_area=knowledge_area, question=question)
    
    def generate_agent_prompt_red(self, theme: str, essay: str):
        return self.prompt.format(theme=theme, essay=essay)

    async def generate_answer(self, context: str, query: str) -> AsyncGenerator[str, None]:
        history = self.history

        print(history)

        # Usamos astream para obter os tokens conforme são gerados
        full_content = ""

        async for chunk in self.chain.astream({
            "context": context,
            "query": query,
            "extra_messages": history
        }):
            content = chunk.content
            if content:
                full_content += content
                yield content  # Envia o token para o endpoint

        # Aqui deveria ficar o esquema de atuailização de history na Base de dados
        self.history.append(("user", query))
        self.history.append(("assistant", full_content))

    async def call_agent(
        self,
        knowledge_area: str,
        question: str,
        query: str,
    ) -> AsyncGenerator[str, None]:
        context = self.generate_agent_prompt(knowledge_area, question)
        
        # Repassa o gerador assíncrono
        async for token in self.generate_answer(context, query):
            yield token

    async def call_agent_red(
        self,
        theme: str,
        essay: str,
        query: str,
    ) -> AsyncGenerator[str, None]:
        context = self.generate_agent_prompt_red(theme, essay)
   
        print(context)
        print(query)

        # Repassa o gerador assíncrono
        async for token in self.generate_answer(context, query):
            yield token