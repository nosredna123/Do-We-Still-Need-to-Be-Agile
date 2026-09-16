from rest_framework.serializers import ModelSerializer, ValidationError

from foodguard.core.models.anamnese import Anamnese
from foodguard.api.exceptions.anamnese import AnamneseObjectiveRequiredException


class AnamneseSerializer(ModelSerializer):
    # Campos de texto obrigatórios (todos menos 'previous_consultation_result' e
    # os condicionais de consulta prévia, tratados à parte). Mensagem por campo.
    REQUIRED_TEXT_FIELDS = {
        'favorite_foods': 'Informe ao menos um alimento de preferência.',
        'food_allergies': 'Informe suas alergias alimentares (ou "Nenhuma").',
        'food_intolerances': 'Informe suas intolerâncias alimentares (ou "Nenhuma").',
        'disease_history': 'Informe seu histórico de doenças (ou "Nenhum").',
        'medications': 'Informe os medicamentos em uso (ou "Nenhum").',
        'food_aversions': 'Informe os alimentos que você não gosta (ou "Nenhum").',
    }

    class Meta:
        model = Anamnese
        fields = ['previous_consultation', 'alcohol_intake', 'smoking', 'previous_consultation_objective',
                  'previous_consultation_result', 'disease_history', 'medications', 'food_allergies',
                  'food_intolerances', 'favorite_foods', 'food_aversions', 'body_feeling', 'eating_style']

    def _resolve(self, attrs, field, default=None):
        """Valor enviado ou, em PATCH parcial, o já persistido na instância."""
        return attrs.get(field, getattr(self.instance, field, default))

    def validate(self, attrs):
        # Objetivo da consulta é obrigatório apenas quando houve consulta prévia.
        is_previous = self._resolve(attrs, 'previous_consultation', False)
        objective = self._resolve(attrs, 'previous_consultation_objective', '')
        if isinstance(objective, str):
            objective = objective.strip()
        if is_previous and not objective:
            raise AnamneseObjectiveRequiredException()

        # Demais campos obrigatórios (vale para create e para o PATCH parcial).
        errors = {}
        for field, message in self.REQUIRED_TEXT_FIELDS.items():
            value = self._resolve(attrs, field)
            if not (isinstance(value, str) and value.strip()):
                errors[field] = [message]

        feeling = self._resolve(attrs, 'body_feeling')
        if not feeling:
            errors['body_feeling'] = [
                'Selecione um sentimento sobre o seu corpo e alimentação.'
            ]

        if errors:
            raise ValidationError(errors)

        return attrs