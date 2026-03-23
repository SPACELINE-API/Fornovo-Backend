from django.urls import path
from .views import CriarNormaCompleta

urlpatterns = [
    path('cadastrar/', CriarNormaCompleta.as_view(), name='criar-norma-completa'),
]