from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.usuarios.auth.permissions import IsAdm, IsAdmOrProjetista, IsAdmOrRevisor
from rest_framework.response import Response
from .models import Usuario
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings
import jwt
import datetime

# Create your views here.

class criarUsuario(APIView):
    permission_classes = [IsAuthenticated, IsAdm]
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

        except Exception as e:
            return Response({"erro": str(e)}, status=400)

class listarUsuario(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        usuarios = Usuario.objects.all()

        data = []
        for u in usuarios:
            if request.user.nivel_usuario != 'Administrador' and u.nivel_usuario == 'Administrador':
                continue
            data.append({
                "id": u.id_usuario,
                "nome": u.nome_usuario,
                "email": u.email_usuario,
                "nivelUsuario": u.nivel_usuario,
                "status": u.status
            })
        return Response(data)

class atualizarStatusUsuario(APIView):
    permission_classes = [IsAuthenticated, IsAdm]
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
    permission_classes = [IsAuthenticated, IsAdm]
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

class LoginUsuario(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        senha = request.data.get('senha')

        if not email or not senha:
            return Response({'erro': 'Email e senha são obrigatórios.'}, status=400)

        try:
            usuario = Usuario.objects.get(email_usuario=email)
        except Usuario.DoesNotExist:
            return Response({'erro': 'Credenciais inválidas.'}, status=401)

        if not check_password(senha, usuario.senha_usuario):
            return Response({'erro': 'Credenciais inválidas.'}, status=401)

        if usuario.status != 'Ativo':
            return Response({'erro': 'Usuário inativo.'}, status=403)

        payload = {
            'id_usuario': str(usuario.id_usuario),
            'nivel_usuario': usuario.nivel_usuario,
            'nome_usuario': usuario.nome_usuario,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        return Response({
            'mensagem': 'Login realizado com sucesso.',
            'token': token
        }, status=200)
