from django.urls import path
from . import views
app_name = 'calculos'

urlpatterns = [
    path('', views.index, name='index'), 
    
    # Exemplo: dominio.com/projetos/cadastrar/
    # path('cadastrar/', views.cadastrar_projeto, name='cadastrar'),c
]