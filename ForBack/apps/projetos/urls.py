from django.urls import path
from . import views
from .views import cadastrarProjeto, uploadArquivo, listarProjetos
app_name = 'projetos'

urlpatterns = [
    path('cadastrarProjeto', cadastrarProjeto.as_view(), name='cadastrarProjeto'),
    path('upload-arquivo', uploadArquivo.as_view(), name='upload-arquivo'), # URL do Upload de Arquivo
    path('listarProjetos', listarProjetos.as_view(), name='ListarProjetos')
]
