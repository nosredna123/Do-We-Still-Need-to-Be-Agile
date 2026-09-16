from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from foodguard.core.models.base import BaseModel


class Anamnese(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='anamnese'
    )
    previous_consultation = models.BooleanField(
        default=False, 
        verbose_name="Já fez consulta prévia com nutricionista?"
    )
    alcohol_intake = models.BooleanField(
        default=False, 
        verbose_name="Ingestão de Álcool"
    )
    smoking = models.BooleanField(
        default=False, 
        verbose_name="Fumo"
    )

    previous_consultation_objective = models.TextField(
        blank=True, null=True,
        max_length=5000,
        verbose_name="Qual era o objetivo na época?"
    )

    previous_consultation_result = models.TextField(
        blank=True, null=True, 
        max_length=5000,
        verbose_name="Obteve resultado? Se sim, qual?"
    )

    disease_history = models.TextField(
        blank=True, null=True, 
        max_length=5000,
        verbose_name="Histórico de doenças? Se sim, quais?"
    )

    medications = models.TextField(
        blank=True, null=True, 
        max_length=5000,
        verbose_name="Faz uso de algum medicamento? Se sim, qual?"
    )
    
    food_allergies = models.TextField(
        blank=True, null=True,
        max_length=5000,
        verbose_name="Possui alergia a algum alimento? Se sim, qual?"
    )

    food_intolerances = models.TextField(
        blank=True, null=True,
        max_length=5000,
        verbose_name="Tem intolerância a algum alimento? Se sim, qual?"
    )

    favorite_foods = models.TextField(
        max_length=5000,
        verbose_name="Alimentos que você gosta de comer e não podem faltar"
    )

    food_aversions = models.TextField(
        blank=True, null=True, 
        max_length=5000,
        verbose_name="Aversões/Tabus Alimentares/Alimentos que não gosta"
    )

    FEELING_CHOICES = [
        ('very_satisfied', 'Muito Satisfeito'),
        ('satisfied', 'Satisfeito'),
        ('indifferent', 'Indiferente'),
        ('dissatisfied', 'Insatisfeito'),
        ('very_dissatisfied', 'Muito Insatisfeito'),
    ]
    body_feeling = models.CharField(
        max_length=20,
        choices=FEELING_CHOICES,
        blank=True, null=True,
        verbose_name="Sentimento sobre o seu corpo e alimentação?"
    )

    VEGETARIAN_CHOICES = [
        ('not', 'Não'),
        ('vegetarian', 'Vegetariano(a)'),
        ('vegan', 'Vegano(a)'),
    ]
    eating_style = models.CharField(
        max_length=20,
        choices=VEGETARIAN_CHOICES,
        default='not',
        verbose_name="Estilo de alimentação"
    )

    class Meta:
        verbose_name = "Anamnese"
        verbose_name_plural = "Anamneses"

    def clean(self):
        if self.previous_consultation:
            if not self.previous_consultation_objective:
                raise ValidationError("O campo 'Qual era o objetivo na época?' é obrigatório quando 'Já fez consulta prévia com nutricionista?' é marcado como sim.")