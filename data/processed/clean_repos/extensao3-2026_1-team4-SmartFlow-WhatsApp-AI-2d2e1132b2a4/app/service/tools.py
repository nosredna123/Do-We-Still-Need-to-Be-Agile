from langchain_core.tools import tool
from pathlib import Path




def create_knowledge_tool(retriever):

    @tool("buscar_base_conhecimento")
    def buscar_base_conhecimento(query: str) -> str:
        """
        Use esta ferramenta SOMENTE quando precisar consultar
        informações específicas que podem existir na base de conhecimento.

        A base pode conter:
        - documentos enviados
        - políticas internas
        - informações empresariais
        - regras de negócio
        - produtos e serviços
        - informações privadas da empresa

        NÃO use esta ferramenta para:
        - cumprimentos
        - conversas casuais
        - respostas simples
        - opiniões gerais
        - perguntas que podem ser respondidas sem contexto externo

        Sempre prefira usar esta ferramenta para perguntas factuais,
        técnicas ou específicas da empresa.
        """

        try:

            docs = retriever.invoke(query)

            if not docs:
                return (
                    "Nenhuma informação relevante foi encontrada "
                    "na base de conhecimento."
                )

            context = []

            for i, doc in enumerate(docs, start=1):

                content = doc.page_content.strip()

                if not content:
                    continue

                context.append(
                    f"[Documento {i}]\n{content}"
                )

            if not context:
                return (
                    "Os documentos encontrados estavam vazios "
                    "ou inválidos."
                )

            return "\n\n".join(context)

        except Exception as ex:

            print(f"Erro na tool de conhecimento: {ex}")

            return (
                "Ocorreu um erro ao consultar "
                "a base de conhecimento."
            )

    return buscar_base_conhecimento

from pathlib import Path
from langchain_core.tools import tool


from pathlib import Path

def create_feedback_tool(ia_id: int):

    @tool("mandar_feedback")
    def mandar_feedback(feedback: str) -> str:
        """
        Use essa ferramenta quando não souber responder
        ou quando faltarem informações para responder.
        """

        try:
            feedback_dir = Path("feedbacks")
            feedback_dir.mkdir(exist_ok=True)

            feedback_file = feedback_dir / f"ia_{ia_id}.txt"

            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write(feedback.strip() + "\n")

            return "Feedback registrado."

        except Exception as ex:
            print(f"Erro ao salvar feedback: {ex}")
            return "Erro ao registrar feedback."

    return mandar_feedback