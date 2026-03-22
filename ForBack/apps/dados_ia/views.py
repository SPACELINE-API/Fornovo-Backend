from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import DadosExtraidos, LogValidacao, DadosInseridosManualmente
from apps.projetos.models import Projeto, Norma, Arquivo

class CadastrarDadosExtraidos(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            arquivo_id = request.data.get("arquivo")
            dados = request.data.get("dados")

            arquivo = Arquivo.objects.get(id_arquivo=arquivo_id)
            
            extraido = DadosExtraidos.objects.create(
                arquivo=arquivo,
                dados=dados
            )

            return Response({
                "mensagem": "Dados extraídos cadastrados com sucesso",
                "id": extraido.id_dados
            }, status=201)
        except Arquivo.DoesNotExist:
            return Response({"erro": "Arquivo não encontrado"}, status=404)
        except Exception as e:
            return Response({"erro": str(e)}, status=400)

    def get(self, request):
        dados = DadosExtraidos.objects.all()
        lista = []
        for item in dados:
            lista.append({
                "id_dados": item.id_dados,
                "arquivo": item.arquivo.id_arquivo,
                "dados": item.dados
            })
        return Response(lista)

class CadastrarLogValidacao(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            projeto_id = request.data.get("projeto")
            norma_id = request.data.get("norma")
            dados = request.data.get("dados")

            projeto = Projeto.objects.get(id_projeto=projeto_id)
            norma = Norma.objects.get(id_norma=norma_id)

            log = LogValidacao.objects.create(
                projeto=projeto,
                norma=norma,
                dados=dados
            )

            return Response({
                "mensagem": "Log de validação criado com sucesso",
                "id": log.id_log
            }, status=201)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)
        except Norma.DoesNotExist:
            return Response({"erro": "Norma não encontrada"}, status=404)
        except Exception as e:
            return Response({"erro": str(e)}, status=400)

class CadastrarDadosManuais(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            projeto_id = request.data.get("projeto")
            dados = request.data.get("dados")

            projeto = Projeto.objects.get(id_projeto=projeto_id)

            manual = DadosInseridosManualmente.objects.create(
                projeto=projeto,
                dados=dados
            )

            return Response({
                "mensagem": "Dados manuais inseridos com sucesso",
                "id": manual.id_dados
            }, status=201)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)
        except Exception as e:
            return Response({"erro": str(e)}, status=400)