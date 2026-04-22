from rest_framework.permissions import BasePermission

class IsAdm(BasePermission):
    """
    Permite acesso apenas a usuários com nível 'adm'.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'adm')

class IsProjetista(BasePermission):
    """
    Permite acesso apenas a usuários com nível 'projetista'.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'projetista')

class IsRevisor(BasePermission):
    """
    Permite acesso apenas a usuários com nível 'revisor'.
    """
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'nivel_usuario') and request.user.nivel_usuario == 'revisor')

class IsAdmOrProjetista(BasePermission):
    """
    Permite acesso a 'adm' ou 'projetista' (níveis mais altos).
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            hasattr(request.user, 'nivel_usuario') and 
            request.user.nivel_usuario in ['adm', 'projetista']
        )

class IsAdmOrRevisor(BasePermission):
    """
    Permite acesso a 'adm' ou 'revisor'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            hasattr(request.user, 'nivel_usuario') and 
            request.user.nivel_usuario in ['adm', 'revisor']
        )
