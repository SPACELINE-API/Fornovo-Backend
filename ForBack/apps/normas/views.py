import hashlib
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
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
                return Response({"erro": "Arquivo, nome, código e ano são obrigatórios"}, status=400)

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
                "id_norma": nova_norma.id,
                "nome_final": arquivo.name,
                "url_arquivo": nova_norma.arquivo_pdf.url
            }, status=201)

        except Exception as e:
            # Caso ocorra qualquer erro inesperado, retorna o erro
            return Response({"erro": str(e)}, status=400)

class AlterarStatusNorma(APIView):
    def patch(self, request, id_norma):
        try:
            novo_status = request.data.get("status")  # Puxa o status enviado

            if novo_status not in ["ativa", "inativa"]: # Validação
                return Response(
                    {"erro": "Status inválido, apenas 'ativa' ou 'inativa'."},
                    status=400
                )

            norma = Norma.objects.get(id_norma=id_norma) # Busca norma

            if norma.status == novo_status: # Verifica se o status já está no estado solicitado
                return Response(
                    {"mensagem": f"A norma já está {norma.status}."},
                    status=400
                )
                
            norma.status = novo_status # Atualiza o status porque é diferente
            norma.save()

            return Response({
                "mensagem": "Status atualizado com sucesso!",
                "id_norma": norma.id_norma,
                "status_atual": norma.status
            }, status=200)

        except Norma.DoesNotExist:
            return Response({"erro": "Norma não encontrada."}, status=404)

class VisualizarOuBaixarNorma(APIView):
    def get(self, request, id_norma):
        try:
            norma = Norma.objects.get(id_norma=id_norma) # Puxa norma

            if norma.status != "ativo": # Se estiver inativo, bloqueia
                return Response(
                    {"erro": "Esta norma está inativa e não pode ser acessada."},
                    status=403
                )

            if not norma.arquivo_pdf: # Erro se não encontrar
                return Response({"erro": "Arquivo não encontrado"}, status=404)

            baixar = request.GET.get("download") == "1" # Se foi solicitado download, baixa

            filename = (
                f"{norma.codigo}:{norma.ano}:{norma.serie}.pdf"
                if norma.serie
                else f"{norma.codigo}:{norma.ano}.pdf"
            )

            return FileResponse(
                norma.arquivo_pdf.open("rb"),
                as_attachment=baixar,
                filename=filename,
                content_type="application/pdf"
            )

        except Norma.DoesNotExist:
            return Response({"erro": "Norma não encontrada"}, status=404)