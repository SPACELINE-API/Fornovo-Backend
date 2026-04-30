from rest_framework.permissions import BasePermission

class IsAdm(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'Administrador')

class IsProjetista(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'Projetista')

class IsRevisor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'Revisor')


