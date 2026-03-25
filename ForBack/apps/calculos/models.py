from django.db import models
from apps.projetos.models import Projeto


# AMBIENTES
class Ambiente(models.Model):
    id = models.AutoField(primary_key=True)  # ID único

    projeto = models.ForeignKey(
            Projeto,
            on_delete=models.CASCADE,
            null=True,
            related_name="ambientes"
        ) # Chave estrangeira com projeto

    nome = models.CharField(max_length=255)  # Nome do ambiente
    comprimento = models.DecimalField(max_digits=10, decimal_places=2)  # Comprimento
    largura = models.DecimalField(max_digits=10, decimal_places=2)  # Largura
    altura = models.DecimalField(max_digits=10, decimal_places=2)  # Altura
    area = models.DecimalField(max_digits=10, decimal_places=2)  # Área calculada
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação

    def __str__(self):
        return self.nome


# PONTOS ELÉTRICOS
class PontoEletrico(models.Model):
    id = models.AutoField(primary_key=True)  # ID único
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)  # Ligação com ambiente
    tomadas = models.IntegerField()  # Quantidade de tomadas
    pontos_iluminacao = models.IntegerField()  # Pontos de luz
    interruptores = models.IntegerField()  # Interruptores


# CABOS
class Cabo(models.Model):
    id = models.AutoField(primary_key=True)  # ID único
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)  # Ligação com ambiente
    circuito = models.CharField(max_length=255)  # Nome do circuito
    secao_mm2 = models.DecimalField(max_digits=10, decimal_places=2)  # Bitola do cabo


# DISJUNTORES
class Disjuntor(models.Model):
    id = models.AutoField(primary_key=True)  # ID único
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)  # Ambiente
    amperagem = models.IntegerField()  # Corrente do disjuntor
    quantidade = models.IntegerField()  # Número de disjuntores


# TIPOS DE COMPONENTES
class TipoEletrico(models.Model):
    id = models.AutoField(primary_key=True)  # ID único
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)  # Ambiente
    tipo_tomada = models.CharField(max_length=255)  # Tipo de tomada
    tipo_interruptor = models.CharField(max_length=255)  # Tipo de interruptor
    tipo_luminaria = models.CharField(max_length=255)  # Tipo de luminária
    altura_instalacao = models.DecimalField(max_digits=10, decimal_places=2)  # Altura de instalação


# RAMAIS
class Ramal(models.Model):
    id = models.AutoField(primary_key=True)  # ID único
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)  # Ambiente
    nome = models.CharField(max_length=255)  # Nome do ramal
    diametro = models.CharField(max_length=50)  # Diâmetro do ramal
    comprimento_m = models.DecimalField(max_digits=10, decimal_places=2)  # Comprimento em metros


# HIDRÁULICA
class Hidraulica(models.Model):
    id = models.AutoField(primary_key=True)  # ID único
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)  # Ambiente
    registros = models.IntegerField()  # Número de registros
    valvulas = models.IntegerField()  # Número de válvulas
    conexoes = models.IntegerField()  # Número de conexões


# RESERVATÓRIOS
class Reservatorio(models.Model):
    id = models.AutoField(primary_key=True)  # ID único
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)  # Ambiente
    tipo = models.CharField(max_length=255)  # Tipo de reservatório
    capacidade_l = models.DecimalField(max_digits=10, decimal_places=2)  # Capacidade em litros


