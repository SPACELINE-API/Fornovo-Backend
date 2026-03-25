from django.urls import path
from .views import CriarNormaCompleta, AlterarStatusNorma

urlpatterns = [
    path('cadastrar', CriarNormaCompleta.as_view(), name='criar-norma-completa'), # POST - Norma
    path("<int:id_norma>/status", AlterarStatusNorma.as_view(), name='alterar-status-norma'), # UPDATE - Norma > Status
]
