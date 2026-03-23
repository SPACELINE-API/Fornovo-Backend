from django.urls import path
from .views import CadastrarDadosExtraidos, CadastrarLogValidacao, CadastrarDadosManuais, ConverterArquivo

app_name = 'dados_ia'

urlpatterns = [
    path('dados-extraidos/', CadastrarDadosExtraidos.as_view(), name='cadastrar_dados_extraidos'),
    path('log-validacao/', CadastrarLogValidacao.as_view(), name='cadastrar_log_validacao'),
    path('dados-manuais/', CadastrarDadosManuais.as_view(), name='cadastrar_dados_manuais'),
    path('dwg-dxf/', ConverterArquivo.as_view(), name='converter_arquivo')
]
