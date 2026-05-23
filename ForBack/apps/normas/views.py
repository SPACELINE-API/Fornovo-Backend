import hashlib
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse
from rest_framework import status
from .models import Norma
from apps.projetos.services.notificacoes import (
    usuario_da_requisicao,
    registrar_norma_criada,
    registrar_norma_atualizada,
    registrar_norma_status,
)

class CriarNormaCompleta(APIView):
    def post(self, request):
        try:
            arquivo = request.FILES.get("arquivo_pdf")
            codigo = request.data.get("codigo")
            nome = request.data.get("nome")
            ano = request.data.get("ano")
            serie = request.data.get("serie")
            descricao = request.data.get("descricao")

            if not arquivo or not codigo or not ano:
                return Response({"erro": "Arquivo, nome, código e ano são obrigatórios"}, status=400)

            if Norma.objects.filter(codigo=codigo, ano=ano, serie=serie).exists():
                return Response({"erro": "Já existe uma norma cadastrada com este código, ano e série."}, status=400)

            ext = arquivo.name.split(".")[-1].lower()
            if ext != "pdf" or arquivo.content_type != "application/pdf":
                return Response({"erro": "Apenas arquivos PDF válidos são permitidos"}, status=400)

            hash_arquivo = hashlib.sha256(arquivo.read()).hexdigest()
            arquivo.seek(0)

            if Norma.objects.filter(hash_arquivo=hash_arquivo).exists():
                return Response({"erro": "Este arquivo PDF já foi enviado em outra norma."}, status=400)

            nome_limpo = f"{codigo}_{ano}"
            if serie:
                nome_limpo += f"_{serie}"
            
            arquivo.name = f"{nome_limpo.replace(' ', '_')}.pdf"

            nova_norma = Norma.objects.create(
                codigo=codigo,
                nome=nome,
                ano=ano,
                serie=serie,
                descricao=descricao,
                arquivo_pdf=arquivo,
                hash_arquivo=hash_arquivo
            )
            registrar_norma_criada(nova_norma, usuario_da_requisicao(request))

            return Response({
                "mensagem": "Norma e arquivo cadastrados com sucesso!",
                "id_norma": nova_norma.id_norma,
                "nome_final": arquivo.name,
                "url_arquivo": nova_norma.arquivo_pdf.url
            }, status=201)

        except Exception as e:
            return Response({"erro": str(e)}, status=400)

class AlterarStatusNorma(APIView):
    def patch(self, request, id_norma):
        try:
            novo_status = request.data.get("status")  

            if novo_status not in ["ativo", "inativo"]: 
                return Response(
                    {"erro": "Status inválido, apenas 'ativo' ou 'inativo'."},
                    status=400
                )

            norma = Norma.objects.get(id_norma=id_norma) 

            if norma.status == novo_status: 
                return Response(
                    {"mensagem": f"A norma já está {norma.status}."},
                    status=400
                )
                
            norma.status = novo_status 
            norma.save()
            registrar_norma_status(norma, usuario_da_requisicao(request))

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
            norma = Norma.objects.get(id_norma=id_norma) 

            if norma.status != "ativo": 
                return Response(
                    {"erro": "Esta norma está inativo e não pode ser acessado."},
                    status=403
                )

            if not norma.arquivo_pdf: 
                return Response({"erro": "Arquivo não encontrado"}, status=404)

            baixar = request.GET.get("download") == "1" 

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

class ListarNormas(APIView):
    def get(self, request):
        normas = Norma.objects.all()
        lista_normas = [
            {
                "id_norma": norma.id_norma,
                "codigo": norma.codigo,
                "nome": norma.nome,
                "ano": norma.ano,
                "serie": norma.serie,
                "descricao": norma.descricao,
                "status": norma.status,
                "url_arquivo": norma.arquivo_pdf.url if norma.arquivo_pdf else None
            }
            for norma in normas
        ]
        return Response(lista_normas, status=200)
    
class listarQuantidadeNorma(APIView):
    def get(self, request):
        normas = Norma.objects.all()
        return Response({"total": normas.count()}, status=200)
    
class EditarDetsNorma(APIView):
    def patch(self, request, id_norma):
        try:
            norma = Norma.objects.get(id_norma=id_norma)
            codigo = request.data.get("codigo")
            nome = request.data.get("nome")
            ano = request.data.get("ano")
            serie = request.data.get("serie")
            descricao = request.data.get("descricao")
            arquivo_novo = request.FILES.get("arquivo_pdf")
            remover_arquivo = request.data.get("remover_arquivo")

            if codigo:
                norma.codigo = codigo

            if nome:
                norma.nome = nome

            if ano:
                norma.ano = ano

            if serie is not None:
                norma.serie = serie

            if descricao is not None:
                norma.descricao = descricao

            if remover_arquivo == "true":
                if norma.arquivo_pdf:
                    norma.arquivo_pdf.delete(save=False)
                    norma.arquivo_pdf = None

            if arquivo_novo:

                ext = arquivo_novo.name.split(".")[-1].lower()

                if ext != "pdf" or arquivo_novo.content_type != "application/pdf":
                    return Response(
                        {"erro": "Apenas arquivos PDF válidos são permitidos"},
                        status=400
                    )
                hash_arquivo = hashlib.sha256(
                    arquivo_novo.read()
                ).hexdigest()

                arquivo_novo.seek(0)
                if Norma.objects.filter(hash_arquivo=hash_arquivo)\
                        .exclude(id_norma=id_norma)\
                        .exists():

                    return Response(
                        {"erro": "Este arquivo PDF já foi enviado em outra norma."},
                        status=400
                    )
                if norma.arquivo_pdf:
                    norma.arquivo_pdf.delete(save=False)
                nome_limpo = f"{norma.codigo}_{norma.ano}"

                if norma.serie:
                    nome_limpo += f"_{norma.serie}"

                arquivo_novo.name = (
                    f"{nome_limpo.replace(' ', '_')}.pdf"
                )

                norma.arquivo_pdf = arquivo_novo
                norma.hash_arquivo = hash_arquivo

            norma.save()
            registrar_norma_atualizada(norma, usuario_da_requisicao(request))

            return Response({
                "mensagem": "Detalhes da norma atualizados com sucesso!",
                "id_norma": norma.id_norma,
                "codigo": norma.codigo,
                "nome": norma.nome,
                "ano": norma.ano,
                "serie": norma.serie,
                "descricao": norma.descricao,
                "status": norma.status,
                "url_arquivo": norma.arquivo_pdf.url if norma.arquivo_pdf else None
            }, status=200)

        except Norma.DoesNotExist:
            return Response(
                {"erro": "Norma não encontrada."},
                status=404
            )
