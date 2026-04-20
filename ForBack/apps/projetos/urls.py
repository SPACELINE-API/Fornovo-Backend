from django.urls import path
from . import views
from .views import (
    VerificarStatusIA, cadastrarProjeto, deletarArquivo, uploadArquivo,
    listarProjetos, buscarArquivo, buscarProjeto, ProjetoDelete, ProjetoUpdate,
    verificarArquivo, AtualizarStatusProjeto,
    # SPACELINE-54: especificações geradas por IA
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

    # --- Especificações IA (SPACELINE-54) ---
    # CA.2 / CA.3: recebe um .docx, persiste em /media e salva no banco
    path('especificacoes/upload', UploadEspecificacao.as_view(), name='upload-especificacao'),
    # CA.4: retorna metadados ou o arquivo para download (?download=1)
    path('especificacoes/<int:id_especificacao>/', BaixarEspecificacao.as_view(), name='detalhes-especificacao'),
    # C.A 1 / C.A 2: Endpoint dedicado para download imediato
    path('especificacoes/<int:id_especificacao>/download/', DownloadEspecificacao.as_view(), name='download-especificacao'),
    # Atalho para baixar a última versão de um projeto
    path('<uuid:id_projeto>/especificacoes/latest/', DownloadUltimaEspecificacao.as_view(), name='download-ultima-especificacao'),
    # RN.1: lista especificações de um projeto específico
    path('<uuid:id_projeto>/especificacoes/', ListarEspecificacoes.as_view(), name='listar-especificacoes'),
]