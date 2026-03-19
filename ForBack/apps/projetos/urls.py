from django.urls import path
from . import views
from .views import cadastrarProjeto
app_name = 'projetos'

urlpatterns = [
    path('cadastrarProjeto', views.cadastrarProjeto, name='cadastrarProjeto')
    
    # Exemplo: dominio.com/projetos/cadastrar/
    # path('cadastrar/', views.cadastrar_projeto, name='cadastrar'),
]