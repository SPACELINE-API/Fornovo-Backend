from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>App Cálculos: Conexão bem-sucedida!</h1><p>Esta é a listagem de cálculos do Fornovo.</p>")