# SPDA / ATERRAMENTO
class SPDA(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    hastes = models.IntegerField()  # Quantidade de hastes
    caixas_inspecao = models.IntegerField()  # Caixas de inspeção
    terminais_aereos = models.IntegerField()  # Terminais aéreos


# TELEFONIA / REDE / CFTV
class Telecom(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    quadros_rede = models.IntegerField()  # Quadros de rede
    patch_cords = models.IntegerField()  # Patch cords
    cameras = models.IntegerField()  # Câmeras CFTV


# CABEAMENTOS
class Cabeamento(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    circuito = models.CharField(max_length=255)  # Circuito
    comprimento_m = models.DecimalField(max_digits=10, decimal_places=2)  # Comprimento
    tomadas = models.IntegerField()  # Quantidade de tomadas


# EXTINTORES
class Extintor(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=255)  # Tipo de extintor
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2)  # Peso em kg
    capacidade_l = models.DecimalField(max_digits=10, decimal_places=2)  # Capacidade


# HIDRANTES
class Hidrante(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    localizacao = models.CharField(max_length=255)  # Localização
    diametro = models.CharField(max_length=50)  # Diâmetro
    conexoes = models.IntegerField()  # Quantidade de conexões


# DUTOS
class Duto(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    diametro = models.CharField(max_length=50)  # Diâmetro do duto
    comprimento_m = models.DecimalField(max_digits=10, decimal_places=2)  # Comprimento


# COBERTURA
class Cobertura(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    estrutura = models.CharField(max_length=255)  # Estrutura
    telhamento = models.CharField(max_length=255)  # Tipo de telhado
    espessura_cm = models.DecimalField(max_digits=10, decimal_places=2)  # Espessura
    inclinacao_percent = models.DecimalField(max_digits=10, decimal_places=2)  # Inclinação


# PEÇAS
class Peca(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=255)  # Descrição da peça
    secao = models.CharField(max_length=255)  # Seção da peça


# CANTEIRO DE OBRAS
class Canteiro(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    conteineres = models.IntegerField()  # Número de contêineres
    banheiros = models.IntegerField()  # Número de banheiros
    andaimes = models.IntegerField()  # Andaimes


# RESÍDUOS
class Residuo(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    comum_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Resíduo comum m³
    contaminado_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Resíduo contaminado m³
    destinacao = models.CharField(max_length=255)  # Destinação


# ESCAVAÇÃO
class Escavacao(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    profundidade_m = models.DecimalField(max_digits=10, decimal_places=2)  # Profundidade
    inclinacao_percent = models.DecimalField(max_digits=10, decimal_places=2)  # Inclinação


# VOLUMES
class Volume(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    terraplanagem_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Terraplanagem
    escavacao_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Escavação
    aterro_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Aterro
    enrocamento_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Enrocamento
    contencao_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Contenção
    taludamento_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Taludamento
    nivelamento_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Nivelamento
    compactacao_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Compactação


# FUNDAÇÕES
class Fundacao(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=255)  # Tipo da fundação
    profundidade_m = models.DecimalField(max_digits=10, decimal_places=2)  # Profundidade
    volume_lastro_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Lastro
    volume_concreto_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Concreto
    ferragem_kgf = models.DecimalField(max_digits=10, decimal_places=2)  # Aço
    estribo_kgf = models.DecimalField(max_digits=10, decimal_places=2)  # Estribo
    forma_m2 = models.DecimalField(max_digits=10, decimal_places=2)  # Forma m²


# SUPER ESTRUTURA
class SuperEstrutura(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=255)  # Tipo
    largura_m = models.DecimalField(max_digits=10, decimal_places=2)  # Largura
    altura_m = models.DecimalField(max_digits=10, decimal_places=2)  # Altura
    volume_concreto_m3 = models.DecimalField(max_digits=10, decimal_places=2)  # Concreto
    ferragem_kgf = models.DecimalField(max_digits=10, decimal_places=2)  # Aço
    estribo_kgf = models.DecimalField(max_digits=10, decimal_places=2)  # Estribo
    forma_m2 = models.DecimalField(max_digits=10, decimal_places=2)  # Forma


# ESTRUTURAS METÁLICAS
class EstruturaMetalica(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=255)  # Tipo
    perfil = models.CharField(max_length=255)  # Perfil metálico
    secao = models.CharField(max_length=255)  # Seção
    peso_kgf = models.DecimalField(max_digits=10, decimal_places=2)  # Peso
    elastomero = models.DecimalField(max_digits=10, decimal_places=2)  # Elastômero


# ESTRUTURAS EM MADEIRA
class EstruturaMadeira(models.Model):
    id = models.AutoField(primary_key=True)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE)
    peca = models.CharField(max_length=255)  # Nome da peça
    secao = models.CharField(max_length=255)  # Seção da peça
    peso_kgf = models.DecimalField(max_digits=10, decimal_places=2)  # Peso
    telhamento = models.CharField(max_length=255)  # Telhamento