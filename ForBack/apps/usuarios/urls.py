from django.urls import path
from . import views
from .views import cadastrarProjeto
app_name = 'usuarios'

urlpatterns = [
    path('criarUsuario', views.criarUsuario, name='criarUsuario')
    
    # Exemplo: dominio.com/projetos/cadastrar/
    # path('cadastrar/', views.cadastrar_projeto, name='cadastrar'),
]