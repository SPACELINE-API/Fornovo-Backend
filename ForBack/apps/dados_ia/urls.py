from django.urls import path
from .views import (
    ConsultarDadosProcessadosIA,
    ConverterArquivo,
    StatusMemCal,
    inserirNorma,
    ProcessarProjetoIA,
    SalvarMemorialCalculo,
    SalvarEspecificacao,
    StatusEspecificacao,
    ativarNorma,
    DownloadRelatorio,
    StatusRelatorio,
    historicoRelatorio,
    ConformidadeIAView,
)

app_name = 'dados_ia'

urlpatterns = [
    path('dwg-dxf', ConverterArquivo.as_view(), name='converter_arquivo'),
    path('processar-ia', ProcessarProjetoIA.as_view(), name='processar_projeto_ia'),
    path('inserir-norma/<int:id>', inserirNorma.as_view(), name='inserir-norma'),
    path('inserir-norma', inserirNorma.as_view()),
    path('ativar-norma/<int:id>', ativarNorma.as_view()),
    path('salvar-memorial', SalvarMemorialCalculo.as_view(), name='salvar-memorial-calculo'),
    path('status-memorial/', StatusMemCal.as_view(), name='status-memorial-calculo'),
    path('salvar-especificacao', SalvarEspecificacao.as_view(), name='salvar-especificacao'),
    path('status-especificacao/', StatusEspecificacao.as_view(), name='status-especificacao'),
    path('dados-processados/<uuid:projeto_id>', ConsultarDadosProcessadosIA.as_view(), name='consultar_dados_ia'),
    path('download-relatorio', DownloadRelatorio.as_view(), name='download-relatorio'),
    path('status-relatorio', StatusRelatorio.as_view(), name='status-relatorio'),
    path('historico-relatorio', historicoRelatorio.as_view(), name = 'historico-relatorio'),
    path('conformidade/', ConformidadeIAView.as_view(), name='conformidade-ia'),
]
