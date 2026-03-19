from django.db import models
import uuid

class Usuario(models.Model):
    id_usuario = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    nome_usuario = models.CharField(max_length=120)
    email_usuario = models.EmailField(max_length=150, unique=True)
    senha_usuario = models.CharField(max_length=255)
    nivel_usuario = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Ativo')

    class Meta:
        db_table = "usuarios"

    def __str__(self):
        return self.nome_usuario