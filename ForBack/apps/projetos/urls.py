from django.urls import path
from . import views
from .views import cadastrarProjeto, uploadArquivo, listarProjetos, buscarArquivo, ProjetoDelete, ProjetoUpdate
app_name = 'projetos'

urlpatterns = [
    path('cadastrarProjeto', cadastrarProjeto.as_view(), name='cadastrarProjeto'),
    path('upload-arquivo', uploadArquivo.as_view(), name='upload-arquivo'), # URL do Upload de Arquivo
    path('listarProjetos', listarProjetos.as_view(), name='ListarProjetos'),
    path('buscarArquivo/<int:id_arquivo>', buscarArquivo.as_view(), name='buscarArquivo'),
    path('deletarProjeto/<uuid:id_projeto>', ProjetoDelete.as_view(), name='deletarProjeto'),
    path('atualizarProjeto/<uuid:id_projeto>', ProjetoUpdate.as_view(), name='atualizarProjeto'),
]
    