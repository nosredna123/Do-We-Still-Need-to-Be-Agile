from drf_spectacular.utils import extend_schema
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404

from foodguard.api.serializers.anamnese import AnamneseSerializer
from foodguard.core.models.anamnese import Anamnese
from foodguard.api.exceptions.anamnese import AnamneseHasAlreadyBeenCreatedException
from foodguard.core.models.chat import Chat

@extend_schema(summary="Cria uma anamnese para o usuário")
class AnamneseCreateView(CreateAPIView):
    serializer_class = AnamneseSerializer

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save(user=self.request.user)
        except IntegrityError:
            raise AnamneseHasAlreadyBeenCreatedException()

@extend_schema(summary="Recupera ou atualiza a anamnese do usuário")
class AnamneseGetUpdateView(RetrieveUpdateAPIView):
    serializer_class = AnamneseSerializer
    http_method_names = ['get', 'patch', 'options']

    def get_object(self):
        return get_object_or_404(Anamnese, user=self.request.user)

    def perform_update(self, serializer):
        with transaction.atomic():
            serializer.save()
            # RN004: fecha (somente leitura) os chats anteriores à atualização.
            # Eles continuam visíveis no histórico — apenas não recebem mensagens.
            Chat.objects.filter(
                user=self.request.user,
                created_at__lte=serializer.instance.updated_at,
            ).update(is_open=False)

