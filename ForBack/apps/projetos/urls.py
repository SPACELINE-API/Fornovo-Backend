from django.urls import path
from . import views
from .views import cadastrarProjeto, uploadArquivo, listarProjetos, buscarArquivo, buscarProjeto
app_name = 'projetos'

urlpatterns = [
    path('cadastrarProjeto', cadastrarProjeto.as_view(), name='cadastrarProjeto'),
    path('upload-arquivo', uploadArquivo.as_view(), name='upload-arquivo'), # URL do Upload de Arquivo
    path('listarProjetos', listarProjetos.as_view(), name='ListarProjetos'),
    path('buscarArquivo/<str:projeto_id>', buscarArquivo.as_view(), name='buscarArquivo'),
    path('buscarProjeto/<str:id_projeto>/', buscarProjeto.as_view())
]
