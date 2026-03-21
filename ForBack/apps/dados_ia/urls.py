from django.urls import path
from .views import CadastrarDadosExtraidos, CadastrarLogValidacao, CadastrarDadosManuais

app_name = 'dados_ia'

urlpatterns = [
    path('dados-extraidos/', CadastrarDadosExtraidos.as_view(), name='cadastrar_dados_extraidos'),
    path('log-validacao/', CadastrarLogValidacao.as_view(), name='cadastrar_log_validacao'),
    path('dados-manuais/', CadastrarDadosManuais.as_view(), name='cadastrar_dados_manuais'),
]