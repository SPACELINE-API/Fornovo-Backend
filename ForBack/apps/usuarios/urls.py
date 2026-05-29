from django.urls import path
from . import views
from .views import criarUsuario, listarUsuario, atualizarStatusUsuario, atualizarUsuario, LoginUsuario, listarQuantidadeUsuario
app_name = 'usuarios'

urlpatterns = [
    path('listarUsuario', listarUsuario.as_view()),
    path('criarUsuario', criarUsuario.as_view()),
    path('status/<uuid:id>', atualizarStatusUsuario.as_view()),
    path('editarUsuario/<uuid:id>', atualizarUsuario.as_view()),
    path('quantidadeUsuario', listarQuantidadeUsuario.as_view()),
    path('login', LoginUsuario.as_view(), name='login')
]