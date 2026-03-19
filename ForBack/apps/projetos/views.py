from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Projeto
from apps.usuarios.models import Usuario

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