from django.urls import path
from django.urls import include

urlpatterns = [
    path('auth/', include('foodguard.users.urls')),
    path('chats/', include('foodguard.api.urls.message')),
    path('chats/', include('foodguard.api.urls.chat')),
    path('anamnese/', include('foodguard.api.urls.anamnese')),
]