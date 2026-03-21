from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Projeto, Arquivo
from apps.usuarios.models import Usuario
import hashlib


class cadastrarProjeto(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            engenheiro_id = request.data.get("engenheiro")

            engenheiro = Usuario.objects.get(id_usuario=engenheiro_id)

            projeto = Projeto.objects.create(
                nome_projeto=request.data.get("nome_projeto"),
                engenheiro=engenheiro,
                cliente=request.data.get("cliente"),
                localizacao=request.data.get("localizacao"),
                status = request.data.get('status', 'Pendente')
            )

            return Response({
                "mensagem": "Projeto criado com sucesso",
                "id": projeto.id_projeto
            })

        except Usuario.DoesNotExist:
            return Response({"erro": "Engenheiro não encontrado"}, status=404)

        except Exception as e:
            return Response({"erro": str(e)}, status=400)

class uploadArquivo(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            # Pega o arquivo da requisição
            arquivo = request.FILES.get("arquivo")
            if not arquivo: # Se não tiver, dá erro
                return Response({"erro": "Nenhum arquivo enviado"}, status=400)

            # Pega o ID do Projeto
            projeto_id = request.data.get("projeto_id")
            if not projeto_id: # Se não tiver, dá erro
                return Response({"erro": "ID do projeto é obrigatório"}, status=400)

            projeto = Projeto.objects.get(id_projeto=projeto_id)

            # Validação da extensão, só entra 3 tipos de arquivos, pdf, dwg e dxf
            ext_permitidas = ["pdf", "dwg", "dxf"]
            ext = arquivo.name.split(".")[-1].lower()

            if ext not in ext_permitidas: # Se não for nenhum dos 3, dá erro
                return Response({"erro": f"Extensão '{ext}' não permitida"}, status=400)

            # Gera hash do arquivo para detectar arquivos duplicados
            hash_arquivo = hashlib.sha256(arquivo.read()).hexdigest()
            arquivo.seek(0)  # reseta cursor depois de ler

            # Salva no model (FileField salva automático em MEDIA_ROOT/upload_to)
            novo_arquivo = Arquivo.objects.create(
                projeto=projeto,
                nome_arquivo=arquivo.name,
                caminho_arquivo=arquivo,
                tipo_arquivo=ext,
                hash_arquivo=hash_arquivo
            )
            # Mensagem de êxito
            return Response({
                "mensagem": "Arquivo enviado com sucesso",
                "id_arquivo": novo_arquivo.id_arquivo
            })

        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)

        except Exception as e:
            return Response({"erro": str(e)}, status=400)