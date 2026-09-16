import logging

import dspy
from django.conf import settings

from foodguard.core.services.ai_signatures import (
    AssessFoodSafety,
    FoodSafetyAssessment,
    FoodSafetyFollowUp,
)

logger = logging.getLogger('django')


class OpenAIClient:
    """
    Client de IA do FoodGuard apoiado em OpenAI (via DSPy/litellm).

    Suporta dois modos:
      - assess_safety: primeira interação — avaliação estruturada de segurança
        alimentar (mesmo contrato do GeminiClient, drop-in).
      - continue_conversation: turnos seguintes — resposta conversacional de
        acompanhamento, contextualizada pelo histórico do chat.

    Usa dspy.context(lm=...) por chamada em vez de dspy.configure global, para
    coexistir com outros clients/LMs sem conflito de estado global.
    """

    def __init__(self):
        self._lm = dspy.LM(
            model=f"openai/{settings.OPENAI_MODEL_NAME}",
            api_key=settings.OPENAI_API_KEY,
            temperature=settings.OPENAI_TEMPERATURE,
        )
        self._assess = dspy.ChainOfThought(AssessFoodSafety)
        self._follow_up = dspy.ChainOfThought(FoodSafetyFollowUp)

    def assess_safety(
        self,
        user_anamnesis: str,
        food_ingredients: str,
        user_query: str,
    ) -> dict:
        try:
            with dspy.context(lm=self._lm, adapter=dspy.JSONAdapter()):
                result = self._assess(
                    user_anamnesis=user_anamnesis,
                    food_ingredients=food_ingredients,
                    user_query=user_query,
                )

            assessment: FoodSafetyAssessment = result.assessment

            logger.debug(
                "DSPy ChainOfThought rationale (assess): %s",
                getattr(result, "rationale", "N/A"),
            )

            return {
                "rationale": getattr(result, "rationale", ""),
                "verdict": assessment.verdict,
                "explanation": assessment.explanation,
                "recommends_doctor": assessment.recommends_doctor,
            }
        except Exception as e:
            logger.error("Erro no pipeline DSPy (OpenAI assess): %s", str(e), exc_info=True)
            raise

    def continue_conversation(
        self,
        user_anamnesis: str,
        food_context: str,
        history: dspy.History,
        user_query: str,
    ) -> dict:
        try:
            with dspy.context(lm=self._lm, adapter=dspy.JSONAdapter()):
                result = self._follow_up(
                    user_anamnesis=user_anamnesis,
                    food_context=food_context,
                    history=history,
                    user_query=user_query,
                )

            logger.debug(
                "DSPy ChainOfThought rationale (follow-up): %s",
                getattr(result, "rationale", "N/A"),
            )

            return {
                "response": result.answer,
                "recommends_doctor": result.recommends_doctor,
            }
        except Exception as e:
            logger.error(
                "Erro no pipeline DSPy (OpenAI follow-up): %s", str(e), exc_info=True
            )
            raise
