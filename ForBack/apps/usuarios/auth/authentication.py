import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from ..models import Usuario

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return None

        try:
            prefix, token = auth_header.split(' ')
            if prefix.lower() != 'bearer':
                return None
        except ValueError:
            raise AuthenticationFailed('Formato do token inválido.')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token inválido.')

        try:
            usuario = Usuario.objects.get(id_usuario=payload['id_usuario'])
        except Usuario.DoesNotExist:
            raise AuthenticationFailed('Usuário não encontrado.')

        if usuario.status != 'Ativo':
            raise AuthenticationFailed('Usuário inativo.')

        return (usuario, token)


    def authenticate_header(self, request):
        return 'Bearer realm="api"'
