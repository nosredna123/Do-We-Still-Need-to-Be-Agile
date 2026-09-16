import logging

import dspy
from django.conf import settings

from foodguard.core.services.ai_signatures import AssessFoodSafety, FoodSafetyAssessment

logger = logging.getLogger('django')


class GeminiClient:
    def __init__(self):
        self._lm = dspy.LM(
            model="gemini/gemini-2.5-flash",
            api_key=settings.GEMINI_API_KEY,
            temperature=settings.GEMINI_TEMPERATURE,
        )
        self._chain = dspy.ChainOfThought(AssessFoodSafety)

    def assess_safety(
        self,
        user_anamnesis: str,
        food_ingredients: str,
        user_query: str,
    ) -> dict:
        try:
            # dspy.context por chamada em vez de dspy.configure global, para não
            # sobrescrever a config de outros clients em ambiente multi-thread.
            with dspy.context(lm=self._lm, adapter=dspy.JSONAdapter()):
                result = self._chain(
                    user_anamnesis=user_anamnesis,
                    food_ingredients=food_ingredients,
                    user_query=user_query,
                )

            assessment: FoodSafetyAssessment = result.assessment

            logger.debug(
                "DSPy ChainOfThought rationale: %s",
                getattr(result, "rationale", "N/A"),
            )

            return {
                "rationale": getattr(result, "rationale", ""),
                "verdict": assessment.verdict,
                "explanation": assessment.explanation,
                "recommends_doctor": assessment.recommends_doctor,
            }
        except Exception as e:
            logger.error("Erro no pipeline DSPy: %s", str(e), exc_info=True)
            raise
