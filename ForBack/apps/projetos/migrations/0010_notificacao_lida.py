from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0009_notificacao_arquivo_criado_em'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacao',
            name='lida',
            field=models.BooleanField(default=False),
        ),
    ]
