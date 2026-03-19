from django.urls import path
from . import views
from .views import criarUsuario
app_name = 'usuarios'

urlpatterns = [
    path('criarUsuario', criarUsuario.as_view(), name='criarUsuario')
    
    # Exemplo: dominio.com/projetos/cadastrar/
    # path('cadastrar/', views.cadastrar_projeto, name='cadastrar'),
]