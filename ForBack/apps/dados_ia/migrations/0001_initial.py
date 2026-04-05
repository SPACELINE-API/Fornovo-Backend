
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('normas', '0001_initial'),
        ('projetos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DadosExtraidos',
            fields=[
                ('id_dados', models.AutoField(primary_key=True, serialize=False)),
                ('dados_binarios', models.BinaryField(blank=True, null=True)),
                ('arquivo', models.ForeignKey(db_column='arquivo_id', on_delete=django.db.models.deletion.CASCADE, to='projetos.arquivo')),
            ],
            options={
                'db_table': 'dados_extraidos',
            },
        ),
        migrations.CreateModel(
            name='DadosInseridosManualmente',
            fields=[
                ('id_dados', models.AutoField(primary_key=True, serialize=False)),
                ('dados', models.JSONField()),
                ('projeto', models.ForeignKey(db_column='projeto_id', on_delete=django.db.models.deletion.CASCADE, to='projetos.projeto')),
            ],
            options={
                'db_table': 'dados_inseridos_manualmente',
            },
        ),
        migrations.CreateModel(
            name='LogValidacao',
            fields=[
                ('id_log', models.AutoField(primary_key=True, serialize=False)),
                ('dados', models.JSONField()),
                ('norma', models.ForeignKey(db_column='norma_id', on_delete=django.db.models.deletion.CASCADE, to='normas.norma')),
                ('projeto', models.ForeignKey(db_column='projeto_id', on_delete=django.db.models.deletion.CASCADE, to='projetos.projeto')),
            ],
            options={
                'db_table': 'logs_validacao',
            },
        ),
    ]
