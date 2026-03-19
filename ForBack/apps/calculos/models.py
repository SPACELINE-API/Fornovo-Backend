from django.db import models
from apps.projetos.models import Projeto


class Dimensao(models.Model):
    id_dimensao = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    tipo = models.CharField(max_length=50)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    unidade = models.CharField(max_length=10, default="m")
    referencia = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "dimensoes"


class Ambiente(models.Model):
    id_ambiente = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    nome_ambiente = models.CharField(max_length=100)
    area = models.DecimalField(max_digits=10, decimal_places=2)

    comprimento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    largura = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    altura = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = "ambientes"


class Esquadria(models.Model):
    id_esquadria = models.AutoField(primary_key=True)

    ambiente = models.ForeignKey(
        Ambiente,
        on_delete=models.CASCADE,
        db_column="ambiente_id"
    )

    codigo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)

    largura = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    altura = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    material = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = "esquadrias"


class EstruturaElemento(models.Model):
    id_elemento = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    tipo = models.CharField(max_length=50)

    comprimento = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    largura = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    altura = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    volume_concreto = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    peso_ferragem = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = "estrutura_elementos"


class CircuitoEletrico(models.Model):
    id_circuito = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    codigo = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50, null=True)

    disjuntor = models.IntegerField(null=True)
    secao_cabo = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = "circuitos_eletricos"


class PontoEletrico(models.Model):
    id_ponto = models.AutoField(primary_key=True)

    ambiente = models.ForeignKey(
        Ambiente,
        on_delete=models.CASCADE,
        db_column="ambiente_id"
    )

    circuito = models.ForeignKey(
        CircuitoEletrico,
        on_delete=models.CASCADE,
        db_column="circuito_id"
    )

    tipo = models.CharField(max_length=50)

    potencia = models.IntegerField(null=True)
    altura_instalacao = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = "pontos_eletricos"


class SPDA(models.Model):
    id_spda = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    tipo = models.CharField(max_length=100)
    material = models.CharField(max_length=100, null=True)

    secao = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    comprimento = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    quantidade = models.IntegerField(null=True)

    class Meta:
        db_table = "spda"


class RamalHidraulico(models.Model):
    id_ramal = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    nome_ramal = models.CharField(max_length=50)

    diametro = models.IntegerField(null=True)
    comprimento = models.DecimalField(max_digits=10, decimal_places=2, null=True)

    class Meta:
        db_table = "ramais_hidraulicos"


class PontoHidraulico(models.Model):
    id_ponto = models.AutoField(primary_key=True)

    ambiente = models.ForeignKey(
        Ambiente,
        on_delete=models.CASCADE,
        db_column="ambiente_id"
    )

    ramal = models.ForeignKey(
        RamalHidraulico,
        on_delete=models.CASCADE,
        db_column="ramal_id"
    )

    tipo = models.CharField(max_length=50)
    diametro = models.IntegerField(null=True)

    class Meta:
        db_table = "pontos_hidraulicos"


class Demolicao(models.Model):
    id_demolicao = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    elemento = models.CharField(max_length=100)
    descricao = models.TextField(null=True)

    class Meta:
        db_table = "demolicoes"


class MovimentoSolo(models.Model):
    id_movimento = models.AutoField(primary_key=True)

    projeto = models.ForeignKey(
        Projeto,
        on_delete=models.CASCADE,
        db_column="projeto_id"
    )

    tipo = models.CharField(max_length=50)

    volume = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unidade = models.CharField(max_length=20, default="m3")

    class Meta:
        db_table = "movimento_solo"