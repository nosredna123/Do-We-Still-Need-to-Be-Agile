from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView
from rest_framework.generics import DestroyAPIView

from foodguard.api.serializers.chat import ChatSerializer
from foodguard.core.models.chat import Chat

@extend_schema(summary="Lista chats do usuário")
class ChatListAPIView(ListAPIView):
    serializer_class = ChatSerializer

    def get_queryset(self):
        # Mostra todos os chats não-deletados (is_active=True), abertos e
        # fechados. Os fechados (is_open=False) aparecem no histórico em modo
        # somente leitura.
        return (
            Chat.objects.filter(user=self.request.user, is_active=True)
            .order_by('-created_at')
        )

@extend_schema(summary="Deleta (soft delete) um chat específico do usuário")
class ChatDestroyAPIView(DestroyAPIView):
    serializer_class = ChatSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'chat_id'

    def get_queryset(self):
        return Chat.objects.filter(user=self.request.user, is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=['is_active'])