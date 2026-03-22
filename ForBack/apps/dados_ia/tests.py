from django.test import TestCase
from apps.projetos.models import Projeto, Norma, Arquivo
from apps.usuarios.models import Usuario
from .models import DadosExtraidos, LogValidacao, DadosInseridosManualmente
import zlib
import json

# Lista global para armazenar os resultados dos testes
RESULTADOS_TESTES = []

def registrar_resultado(nome, status):
    RESULTADOS_TESTES.append({"nome": nome, "status": status})

def imprimir_resumo():
    print("\n" + "="*60)
    print(f"{'RESUMO DOS TESTES - DADOS IA':^60}")
    print("="*60)
    print(f"{'ID':<5} | {'NOME DO TESTE':<40} | {'STATUS':<10}")
    print("-" * 60)
    for i, res in enumerate(RESULTADOS_TESTES, 1):
        status_icon = "✅" if res['status'] == "PASSOU" else "❌"
        print(f"{i:<5} | {res['nome']:<40} | {status_icon} {res['status']}")
    print("="*60 + "\n")

class Test01_ModelIntegrity(TestCase):
    """
    Testes unitários para validar a integridade dos modelos de IA.
    """

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

    def setUp(self):

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
        self.arquivo = Arquivo.objects.create(
            projeto=self.projeto, 
            nome_arquivo="plantabaixa.dxf", 
            caminho_arquivo="/media/dxf/alpha.dxf",
            hash_arquivo="hash_dummy_123",
            tipo_arquivo="DXF"
        )

    def test_01_json_compression_and_persistence(self):
        print("\n" + "="*50)
        print("🔍 TESTE 1: Integridade e Compressão de JSON")
        print("="*50)
        
        try:
            dados_complexos = {
                "entidades": [
                    {"tipo": "LINE", "coords": [0, 0, 10, 10], "layer": "Eletrico"},
                    {"tipo": "CIRCLE", "raio": 5.5, "centro": [20, 20]}
                ],
                "metadados": {"ia_confianca": 0.98}
            }
            extraido = DadosExtraidos.objects.create(arquivo=self.arquivo, dados=dados_complexos)
            extraido_db = DadosExtraidos.objects.get(id_dados=extraido.id_dados)
            self.assertEqual(extraido_db.dados, dados_complexos)
            print("✅ Sucesso: JSON recuperado é idêntico ao enviado.")
            
            conteudo_binario = bytes(extraido_db.dados_binarios)
            self.assertIsInstance(conteudo_binario, bytes)
            print("✅ Sucesso: Dados armazenados em formato binário.")
            
            registrar_resultado("Integridade e Compressão JSON", "PASSOU")
        except Exception as e:
            registrar_resultado("Integridade e Compressão JSON", "FALHOU")
            raise e

    def test_02_cascade_delete_integrity(self):
        print("\n" + "="*50)
        print("🗑️  TESTE 2: Deleção em Cascata (Integridade)")
        print("="*50)
        
        try:
            DadosExtraidos.objects.create(arquivo=self.arquivo, dados={"teste": "valor"})
            LogValidacao.objects.create(projeto=self.projeto, norma=self.norma, dados={"aviso": "erro"})
            self.projeto.delete()
            self.assertEqual(Arquivo.objects.count(), 0)
            self.assertEqual(DadosExtraidos.objects.count(), 0)
            print("✅ Sucesso: Todos os dados da IA foram limpos ao deletar o Projeto pai.")
            registrar_resultado("Deleção em Cascata (Integridade)", "PASSOU")
        except Exception as e:
            registrar_resultado("Deleção em Cascata (Integridade)", "FALHOU")
            raise e

    def test_03_log_validacao_per_norma(self):
        print("\n" + "="*50)
        print("📋 TESTE 3: Múltiplos Logs por Norma")
        print("="*50)
        
        try:
            norma2 = Norma.objects.create(codigo="NBR 9050", nome="Acessibilidade", ano=2020)
            LogValidacao.objects.create(projeto=self.projeto, norma=self.norma, dados={"result": "OK"})
            LogValidacao.objects.create(projeto=self.projeto, norma=norma2, dados={"result": "Falha"})
            logs_count = LogValidacao.objects.filter(projeto=self.projeto).count()
            self.assertEqual(logs_count, 2)
            print(f"✅ Sucesso: Registrados {logs_count} logs diferentes.")
            registrar_resultado("Múltiplos Logs por Norma", "PASSOU")
        except Exception as e:
            registrar_resultado("Múltiplos Logs por Norma", "FALHOU")
            raise e

    def test_04_dados_manuais_vs_ia(self):
        print("\n" + "="*50)
        print("👤 TESTE 4: Dados Manuais vs IA")
        print("="*50)
        
        try:
            dados_manuais = {"ponto_manual": [10, 10]}
            manual = DadosInseridosManualmente.objects.create(projeto=self.projeto, dados=dados_manuais)
            self.assertEqual(manual.dados["ponto_manual"], [10, 10])
            print("✅ Sucesso: Dados manuais persistidos corretamente.")
            registrar_resultado("Dados Manuais vs IA", "PASSOU")
        except Exception as e:
            registrar_resultado("Dados Manuais vs IA", "FALHOU")
            raise e

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class Test02_APICrud(APITestCase):
    """
    Testes de integração para validar as rotas de CRUD (API) da IA.
    """


    @classmethod
    def tearDownClass(cls):
        imprimir_resumo()
        super().tearDownClass()

    def setUp(self):
        self.usuario = Usuario.objects.create(
            nome_usuario="Engenheiro API", 
            email_usuario="api@fornovo.com",
            senha_usuario="123"
        )
        self.projeto = Projeto.objects.create(
            nome_projeto="Projeto Teste API", 
            engenheiro=self.usuario, 
            cliente="Cliente API"
        )
        self.norma = Norma.objects.create(
            codigo="API 101",
            nome="Norma de Teste API",
            ano=2024
        )
        self.arquivo = Arquivo.objects.create(
            projeto=self.projeto, 
            nome_arquivo="api_test.dxf", 
            caminho_arquivo="/media/dxf/api.dxf",
            hash_arquivo="hash_api_123",
            tipo_arquivo="DXF"
        )

    def test_05_post_dados_extraidos(self):
        print("\n" + "="*50)
        print("🚀 TESTE 5: API CRUD - POST Dados Extraídos")
        print("="*50)
        try:
            url = reverse('dados_ia:cadastrar_dados_extraidos')
            data = {"arquivo": self.arquivo.id_arquivo, "dados": {"cor": "RED"}}
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            print(f"✅ Sucesso: POST {url} retornou 201.")
            registrar_resultado("API POST Dados Extraídos", "PASSOU")
        except Exception as e:
            registrar_resultado("API POST Dados Extraídos", "FALHOU")
            raise e

    def test_06_post_log_validacao(self):
        print("\n" + "="*50)
        print("🚀 TESTE 6: API CRUD - POST Log Validação")
        print("="*50)
        try:
            url = reverse('dados_ia:cadastrar_log_validacao')
            data = {
                "projeto": str(self.projeto.id_projeto),
                "norma": self.norma.id_norma,
                "dados": {"status": "APROVADO"}
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            print(f"✅ Sucesso: POST {url} retornou 201.")
            registrar_resultado("API POST Log Validação", "PASSOU")
        except Exception as e:
            registrar_resultado("API POST Log Validação", "FALHOU")
            raise e

    def test_07_post_dados_manuais(self):
        print("\n" + "="*50)
        print("🚀 TESTE 7: API CRUD - POST Dados Manuais")
        print("="*50)
        try:
            url = reverse('dados_ia:cadastrar_dados_manuais')
            data = {"projeto": str(self.projeto.id_projeto), "dados": {"ajuste": "viga"}}
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            print(f"✅ Sucesso: POST {url} retornou 201.")
            registrar_resultado("API POST Dados Manuais", "PASSOU")
        except Exception as e:
            registrar_resultado("API POST Dados Manuais", "FALHOU")
            raise e

    def test_08_get_dados_extraidos(self):
        print("\n" + "="*50)
        print("🚀 TESTE 8: API CRUD - GET Dados Extraídos")
        print("="*50)
        try:
            # Criar um dado antes
            DadosExtraidos.objects.create(arquivo=self.arquivo, dados={"info": "test_get"})
            url = reverse('dados_ia:cadastrar_dados_extraidos')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(len(response.data) > 0)
            print(f"✅ Sucesso: GET {url} retornou {len(response.data)} registros.")
            registrar_resultado("API GET Dados Extraídos", "PASSOU")
        except Exception as e:
            registrar_resultado("API GET Dados Extraídos", "FALHOU")
            raise e



