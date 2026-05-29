from django.db import models
from django.db.models import Count
from apps.usuarios.models import Usuario
from apps.normas.models import Norma
from django.core.exceptions import ValidationError
from django.utils import timezone
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

    def situacao_prazo(self):
        """
        Compara data_inicio e data_fim com a data atual.
        Retorna: 'no_prazo', 'atrasado' ou 'sem_datas'.
        """
        if not self.data_inicio or not self.data_fim:
            return 'sem_datas'

        if self.status == 'Concluído':
            return 'no_prazo'

        hoje = timezone.localdate()
        if hoje > self.data_fim:
            return 'atrasado'

        return 'no_prazo'

    @classmethod
    def contagem_por_prazo(cls):
        projetos = cls.objects.filter(
            data_inicio__isnull=False,
            data_fim__isnull=False,
        )

        no_prazo = 0
        atrasados = 0

        for projeto in projetos:
            if projeto.situacao_prazo() == 'atrasado':
                atrasados += 1
            else:
                no_prazo += 1

        total = no_prazo + atrasados
        return {
            'no_prazo': no_prazo,
            'atrasados': atrasados,
            'total': total,
        }

    def clean(self):
        if self.data_inicio and self.data_fim:
            if self.data_fim < self.data_inicio:
                raise ValidationError("A data de fim não pode ser menor que a data de início.")

        if Projeto.objects.filter(pk=self.pk).exists():

            projeto_antigo = Projeto.objects.get(pk=self.pk)

            status_atual = projeto_antigo.status
            novo_status = self.status

            if novo_status != status_atual:
                if novo_status not in transicaoStatus.get(status_atual, []):
                    raise ValidationError(
                        f"Não é permitido mudar de '{status_atual}' para '{novo_status}'."
                    )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

def UploadDeArquivo(instance, filename):
    if instance.tipo_arquivo in ['xlsx', 'docx', 'docx_espec']:
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
    caminho_arquivo = models.FileField(upload_to=UploadDeArquivo) 
    tipo_arquivo = models.CharField(max_length=50)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "arquivos"


class Notificacao(models.Model):
    TIPOS = [
        ('info', 'Info'),
        ('sucesso', 'Sucesso'),
        ('alerta', 'Alerta'),
        ('erro', 'Erro'),
    ]

    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='info')
    mensagem = models.TextField()
    usuario = models.CharField(max_length=100, default='Sistema')
    referencia_tipo = models.CharField(max_length=50, null=True, blank=True)
    referencia_id = models.CharField(max_length=100, null=True, blank=True)
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificacoes'
        ordering = ['-criado_em']

    @classmethod
    def queryset_do_usuario(cls, usuario=None):
        """Filtro por destinatário pode ser adicionado na task do dropdown do sino."""
        return cls.objects.all()

    @classmethod
    def contar_nao_lidas(cls, usuario=None):
        return cls.queryset_do_usuario(usuario).filter(lida=False).count()

    def data_formatada(self):
        agora = timezone.localtime(timezone.now())
        dt = timezone.localtime(self.criado_em)
        diff = (agora.date() - dt.date()).days

        if diff == 0:
            return f'Hoje, {dt.strftime("%H:%M")}'
        if diff == 1:
            return f'Ontem, {dt.strftime("%H:%M")}'
        return dt.strftime('%d/%m/%Y %H:%M')

    @classmethod
    def listar_recentes(cls, limite=20):
        return cls.objects.all()[:limite]
    
class NotificacaoLeitura(models.Model):
    notificacao = models.ForeignKey(Notificacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.CASCADE)
    lida_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['notificacao', 'usuario']

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

    @classmethod
    def top_normas_utilizadas(cls, limite=5):
        ranking = (
            cls.objects
            .values('norma')
            .annotate(usos=Count('projeto', distinct=True))
            .order_by('-usos', 'norma')[:limite]
        )

        return {
            'total': cls.objects.count(),
            'normas': [
                {'nome': item['norma'], 'usos': item['usos']}
                for item in ranking
            ],
        }


class EspecificacaoIA(models.Model):
    id_especificacao = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        related_name='especificacoes',
        db_column='projeto_id'
    )

    arquivo = models.FileField(upload_to='especificacoes/')
    titulo = models.CharField(max_length=255)
    versao = models.CharField(max_length=50, default='1.0')
    descricao = models.TextField(null=True, blank=True)
    gerado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'especificacoes_ia'
        ordering = ['-gerado_em']

    def __str__(self):
        return f"{self.titulo} — {self.projeto.nome_projeto} (v{self.versao})"