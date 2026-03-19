from django.db import models
from apps.usuarios.models import Usuario
import uuid

class Projeto(models.Model):
    id_projeto = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    nome_projeto = models.CharField(max_length=200)

    engenheiro = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column="engenheiro_id"
    )

    cliente = models.CharField(max_length=100)
    localizacao = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=50, default='Pendente')

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projetos"

    def __str__(self):
        return self.nome_projeto


class Arquivo(models.Model):
    id_arquivo = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    nome_arquivo = models.CharField(max_length=255)
    hash_arquivo = models.CharField(max_length=255, unique=True)
    caminho_arquivo = models.TextField()
    tipo_arquivo = models.CharField(max_length=50)

    class Meta:
        db_table = "arquivos"


class Norma(models.Model):
    id_norma = models.AutoField(primary_key=True)

    codigo = models.CharField(max_length=50)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)

    ano = models.IntegerField()
    serie = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(max_length=20, default="ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "normas"
        unique_together = ("codigo", "ano", "serie")


class ProjetoNorma(models.Model):
    id = models.AutoField(primary_key=True)

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

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projeto_norma"