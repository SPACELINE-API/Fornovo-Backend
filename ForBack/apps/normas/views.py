import hashlib
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Norma

class CriarNormaCompleta(APIView):
    def post(self, request):
        try:
            # Pega o arquivo e os dados enviados na requisição
            arquivo = request.FILES.get("arquivo_pdf")
            codigo = request.data.get("codigo")
            nome = request.data.get("nome")
            ano = request.data.get("ano")
            serie = request.data.get("serie")
            descricao = request.data.get("descricao")

            # Verifica se os campos obrigatórios foram preenchidos
            if not arquivo or not codigo or not ano:
                return Response({"erro": "Arquivo, código e ano são obrigatórios"}, status=400)

            # Bloqueia o cadastro se já existir uma norma com o mesmo código, ano e série
            if Norma.objects.filter(codigo=codigo, ano=ano, serie=serie).exists():
                return Response({"erro": "Já existe uma norma cadastrada com este código, ano e série."}, status=400)

            # Verifica se a extensão do arquivo é pdf e se o tipo do arquivo é válido
            ext = arquivo.name.split(".")[-1].lower()
            if ext != "pdf" or arquivo.content_type != "application/pdf":
                return Response({"erro": "Apenas arquivos PDF válidos são permitidos"}, status=400)

            # Gera um código único baseado no conteúdo do arquivo (hash)
            hash_arquivo = hashlib.sha256(arquivo.read()).hexdigest()
            # Volta a leitura do arquivo para o início para poder salvar depois
            arquivo.seek(0)

            # Bloqueia se o mesmo arquivo PDF já tiver sido enviado em outra norma
            if Norma.objects.filter(hash_arquivo=hash_arquivo).exists():
                return Response({"erro": "Este arquivo PDF já foi enviado em outra norma."}, status=400)

            # Define o nome do arquivo usando o código, ano e série, removendo espaços
            nome_limpo = f"{codigo}_{ano}"
            if serie:
                nome_limpo += f"_{serie}"
            
            # Força o nome do arquivo para o padrão definido com final .pdf
            arquivo.name = f"{nome_limpo.replace(' ', '_')}.pdf"

            # Salva a nova norma no banco de dados com todos os dados e o arquivo
            nova_norma = Norma.objects.create(
                codigo=codigo,
                nome=nome,
                ano=ano,
                serie=serie,
                descricao=descricao,
                arquivo_pdf=arquivo,
                hash_arquivo=hash_arquivo
            )

            # Retorna mensagem de sucesso e os dados da norma criada
            return Response({
                "mensagem": "Norma e arquivo cadastrados com sucesso!",
                "id_norma": nova_norma.id_norma,
                "nome_final": arquivo.name,
                "url_arquivo": nova_norma.arquivo_pdf.url
            }, status=201)

        except Exception as e:
            # Caso ocorra qualquer erro inesperado, retorna o erro
            return Response({"erro": str(e)}, status=400)