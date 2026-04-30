from django.urls import path
from . import views
from .views import (
    VerificarStatusIA, cadastrarProjeto, deletarArquivo, uploadArquivo,
    listarProjetos, buscarArquivo, buscarProjeto, ProjetoDelete, ProjetoUpdate,
    verificarArquivo, AtualizarStatusProjeto,
    UploadEspecificacao, BaixarEspecificacao, ListarEspecificacoes,
    DownloadEspecificacao, DownloadUltimaEspecificacao,
)

app_name = 'projetos'

urlpatterns = [
    path('cadastrarProjeto', cadastrarProjeto.as_view(), name='cadastrarProjeto'),
    path('upload-arquivo', uploadArquivo.as_view(), name='upload-arquivo'),
    path('listarProjetos', listarProjetos.as_view(), name='ListarProjetos'),
    path('buscarArquivo/<str:projeto_id>', buscarArquivo.as_view(), name='buscarArquivo'),
    path('buscarProjeto/<str:id_projeto>/', buscarProjeto.as_view()),
    path('deletarProjeto/<uuid:id_projeto>', ProjetoDelete.as_view(), name='deletarProjeto'),
    path('atualizarProjeto/<uuid:id_projeto>', ProjetoUpdate.as_view(), name='atualizarProjeto'),
    path('verificarArquivo/<uuid:id_projeto>', verificarArquivo.as_view(), name='verificar_arquivo'),
    path('deletarArquivo/<int:id>', deletarArquivo.as_view(), name='deletarArquivo'),
    path('statusIa/<uuid:id_projeto>', VerificarStatusIA.as_view(), name='statusIA'),
    path('atualizarStatus/<uuid:id_projeto>', AtualizarStatusProjeto.as_view(), name='atualizarStatusProjeto'),
    path('especificacoes/upload', UploadEspecificacao.as_view(), name='upload-especificacao'),
    path('especificacoes/<int:id_especificacao>/', BaixarEspecificacao.as_view(), name='detalhes-especificacao'),
    path('especificacoes/<int:id_especificacao>/download/', DownloadEspecificacao.as_view(), name='download-especificacao'),
    path('<uuid:id_projeto>/especificacoes/latest/', DownloadUltimaEspecificacao.as_view(), name='download-ultima-especificacao'),
    path('<uuid:id_projeto>/especificacoes/', ListarEspecificacoes.as_view(), name='listar-especificacoes'),
]
