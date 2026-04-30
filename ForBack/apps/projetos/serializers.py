from rest_framework import serializers
from .models import Projeto, EspecificacaoIA

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
            'cep', 'localizacao', 'status', 'data_inicio', 'data_fim', 
            'engenheiro', 'engenheiro_nome', 'engenheiro_nivel'
        ]


class EspecificacaoIASerializer(serializers.ModelSerializer):
    arquivo_url = serializers.SerializerMethodField()
    projeto_nome = serializers.CharField(source='projeto.nome_projeto', read_only=True)

    class Meta:
        model = EspecificacaoIA
        fields = [
            'id_especificacao',
            'projeto',
            'projeto_nome',
            'titulo',
            'versao',
            'descricao',
            'arquivo',
            'arquivo_url',
            'gerado_em',
        ]
        read_only_fields = ['id_especificacao', 'gerado_em', 'arquivo_url', 'projeto_nome']

    def get_arquivo_url(self, obj):
        request = self.context.get('request')
        if obj.arquivo and request:
            return request.build_absolute_uri(obj.arquivo.url)
        return None