from rest_framework import serializers
from .models import Projeto

class ProjetoSerializer(serializers.ModelSerializer):
    engenheiro_nome = serializers.CharField(
        source='engenheiro.nome_usuario', 
        read_only=True, 
        default="Não atribuído"
    )
    engenheiro_nivel = serializers.CharField(
        source='engenheiro.nivel_usuario', 
        read_only=True, 
        default="N/A"
    )

    class Meta:
        model = Projeto
        fields = [
            'id_projeto', 'nome_projeto', 'descricao', 'cliente', 
            'localizacao', 'status', 'data_inicio', 'data_fim', 
            'engenheiro', 'engenheiro_nome', 'engenheiro_nivel'
        ]