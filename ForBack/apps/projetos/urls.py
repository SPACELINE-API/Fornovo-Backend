from django.urls import path
from . import views
app_name = 'projetos'

urlpatterns = [
    path('', views.index, name='index'), 
    
    # Exemplo: dominio.com/projetos/cadastrar/
    # path('cadastrar/', views.cadastrar_projeto, name='cadastrar'),
]