from django.urls import path
from .views import (
    CadastrarDadosExtraidos,
    CadastrarLogValidacao,
    CadastrarDadosManuais,
    ConsultarDadosProcessadosIA,
    ConverterArquivo,
    StatusMemCal,
    inserirNorma,
    ProcessarProjetoIA,
    ExtrairDadosDXFAPIView,
    MemorialCalculo,
    SalvarMemorialCalculo,
    ativarNorma,
    DownloadRelatorio,
    StatusRelatorio
)

app_name = 'dados_ia'

urlpatterns = [
    path('dados-extraidos', CadastrarDadosExtraidos.as_view(), name='cadastrar_dados_extraidos'),
    path('log-validacao', CadastrarLogValidacao.as_view(), name='cadastrar_log_validacao'),
    path('dados-manuais', CadastrarDadosManuais.as_view(), name='cadastrar_dados_manuais'),
    path('dwg-dxf', ConverterArquivo.as_view(), name='converter_arquivo'),
    path('processar-ia', ProcessarProjetoIA.as_view(), name='processar_projeto_ia'),
    path('inserir-norma/<int:id>', inserirNorma.as_view(), name='inserir-norma'),
    path('inserir-norma', inserirNorma.as_view()),
    path('ativar-norma/<int:id>', ativarNorma.as_view()),
    path('extrair-dados-dxf', ExtrairDadosDXFAPIView.as_view(), name='extrair_dados_dxf'),
    path('memorial-calculo', MemorialCalculo.as_view(), name='memorial-calculo'),
    path('salvar-memorial', SalvarMemorialCalculo.as_view(), name='salvar-memorial-calculo'),
    path('status-memorial/', StatusMemCal.as_view(), name='status-memorial-calculo'),
    path('dados-processados/<uuid:projeto_id>', ConsultarDadosProcessadosIA.as_view(), name='consultar_dados_ia'),
    path('download-relatorio', DownloadRelatorio.as_view(), name='download-relatorio'),
    path('status-relatorio', StatusRelatorio.as_view(), name='status-relatorio')
]
