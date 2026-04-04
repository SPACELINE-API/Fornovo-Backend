from django.urls import path
from .views import (
    CadastrarDadosExtraidos,
    CadastrarLogValidacao,
    CadastrarDadosManuais,
    ConsultarDadosProcessadosIA,
    ConverterArquivo,
    StatusMemCal,
    executarAgente,
    inserirNorma,
    GerarPlanilhaEletrica,
    GerarPlanilhaLevantamentoAPIView,
    ProcessarProjetoIA,
    GerarPlanilhaServicosPreliminaresAPIView,
    ExtrairDadosDXFAPIView,
    DebugEletricaView,
    MemorialCalculo,
    GerarPlanilhaMovimentoSolo,
    SalvarMemorialCalculo
)

app_name = 'dados_ia'

urlpatterns = [
    path('dados-extraidos', CadastrarDadosExtraidos.as_view(), name='cadastrar_dados_extraidos'),
    path('log-validacao', CadastrarLogValidacao.as_view(), name='cadastrar_log_validacao'),
    path('dados-manuais', CadastrarDadosManuais.as_view(), name='cadastrar_dados_manuais'),
    path('dwg-dxf', ConverterArquivo.as_view(), name='converter_arquivo'),
    path('processar-ia', ProcessarProjetoIA.as_view(), name='processar_projeto_ia'),
    path('executar-agente', executarAgente.as_view(), name='executar-agente'),
    path('inserir-norma', inserirNorma.as_view(), name='inserir-norma'),
    path('planilha-eletrica', GerarPlanilhaEletrica.as_view(), name='planilha-eletrica'),
    path('gerar-levantamento', GerarPlanilhaLevantamentoAPIView.as_view(), name='memorial-calculo'),
    path('gerar-servicos_preliminares', GerarPlanilhaServicosPreliminaresAPIView.as_view(), name='servicos_preliminares'),
    path('extrair-dados-dxf', ExtrairDadosDXFAPIView.as_view(), name='extrair_dados_dxf'),
    path('debug-eletrica', DebugEletricaView.as_view(), name='debug_eletrica'),
    path('memorial-calculo', MemorialCalculo.as_view(), name='memorial-calculo'),
    path('movimento-solo', GerarPlanilhaMovimentoSolo.as_view(), name='movimento-solo'),
    path('salvar-memorial', SalvarMemorialCalculo.as_view(), name='salvar-memorial-calculo'),
    path('status-memorial/', StatusMemCal.as_view(), name='status-memorial-calculo'),
    path('dados-processados/<uuid:projeto_id>', ConsultarDadosProcessadosIA.as_view(), name='consultar_dados_ia'),
]
