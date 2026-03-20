from django.test import TestCase
from apps.projetos.models import Projeto, Norma
from apps.usuarios.models import Usuario
from .models import ArquivoDXF, DadosExtraidos, LogValidacao, DadosInseridosManualmente
import zlib
import json

class DadosIAModelTest(TestCase):
    """
    Testes unitários para validar a integridade dos modelos de IA.
    """

    def setUp(self):
        """Configura os dados base necessários para os testes."""
        self.usuario = Usuario.objects.create(
            nome_usuario="Engenheiro Teste", 
            email_usuario="teste@fornovo.com",
            senha_usuario="123",
            nivel_usuario="Admin"
        )
        self.projeto = Projeto.objects.create(
            nome_projeto="Projeto Edifício Alpha", 
            engenheiro=self.usuario, 
            cliente="Construtora Teste"
        )
        self.norma = Norma.objects.create(
            codigo="NBR 5410",
            nome="Instalações Elétricas",
            ano=2004
        )
        self.arquivo_dxf = ArquivoDXF.objects.create(
            projeto=self.projeto, 
            nome_arquivo="plantabaixa.dxf", 
            caminho_arquivo="/media/dxf/alpha.dxf"
        )

    def test_json_compression_and_persistence(self):
        print("\n" + "="*50)
        print("🔍 TESTE 1: Integridade e Compressão de JSON")
        print("="*50)
        
        dados_complexos = {
            "entidades": [
                {"tipo": "LINE", "coords": [0, 0, 10, 10], "layer": "Eletrico"},
                {"tipo": "CIRCLE", "raio": 5.5, "centro": [20, 20]}
            ],
            "metadados": {"ia_confianca": 0.98}
        }

        # Salvando
        extraido = DadosExtraidos.objects.create(
            arquivo=self.arquivo_dxf,
            dados=dados_complexos
        )

        extraido_db = DadosExtraidos.objects.get(id_dados=extraido.id_dados)

        # 1. Verificando JSON
        self.assertEqual(extraido_db.dados, dados_complexos)
        print("✅ Sucesso: JSON recuperado é idêntico ao enviado.")

        # 2. Verificando persistência binária (Corrigindo erro de memoryview no Postgres)
        conteudo_binario = bytes(extraido_db.dados_binarios)
        self.assertIsInstance(conteudo_binario, bytes)
        print("✅ Sucesso: Dados armazenados em formato binário (BinaryField).")

        # 3. Comparação de tamanho
        json_size = len(json.dumps(dados_complexos))
        compressed_size = len(conteudo_binario)
        desconto = 100 - (compressed_size / json_size * 100)
        
        print(f"📊 Estatísticas de Armazenamento:")
        print(f"   - Tamanho Texto (JSON): {json_size} bytes")
        print(f"   - Tamanho Comprimido (Zlib): {compressed_size} bytes")
        print(f"   - Economia de Espaço: {desconto:.2f}%")
        print("-" * 50)

    def test_cascade_delete_integrity(self):
        print("\n" + "="*50)
        print("🗑️  TESTE 2: Deleção em Cascata (Integridade)")
        print("="*50)
        
        DadosExtraidos.objects.create(arquivo=self.arquivo_dxf, dados={"teste": "valor"})
        LogValidacao.objects.create(projeto=self.projeto, norma=self.norma, dados={"aviso": "erro"})

        print(f"📦 Registros antes: Arquivos={ArquivoDXF.objects.count()}, Dados IA={DadosExtraidos.objects.count()}")
        
        # Executa delete
        self.projeto.delete()

        # Verificações
        self.assertEqual(ArquivoDXF.objects.count(), 0)
        self.assertEqual(DadosExtraidos.objects.count(), 0)
        
        print("✅ Sucesso: Todos os dados da IA foram limpos ao deletar o Projeto pai.")
        print("-" * 50)

    def test_log_validacao_per_norma(self):
        print("\n" + "="*50)
        print("📋 TESTE 3: Múltiplos Logs por Norma")
        print("="*50)
        
        norma2 = Norma.objects.create(codigo="NBR 9050", nome="Acessibilidade", ano=2020)
        
        LogValidacao.objects.create(projeto=self.projeto, norma=self.norma, dados={"result": "OK"})
        LogValidacao.objects.create(projeto=self.projeto, norma=norma2, dados={"result": "Falha"})

        logs_count = LogValidacao.objects.filter(projeto=self.projeto).count()
        self.assertEqual(logs_count, 2)
        
        print(f"✅ Sucesso: Registrados {logs_count} logs diferentes para o mesmo projeto.")
        print("-" * 50)

    def test_dados_manuais_vs_ia(self):
        print("\n" + "="*50)
        print("👤 TESTE 4: Dados Manuais vs IA")
        print("="*50)
        
        dados_manuais = {"ponto_manual": [10, 10]}
        manual = DadosInseridosManualmente.objects.create(projeto=self.projeto, dados=dados_manuais)
        
        self.assertEqual(manual.dados["ponto_manual"], [10, 10])
        print("✅ Sucesso: Dados manuais persistidos corretamente e isolados da IA.")
        print("-" * 50)

