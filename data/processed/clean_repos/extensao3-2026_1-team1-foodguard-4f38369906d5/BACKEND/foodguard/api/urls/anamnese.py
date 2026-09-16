from django.urls import path

from foodguard.api.views.anamnese import AnamneseCreateView
from foodguard.api.views.anamnese import AnamneseGetUpdateView


urlpatterns = [
    path('', AnamneseCreateView.as_view(), name='create-anamnese'),
    path('me/', AnamneseGetUpdateView.as_view(), name='get-or-update-anamnese'),
]