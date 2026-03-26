from django.urls import path
from .views import CriarNormaCompleta, AlterarStatusNorma, VisualizarOuBaixarNorma

urlpatterns = [
    path('cadastrar', CriarNormaCompleta.as_view(), name='criar-norma-completa'), # POST - Norma
    path("status/<int:id_norma>", AlterarStatusNorma.as_view(), name='alterar-status-norma'), # UPDATE - Norma > Status
    path("buscar/<int:id_norma>", VisualizarOuBaixarNorma.as_view(), name='visualizar-baixar-norma'), # GET - Norma (OBS: É necessário usar ?downlaod=1 se for pra baixar e ?download=0 se for para visualização apenas)
]
