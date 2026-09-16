from django.urls import path

from foodguard.api.views.message import MessageCreateAPIView
from foodguard.api.views.message import MessageListAPIView


urlpatterns = [
    path('message/send/', MessageCreateAPIView.as_view(), name='send-message'),
    path('<uuid:chat_id>/messages/', MessageListAPIView.as_view(), name='list-messages'),
]