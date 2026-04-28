from django.db import models
from apps.usuarios.models import Usuario
from apps.normas.models import Norma
from django.core.exceptions import ValidationError
import uuid

padraoStatus = [
    ('Pendente', 'Pendente'),
    ('Em andamento', 'Em andamento'),
    ('Em revisão', 'Em revisão'),
    ('Concluído', 'Concluído'),
]

transicaoStatus = {
    "Pendente": ["Em andamento"],
    "Em andamento": ["Em revisão"],
    "Em revisão": ["Em andamento", "Concluído"],
    "Concluído": []
}

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
    cep = models.CharField(max_length=10, null=True, blank=True)
    localizacao = models.CharField(max_length=200, null=True, blank=True)


    status = models.CharField(max_length=50, choices=padraoStatus, default='Pendente')

    descricao = models.TextField(null=True, blank=True)
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projetos"

    def __str__(self):
        return self.nome_projeto

    
    def clean(self): 
        # validação de datas
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError("A data de fim não pode ser menor que a data de início.")

        # só valida transição se o projeto já existir no banco
        if Projeto.objects.filter(pk=self.pk).exists():

            projeto_antigo = Projeto.objects.get(pk=self.pk)

            status_atual = projeto_antigo.status
            novo_status = self.status

            if novo_status != status_atual:
                if novo_status not in transicaoStatus.get(status_atual, []):
                    raise ValidationError(
                        f"Não é permitido mudar de '{status_atual}' para '{novo_status}'."
                    )
    
    # Essa função serve para valdiar a função clean
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

def UploadDeArquivo(instance, filename):
    if instance.tipo_arquivo in ['xlsx', 'docx']:
        return f'memorial/{filename}'
    return f'cad_arquivos/{filename}'

class Arquivo(models.Model):
    id_arquivo = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    nome_arquivo = models.CharField(max_length=255)
    hash_arquivo = models.CharField(max_length=255, unique=True)
    caminho_arquivo = models.FileField(upload_to=UploadDeArquivo) # xlsx/docx para memorial/, o resto para cad_arquivos
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

    norma = models.CharField(max_length=255)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projeto_norma"


class EspecificacaoIA(models.Model):
    """
    Representa um documento de especificação gerado por IA (.docx),
    vinculado a um projeto existente (RN.1).
    O arquivo é salvo em /media/especificacoes/ (CA.1 / CA.2).
    Os metadados e o caminho são persistidos no banco (CA.3 / CA.4).
    """
    id_especificacao = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='especificacoes',
        db_column='projeto_id'
    )

    # Caminho do arquivo dentro de /media/ — permite recuperar para download (CA.4)
    arquivo = models.FileField(upload_to='especificacoes/')

    # Metadados da especificação (CA.3)
    titulo = models.CharField(max_length=255)
    versao = models.CharField(max_length=50, default='1.0')
    descricao = models.TextField(null=True, blank=True)
    gerado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'especificacoes_ia'
        ordering = ['-gerado_em']

    def __str__(self):
        return f"{self.titulo} — {self.projeto.nome_projeto} (v{self.versao})"