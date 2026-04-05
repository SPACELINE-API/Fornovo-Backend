from rest_framework import serializers
from .models import Projeto

class ProjetoSerializer(serializers.ModelSerializer):
    engenheiro_nome = serializers.ReadOnlyField(source='engenheiro.nome_usuario')

    class Meta:
        model = Projeto
        fields = [
            'id_projeto',
            'nome_projeto',
            'descricao',
            'cliente',
            'localizacao',
            'status',
            'data_inicio',
            'data_fim',
            'engenheiro',
            'engenheiro_nome'
        ]

        extra_kwargs = {
            'engenheiro': {
                'required': False
            }
        }