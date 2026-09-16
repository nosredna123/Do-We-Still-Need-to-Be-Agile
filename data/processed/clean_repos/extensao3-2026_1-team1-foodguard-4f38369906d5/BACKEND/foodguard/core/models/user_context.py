from django.conf import settings
from django.db import models

from foodguard.core.models.base import BaseModel


class UserContext(BaseModel):
    """Janela de contexto acumulada do usuário.

    Guarda informações relevantes que o usuário mencionou no chat e que NÃO
    constam na anamnese (ex.: uma alergia informada em conversa). É preenchida
    por um modelo auxiliar e injetada no prompt do modelo principal.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="context",
    )
    # Fatos acumulados, um por linha.
    content = models.TextField(blank=True, default="")

    class Meta:
        # Nome de tabela próprio para não colidir com uma tabela `core_usercontext`
        # órfã (de outra branch) que possa existir no banco de desenvolvimento.
        db_table = "core_user_chat_context"
        verbose_name = "Contexto do usuário"
        verbose_name_plural = "Contextos dos usuários"

    def __str__(self):
        return f"Contexto de {self.user}"
