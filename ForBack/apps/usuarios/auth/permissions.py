from rest_framework.permissions import BasePermission

class IsAdm(BasePermission):
    """
    Permite acesso apenas a usuários com nível 'Administrador'.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'Administrador')

class IsProjetista(BasePermission):
    """
    Permite acesso apenas a usuários com nível 'Projetista'.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'Projetista')

class IsRevisor(BasePermission):
    """
    Permite acesso apenas a usuários com nível 'Revisor'.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'Revisor')

class IsAdmOrProjetista(BasePermission):
    """
    Permite acesso a 'Administrador' ou 'Projetista' (níveis mais altos).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            hasattr(request.user, 'nivel_usuario') and 
            request.user.nivel_usuario in ['Administrador', 'Projetista']
        )

class IsAdmOrRevisor(BasePermission):
    """
    Permite acesso a 'Administrador' ou 'Revisor'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            hasattr(request.user, 'nivel_usuario') and 
            request.user.nivel_usuario in ['Administrador', 'Revisor']
        )
