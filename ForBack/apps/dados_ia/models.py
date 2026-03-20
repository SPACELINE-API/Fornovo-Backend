import zlib
import json
from django.db import models
from apps.projetos.models import Projeto, Norma

# Create your models here.

'''
Descrição do problema:
Modelar e implementar as tabelas de banco de dados específicas para o módulo de Inteligência Artificial.

O que deve ser feito:
- Criar todas as tabelas necessárias para a funcionalidade da IA.
- Vincular cada elemento extraído ao arquivo CAD de origem para garantir a rastreabilidade.
- Adicionar índices nos campos de id do projeto para acelerar a recuperação dos dados durante a geração do memorial.
'''

class ArquivoDXF(models.Model):
    """
    Objetivo: Armazenar a referência aos arquivos originais (DXF/CAD) submetidos.
    Recebe: O ID do projeto vinculado, o nome do arquivo, seu caminho no servidor e o status de processamento.
    Uso: Serve como uma base de dados para a IA realizar a analise desses dados e gerar o memorial de calculo.
    """
    id_arquivo = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )
    nome_arquivo = models.CharField(max_length=255)
    caminho_arquivo = models.CharField(max_length=500)
    data_upload = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pendente")

    class Meta:
        db_table = "arquivos_dxf"

class DadosExtraidos(models.Model):
    """
    Objetivo: Armazenar o resultado da extração pesada de coordenadas e geometrias.
    Recebe: O ID do arquivo DXF de origem e uma estrutura complexa de dados (JSON).
    Uso: Para economizar espaço, os dados são comprimidos com zlib antes de serem salvos no banco.
    """
    id_dados = models.AutoField(primary_key=True)
    arquivo = models.ForeignKey(
        ArquivoDXF,
        on_delete=models.CASCADE,
        db_column="arquivo_id"
    )
    
    # Campo binário para armazenar o JSON comprimido (mais leve que texto puro)
    dados_binarios = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = "dados_extraidos"

    @property
    def dados(self):
        """Propriedade para acessar os dados descomprimidos automaticamente."""
        if not self.dados_binarios:
            return None
        return json.loads(zlib.decompress(self.dados_binarios).decode('utf-8'))

    @dados.setter
    def dados(self, value):
        """Seta os dados comprimindo-os para zlib antes de salvar no banco."""
        if value:
            self.dados_binarios = zlib.compress(json.dumps(value).encode('utf-8'))
        else:
            self.dados_binarios = None

class LogValidacao(models.Model):
    """
    Objetivo: Registrar o histórico de auditoria da IA sobre o projeto.
    Recebe: Vínculo com o projeto, a norma aplicada (NBR) e o resultado da validação (JSON).
    Uso: Permite ao usuário ver por que a IA aprovou ou reprovou certos elementos técnicos.
    """
    id_log = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )
    norma = models.ForeignKey(
        Norma,
        on_delete=models.CASCADE,
        db_column="norma_id"
    )
    dados = models.JSONField()

    class Meta:
        db_table = "logs_validacao"

class DadosInseridosManualmente(models.Model):
    """
    Objetivo: Armazenar ajustes e dados técnicos fornecidos diretamente pelo usuário.
    Recebe: Vínculo com o projeto e os dados customizados (JSON).
    Uso: Essencial para garantir que a vontade do projetista sobreponha a IA quando necessário.
    """
    id_dados = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )
    dados = models.JSONField()

    class Meta:
        db_table = "dados_inseridos_manualmente"
