from django.db import models

class Norma(models.Model):

    statusNorma= [
    ("ativo", "Ativo"),
    ("inativo", "Inativo"),
    ]
 
    id_norma = models.AutoField(primary_key=True)

    codigo = models.CharField(max_length=50)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(null=True, blank=True)

    hash_arquivo = models.CharField(max_length=64, unique=True, null=True, blank=True)

    ano = models.IntegerField()
    serie = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=statusNorma, default="ativo")
    criado_em = models.DateTimeField(auto_now_add=True)

    arquivo_pdf = models.FileField(upload_to="nbr-pdf/", null=True, blank=True)

    class Meta:
        db_table = "normas"
        unique_together = ("codigo", "ano", "serie")


