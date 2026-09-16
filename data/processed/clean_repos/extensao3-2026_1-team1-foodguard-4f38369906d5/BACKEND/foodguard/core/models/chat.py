from django.conf import settings
from django.db import models

from foodguard.core.models.base import BaseModel


class Chat(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chats"
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default="Nova conversa"
    )
    # Chat "aberto" (pode receber mensagens). Fechado (False) quando a anamnese é
    # atualizada (RN004): permanece visível no histórico, mas só leitura.
    # OBS: distinto de `is_active` (BaseModel), que é usado para soft delete.
    is_open = models.BooleanField(default=True)
    # URL da imagem do produto escaneado (OpenFoodFacts), exibida no card da
    # galeria de chats. Null quando a conversa não teve produto com imagem.
    image_url = models.URLField(max_length=500, blank=True, null=True)
    # Severidade da conversa (cache desnormalizado): veredito da avaliação mais
    # recente do chat. Mesmos códigos de Message.Verdict. Usada para o badge e o
    # filtro por severidade na galeria. Sem `choices` aqui para evitar import
    # circular com message.py (que já importa Chat).
    severity = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
