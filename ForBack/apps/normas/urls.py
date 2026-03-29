from django.urls import path
from .views import CriarNormaCompleta, AlterarStatusNorma, EditarDetsNorma, ListarNormas, VisualizarOuBaixarNorma

urlpatterns = [
    path('cadastrar', CriarNormaCompleta.as_view(), name='criar-norma-completa'), # POST - Norma
    path("status/<int:id_norma>", AlterarStatusNorma.as_view(), name='alterar-status-norma'), # UPDATE - Norma > Status
    path("buscar/<int:id_norma>", VisualizarOuBaixarNorma.as_view(), name='visualizar-baixar-norma'), # GET - Norma (OBS: É necessário usar ?downlaod=1 se for pra baixar e ?download=0 se for para visualização apenas)
    path("listarNormas", ListarNormas.as_view(), name='listar-normas'), # GET - Norma (Lista todas as normas)
    path("editarDetalhes/<int:id_norma>", EditarDetsNorma.as_view(), name='editar-detalhes-norma'), # PATCH - Norma (OBS: Reutiliza a mesma view de criação, mas usando o método PATCH e passando o id da norma a ser editada)
]
