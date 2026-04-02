from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Projeto, Arquivo
from apps.usuarios.models import Usuario
from .serializers import ProjetoSerializer
from django.http import FileResponse
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

class listarProjetos(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        projetos = Projeto.objects.all()
        serializer = ProjetoSerializer(projetos, many=True)

        return Response(serializer.data)   

class buscarProjeto(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id_projeto):
        projeto = Projeto.objects.get(id_projeto = id_projeto)
        serializer = ProjetoSerializer(projeto)

        return Response(serializer.data) 

class ProjetoDelete(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)
            projeto.delete()
            return Response(status=204)

        except Projeto.DoesNotExist:
            return Response(
                {"erro": "Projeto não encontrado"},
                status=404
            )
        
class ProjetoUpdate(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)

            serializer = ProjetoSerializer(
                projeto,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()

                return Response({
                    "mensagem": "Projeto atualizado com sucesso",
                    "dados": serializer.data
                })

            return Response(serializer.errors, status=400)

        except Projeto.DoesNotExist:
            return Response(
                {"erro": "Projeto não encontrado"},
                status=404
            )

class uploadArquivo(APIView): # POST Arquivo
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

class verificarArquivo(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id_projeto):
        arquivo = Arquivo.objects.filter(
            projeto_id=id_projeto
        ).first()

        if not arquivo:
            return Response(
                {"existe": False},
                status=404
            )

        return Response(
            {
                "existe": True,
                "id_arquivo": arquivo.id_arquivo,
                "nome_arquivo": arquivo.nome_arquivo,
                "tipo_arquivo": arquivo.tipo_arquivo,
                "hash_arquivo": arquivo.hash_arquivo
            },
            status=200
        )

class buscarArquivo(APIView): # GET Arquivo
    def get(self, request, projeto_id):
        try:
            arquivo = Arquivo.objects.filter(projeto_id=projeto_id).first()

            if not arquivo:
                return Response({"error": "Nenhum arquivo vinculado ao projeto"}, status=404)

            if not arquivo.caminho_arquivo:
                return Response(
                    {"erro": "Arquivo não encontrado"},
                    status=404
                )

            baixar = request.GET.get("download") == "1"

            # pega extensão do arquivo
            extensao = arquivo.nome_arquivo.split(".")[-1].lower()

            # arquivos CAD sempre baixam, pra evitar bugs
            if extensao in ["dwg", "dxf"]:
                baixar = True

            # define o tipo
            if extensao == "pdf":
                content_type = "application/pdf"
            else:
                content_type = "application/octet-stream"

            return FileResponse(
                arquivo.caminho_arquivo.open("rb"),
                as_attachment=baixar,
                filename=arquivo.nome_arquivo,
                content_type=content_type
            )

        except Arquivo.DoesNotExist:
            return Response(
                {"erro": "Arquivo não encontrado"},
                status=404
            )
        
class deletarArquivo(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, id):
        try:
            arquivo = Arquivo.objects.get(id_arquivo=id)
            arquivo.caminho_arquivo.delete(save=False)
            arquivo.delete()

            return Response({
                "mensagem": "Arquivo deletado com sucesso"
            })

        except Arquivo.DoesNotExist:
            return Response({"erro": "Arquivo não encontrado"}, status=404)
