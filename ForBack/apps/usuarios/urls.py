from django.urls import path
from . import views
from .views import criarUsuario, listarUsuario, atualizarStatusUsuario, atualizarUsuario
app_name = 'usuarios'

urlpatterns = [
    path('listarUsuario', listarUsuario.as_view()),
    path('criarUsuario', criarUsuario.as_view()),
    path('status/<uuid:id>', atualizarStatusUsuario.as_view()),
    path('editarUsuario/<uuid:id>', atualizarUsuario.as_view())
    
]