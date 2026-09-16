from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from foodguard.core.models.base import BaseModel
from foodguard.core.models.chat import Chat


class Message(BaseModel):
    class Role(models.TextChoices):
        USER = 'U', _('Usuário')
        ASSISTANT = 'A', _('Assistente')

    class Verdict(models.TextChoices):
        SAFE = 'SAFE', _('Seguro')
        LOW_CONCERN = 'LOW_CONCERN', _('Atenção leve')
        MODERATE_RISK = 'MODERATE_RISK', _('Risco moderado')
        HIGH_RISK = 'HIGH_RISK', _('Alto risco')
        INSUFFICIENT_DATA = 'INSUFFICIENT_DATA', _('Dados insuficientes')

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    role = models.CharField(
        max_length=1,
        choices=Role.choices
    )
    content = models.TextField(
        max_length=5000
    )
    # Veredito da avaliação de segurança (apenas em mensagens do assistente
    # geradas pelo pipeline de análise; null em mensagens de usuário e em
    # respostas conversacionais de acompanhamento).
    verdict = models.CharField(
        max_length=20,
        choices=Verdict.choices,
        blank=True,
        null=True,
    )
    # True quando a IA recomenda procurar um médico/nutricionista (mensagens do
    # assistente). Exibido como tag no chat.
    recommends_doctor = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        indexes = [
            models.Index(fields=['chat', 'created_at']),
        ]