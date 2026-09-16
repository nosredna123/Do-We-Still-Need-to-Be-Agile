from django.urls import path

from foodguard.api.views.chat import ChatListAPIView
from foodguard.api.views.chat import ChatDestroyAPIView

urlpatterns = [
    path('', ChatListAPIView.as_view(), name='list-chats'),
    path('<uuid:chat_id>/', ChatDestroyAPIView.as_view(), name='destroy-chat'),
]