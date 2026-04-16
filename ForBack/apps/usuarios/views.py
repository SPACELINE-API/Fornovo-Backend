from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Usuario
from django.contrib.auth.hashers import make_password


# Create your views here.

class criarUsuario(APIView):
    def post(self, request):
        try:
            senha = request.data.get('senha')
            usuario = Usuario.objects.create(
                nome_usuario=request.data.get('nome'),
                email_usuario=request.data.get('email'),
                senha_usuario=make_password(senha),
                nivel_usuario=request.data.get('nivelUsuario'),
                status=request.data.get('status', 'Ativo')
            )
            return Response({
                "mensagem": "Usuário criado com sucesso",
                "id": usuario.id_usuario,
                "nome": usuario.nome_usuario
            })

            if not request.data.get('nome'):
                return Response({"erro": "Nome obrigatório"}, status=400)
            if not request.data.get('email'):
                return Response({"erro": "Email obrigatório"}, status=400)
            if not request.data.get('senha'):
                return Response({"erro": "Senha obrigatória"}, status=400)
        except Exception as e:
            return Response({"erro": str(e)}, status=400)

class listarUsuario(APIView):
    def get(self, request):
        usuarios = Usuario.objects.all()

        data = []
        for u in usuarios:
            data.append({
                "id": u.id_usuario,
                "nome": u.nome_usuario,
                "email": u.email_usuario,
                "nivelUsuario": u.nivel_usuario,
                "status": u.status
            })
        return Response(data)

class atualizarStatusUsuario(APIView):
    def patch(self, request, id):
        try:
            usuario = Usuario.objects.get(id_usuario=id)
            novo_status = request.data.get('status')
            usuario.status = novo_status
            usuario.save()

            return Response({
                "mensagem": "Status atualizado com sucesso"
            })

        except Usuario.DoesNotExist:
            return Response({"erro": "Usuário não encontrado"}, status=404)

        except Exception as e:
            return Response({"erro": str(e)}, status=400)

class atualizarUsuario(APIView):
    def patch(self, request, id):
        try:
            usuario = Usuario.objects.get(id_usuario=id)
            usuario.nome_usuario = request.data.get('nome', usuario.nome_usuario)
            usuario.email_usuario = request.data.get('email', usuario.email_usuario)

            senha = request.data.get('senha')
            if senha:
                usuario.senha_usuario = make_password(senha)

            usuario.nivel_usuario = request.data.get('nivelUsuario', usuario.nivel_usuario)

            usuario.save()

            return Response({
                "mensagem": "Usuário atualizado com sucesso"
            })

        except Usuario.DoesNotExist:
            return Response({"erro": "Usuário não encontrado"}, status=404)
        