import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0008_projeto_cep'),
    ]

    operations = [
        migrations.AddField(
            model_name='arquivo',
            name='criado_em',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('tipo', models.CharField(
                    choices=[
                        ('info', 'Info'),
                        ('sucesso', 'Sucesso'),
                        ('alerta', 'Alerta'),
                        ('erro', 'Erro'),
                    ],
                    default='info',
                    max_length=20,
                )),
                ('mensagem', models.TextField()),
                ('usuario', models.CharField(default='Sistema', max_length=100)),
                ('referencia_tipo', models.CharField(blank=True, max_length=50, null=True)),
                ('referencia_id', models.CharField(blank=True, max_length=100, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'notificacoes',
                'ordering': ['-criado_em'],
            },
        ),
    ]
