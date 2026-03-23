from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Norma

class CriarNormaCompleta(APIView):
    def post(self, request):
            try:
                # 1. Pega o arquivo do PDF
                arquivo = request.FILES.get("arquivo_pdf")
                
                # 2. Pega os dados de texto
                codigo = request.data.get("codigo")
                nome = request.data.get("nome")
                ano = request.data.get("ano")
                serie = request.data.get("serie")
                descricao = request.data.get("descricao")

                # Validação básica
                if not codigo or not arquivo:
                    return Response({"erro": "Código e arquivo PDF são obrigatórios"}, status=400)

                # 3. Cria a Norma no banco já salvando o arquivo
                # O Django cuidará de mover o arquivo para a pasta 'normas_pdfs/'
                nova_norma = Norma.objects.create(
                    codigo=codigo,
                    nome=nome,
                    ano=ano,
                    serie=serie,
                    descricao=descricao,
                    arquivo_pdf=arquivo # O FileField recebe o objeto 'arquivo' diretamente
                )

                return Response({
                    "mensagem": "Norma e arquivo cadastrados com sucesso!",
                    "id_norma": nova_norma.id_norma,
                    "url_arquivo": nova_norma.arquivo_pdf.url # Retorna o link do PDF
                }, status=201)

            except Exception as e:
                return Response({"erro": str(e)}, status=400)