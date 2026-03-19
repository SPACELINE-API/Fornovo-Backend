from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Projeto

class cadastrarProjeto(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        nome = request.data.get('nome')
        engenheiro = request.data.get('engenheiro')
        cliente = request.data.get('cliente')
        localizacao = request.data.get('localizacao')
