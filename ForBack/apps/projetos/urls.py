from django.urls import path
from . import views
from .views import cadastrarProjeto, deletarArquivo, uploadArquivo, listarProjetos, buscarArquivo, buscarProjeto, ProjetoDelete, ProjetoUpdate, verificarArquivo
app_name = 'projetos'

urlpatterns = [
    path('cadastrarProjeto', cadastrarProjeto.as_view(), name='cadastrarProjeto'),
    path('upload-arquivo', uploadArquivo.as_view(), name='upload-arquivo'), # URL do Upload de Arquivo
    path('listarProjetos', listarProjetos.as_view(), name='ListarProjetos'),
    path('buscarArquivo/<str:projeto_id>', buscarArquivo.as_view(), name='buscarArquivo'),
    path('buscarProjeto/<str:id_projeto>/', buscarProjeto.as_view()),
    path('deletarProjeto/<uuid:id_projeto>', ProjetoDelete.as_view(), name='deletarProjeto'),
    path('atualizarProjeto/<uuid:id_projeto>', ProjetoUpdate.as_view(), name='atualizarProjeto'),
    path('verificarArquivo/<uuid:id_projeto>', verificarArquivo.as_view(), name='verificar_arquivo'),
    path('deletar-arquivo/<int:id>', deletarArquivo.as_view()),
]
