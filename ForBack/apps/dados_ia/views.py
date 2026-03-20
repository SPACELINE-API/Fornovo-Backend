from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def index(request):
    return HttpResponse("<h1>App Dados IA: Conexão bem-sucedida!</h1><p>Esta é a listagem de dados da IA do Fornovo.</p>")