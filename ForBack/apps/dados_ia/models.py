import zlib
import json
from django.db import models
from apps.projetos.models import Projeto, Norma, Arquivo

class DadosExtraidos(models.Model):
    id_dados = models.AutoField(primary_key=True)
    arquivo = models.ForeignKey(
        Arquivo,
        on_delete=models.CASCADE,
        db_column="arquivo_id"
    )
    
    dados_binarios = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = "dados_extraidos"

    @property
    def dados(self):
        if not self.dados_binarios:
            return None
        return json.loads(zlib.decompress(self.dados_binarios).decode('utf-8'))

    @dados.setter
    def dados(self, value):
        if value:
            self.dados_binarios = zlib.compress(json.dumps(value).encode('utf-8'))
        else:
            self.dados_binarios = None

class LogValidacao(models.Model):
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
    id_dados = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )
    dados = models.JSONField()

    class Meta:
        db_table = "dados_inseridos_manualmente"

class RelatorioConformidade(models.Model):
    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )
    nome_arquivo = models.CharField(max_length=255, default='')
    caminho_arquivo = models.CharField(max_length=500, default='')
    arquivo = models.FileField(upload_to="relatorios/")
    criado_em = models.DateTimeField(auto_now_add=True)
    responsavel = models.CharField(max_length=255, default='')
    geracao_manual = models.BooleanField(default=False)

    class Meta:
        db_table = "relatorios_conformidade"