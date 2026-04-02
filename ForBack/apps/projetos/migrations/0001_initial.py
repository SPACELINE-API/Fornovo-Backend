
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('normas', '0001_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Projeto',
            fields=[
                ('id_projeto', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nome_projeto', models.CharField(max_length=200)),
                ('cliente', models.CharField(max_length=100)),
                ('localizacao', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(choices=[('Pendente', 'Pendente'), ('Em andamento', 'Em andamento'), ('Concluído', 'Concluído')], default='Pendente', max_length=50)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('data_fim', models.DateField(blank=True, null=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('engenheiro', models.ForeignKey(db_column='engenheiro_id', on_delete=django.db.models.deletion.CASCADE, to='usuarios.usuario')),
            ],
            options={
                'db_table': 'projetos',
            },
        ),
        migrations.CreateModel(
            name='Arquivo',
            fields=[
                ('id_arquivo', models.AutoField(primary_key=True, serialize=False)),
                ('nome_arquivo', models.CharField(max_length=255)),
                ('hash_arquivo', models.CharField(max_length=255, unique=True)),
                ('caminho_arquivo', models.FileField(upload_to='cad_arquivos/')),
                ('tipo_arquivo', models.CharField(max_length=50)),
                ('projeto', models.ForeignKey(db_column='projeto_id', on_delete=django.db.models.deletion.CASCADE, to='projetos.projeto')),
            ],
            options={
                'db_table': 'arquivos',
            },
        ),
        migrations.CreateModel(
            name='ProjetoNorma',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('norma', models.ForeignKey(db_column='norma_id', on_delete=django.db.models.deletion.CASCADE, to='normas.norma')),
                ('projeto', models.ForeignKey(db_column='projeto_id', on_delete=django.db.models.deletion.CASCADE, to='projetos.projeto')),
            ],
            options={
                'db_table': 'projeto_norma',
            },
        ),
        migrations.AddField(
            model_name='projeto',
            name='normas',
            field=models.ManyToManyField(related_name='projetos', through='projetos.ProjetoNorma', to='normas.norma'),
        ),
    ]
