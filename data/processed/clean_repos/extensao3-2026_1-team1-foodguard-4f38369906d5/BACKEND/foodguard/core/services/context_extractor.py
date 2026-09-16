import logging

import dspy
from django.conf import settings

from foodguard.core.services.ai_signatures import UpdateUserContext

logger = logging.getLogger('django')


def _clean_list(items) -> list[str]:
    if not items:
        return []
    return [i.strip() for i in items if isinstance(i, str) and i.strip()]


class ContextExtractorClient:
    """Modelo auxiliar (leve) que mantém a memória de fatos do usuário.

    Decide o que adicionar e o que remover do contexto a partir da mensagem.
    Roda em paralelo ao modelo principal. Usa `dspy.context(lm=...)` por chamada
    para não interferir na configuração global usada pelos outros clients.
    """

    def __init__(self):
        self._lm = dspy.LM(
            model=f"openai/{settings.CONTEXT_MODEL_NAME}",
            api_key=settings.OPENAI_API_KEY,
            temperature=0,
        )
        self._update = dspy.Predict(UpdateUserContext)

    def analyze(
        self,
        user_message: str,
        existing_anamnesis: str,
        existing_context: str,
    ) -> dict:
        """Retorna {'add': [...], 'remove': [...]} a aplicar ao contexto."""
        try:
            with dspy.context(lm=self._lm, adapter=dspy.JSONAdapter()):
                result = self._update(
                    user_message=user_message,
                    existing_anamnesis=existing_anamnesis or "Nenhuma.",
                    existing_context=existing_context or "Nenhum.",
                )
            return {
                "add": _clean_list(result.facts_to_add),
                "remove": _clean_list(result.facts_to_remove),
            }
        except Exception as e:
            logger.error("Falha na análise de contexto do usuário: %s", str(e), exc_info=True)
            return {"add": [], "remove": []}
