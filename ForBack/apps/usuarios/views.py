from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Usuario

# Create your views here.

class criarUsuario(APIView):
    def post(self, request):
        try:
            usuario = Usuario.objects.create(
                nome_usuario = request.data.get('nome_usuario'),
                email_usuario = request.data.get('email_usuario'),
                senha_usuario = request.data.get('senha_usuario'),
                nivel_usuario = request.data.get('nivel_usuario'),
                status = request.data.get('status','Ativo')
            )

            return Response({
                "mensagem": "Usuário criado com sucesso",
                "id": usuario.id_usuario,
                'nome': usuario.nome_usuario
            })
        except Exception as e:
            return Response({"erro": str(e)}, status=400)

