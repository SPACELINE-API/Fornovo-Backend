from django.urls import path
from .views import CriarNormaCompleta, AlterarStatusNorma, EditarDetsNorma, ListarNormas, VisualizarOuBaixarNorma

urlpatterns = [
    path('cadastrar', CriarNormaCompleta.as_view(), name='criar-norma-completa'), 
    path("status/<int:id_norma>", AlterarStatusNorma.as_view(), name='alterar-status-norma'), 
    path("buscar/<int:id_norma>", VisualizarOuBaixarNorma.as_view(), name='visualizar-baixar-norma'), 
    path("listarNormas", ListarNormas.as_view(), name='listar-normas'),
    path("editarDetalhes/<int:id_norma>", EditarDetsNorma.as_view(), name='editar-detalhes-norma'),
]
