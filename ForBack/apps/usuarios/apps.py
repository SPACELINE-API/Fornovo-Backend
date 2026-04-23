from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'

    def ready(self):
        import sys
        import os

        # Evita executar fora do servidor ou durante o reloader (para não imprimir duplicado)
        if 'runserver' not in sys.argv or os.environ.get('RUN_MAIN') != 'true':
            return

        from .models import Usuario
        from django.contrib.auth.hashers import make_password
        
        try:
            if not Usuario.objects.filter(nivel_usuario='adm').exists():
                Usuario.objects.create(
                    nome_usuario='Administrador',
                    email_usuario='adm',
                    senha_usuario=make_password('adm'),
                    nivel_usuario='adm',
                    status='Ativo'
                )
            # Imprime sempre que o servidor inicia e o acesso ao db está ok
            print(">>> Banco de dados: OK")
        except Exception as e:
            print(f">>> Erro ao conectar ao banco de dados: {e}")