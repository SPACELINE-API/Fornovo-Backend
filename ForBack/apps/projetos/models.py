from django.db import models
from apps.usuarios.models import Usuario
from apps.normas.models import Norma
from django.core.exceptions import ValidationError
import uuid

padraoStatus = [
    ('Pendente', 'Pendente'),
    ('Em andamento', 'Em andamento'),
    ('Em Revisão', 'Em Revisão'),
    ('Concluído', 'Concluído'),
]

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


    status = models.CharField(max_length=50, choices=padraoStatus, default='Pendente')

    descricao = models.TextField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)

    normas = models.ManyToManyField(
    Norma,
    through='ProjetoNorma',
    related_name='projetos'
)

    class Meta:
        db_table = "projetos"

    def __str__(self):
        return self.nome_projeto

    # Essa função serve para verificar se a data de inicio é menor que a data do fim
    def clean(self):
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError("A data de fim não pode ser menor que a data de início.")
    
    # Essa função serve para valdiar a função clean
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Arquivo(models.Model):
    id_arquivo = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    nome_arquivo = models.CharField(max_length=255)
    hash_arquivo = models.CharField(max_length=255, unique=True)
    caminho_arquivo = models.FileField(upload_to="cad_arquivos/") #Todos os arquivos vão para /media/cad_arquivos
    tipo_arquivo = models.CharField(max_length=50)

    class Meta:
        db_table = "arquivos"

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