from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Projeto, Arquivo
from apps.usuarios.models import Usuario
from .serializers import ProjetoSerializer
import hashlib


class cadastrarProjeto(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ProjetoSerializer(data=request.data)

        if serializer.is_valid():

            usuario_padrao = Usuario.objects.first()

            if not usuario_padrao:
                return Response(
                    {"erro": "Nenhum usuário cadastrado no sistema."},
                    status=400
                )

            serializer.save(engenheiro=usuario_padrao)

            return Response({
                "mensagem": "Projeto criado com sucesso",
                "dados": serializer.data
            }, status=201)

        return Response(serializer.errors, status=400)


class uploadArquivo(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            arquivo = request.FILES.get("arquivo")
            if not arquivo:
                return Response({"erro": "Nenhum arquivo enviado"}, status=400)

            projeto_id = request.data.get("projeto_id")
            if not projeto_id:
                return Response({"erro": "ID do projeto é obrigatório"}, status=400)

            projeto = Projeto.objects.get(id_projeto=projeto_id)

            ext_permitidas = ["pdf", "dwg", "dxf"]
            ext = arquivo.name.split(".")[-1].lower()

            if ext not in ext_permitidas:
                return Response({"erro": f"Extensão '{ext}' não permitida"}, status=400)

            hash_arquivo = hashlib.sha256(arquivo.read()).hexdigest()
            arquivo.seek(0)  

            novo_arquivo = Arquivo.objects.create(
                projeto=projeto,
                nome_arquivo=arquivo.name,
                caminho_arquivo=arquivo,
                tipo_arquivo=ext,
                hash_arquivo=hash_arquivo
            )
            return Response({
                "mensagem": "Arquivo enviado com sucesso",
                "id_arquivo": novo_arquivo.id_arquivo
            })

        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)

        except Exception as e:
            return Response({"erro": str(e)}, status=400)
        
class listarProjetos(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        projetos = Projeto.objects.all()
        serializer = ProjetoSerializer(projetos, many=True)

        return Response(serializer.data)    