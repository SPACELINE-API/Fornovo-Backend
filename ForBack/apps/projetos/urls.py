from django.urls import path
from . import views
from .views import cadastrarProjeto
from .views import uploadArquivo
app_name = 'projetos'

urlpatterns = [
    path('cadastrarProjeto', cadastrarProjeto.as_view(), name='cadastrarProjeto'),
    path('upload-arquivo', uploadArquivo.as_view(), name='upload-arquivo') # URL do Upload de Arquivo   
    # Exemplo: dominio.com/projetos/cadastrar/
    # path('cadastrar/', views.cadastrar_projeto, name='cadastrar'),
]