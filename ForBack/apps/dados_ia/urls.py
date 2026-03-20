from django.urls import path
from . import views
app_name = 'dados_ia'

urlpatterns = [
    path('', views.index, name='index'), 
    
    # Exemplo: dominio.com/dados_ia/estruturas/
    # path('estruturas/', views.estruturas, name='estruturas'),
]