import os
import subprocess
import tempfile
import ctypes
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from django.http import FileResponse

from .models import DadosExtraidos, LogValidacao, DadosInseridosManualmente
from apps.projetos.models import Projeto, Norma, Arquivo
from .services import oda_installer as oda


class CadastrarDadosExtraidos(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            arquivo_id = request.data.get("arquivo")
            dados = request.data.get("dados")
            arquivo = Arquivo.objects.get(id_arquivo=arquivo_id)
            extraido = DadosExtraidos.objects.create(arquivo=arquivo, dados=dados)
            return Response({"mensagem": "Dados extraídos cadastrados com sucesso", "id": extraido.id_dados}, status=201)
        except Arquivo.DoesNotExist:
            return Response({"erro": "Arquivo não encontrado"}, status=404)
        except Exception as e:
            return Response({"erro": str(e)}, status=400)

    def get(self, request):
        dados = DadosExtraidos.objects.all()
        lista = [
            {"id_dados": item.id_dados, "arquivo": item.arquivo.id_arquivo, "dados": item.dados}
            for item in dados
        ]
        return Response(lista)


class CadastrarLogValidacao(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            projeto_id = request.data.get("projeto")
            norma_id = request.data.get("norma")
            dados = request.data.get("dados")
            projeto = Projeto.objects.get(id_projeto=projeto_id)
            norma = Norma.objects.get(id_norma=norma_id)
            log = LogValidacao.objects.create(projeto=projeto, norma=norma, dados=dados)
            return Response({"mensagem": "Log de validação criado com sucesso", "id": log.id_log}, status=201)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)
        except Norma.DoesNotExist:
            return Response({"erro": "Norma não encontrada"}, status=404)
        except Exception as e:
            return Response({"erro": str(e)}, status=400)


class CadastrarDadosManuais(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            projeto_id = request.data.get("projeto")
            dados = request.data.get("dados")
            projeto = Projeto.objects.get(id_projeto=projeto_id)
            manual = DadosInseridosManualmente.objects.create(projeto=projeto, dados=dados)
            return Response({"mensagem": "Dados manuais inseridos com sucesso", "id": manual.id_dados}, status=201)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)
        except Exception as e:
            return Response({"erro": str(e)}, status=400)


class ConverterArquivo(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        arquivo_dwg = request.FILES.get("arquivo")
        if not arquivo_dwg:
            return Response({"erro": "Nenhum arquivo enviado. Use o campo 'arquivo'."}, status=400)

        if not arquivo_dwg.name.lower().endswith(".dwg"):
            return Response({"erro": "Formato inválido. Envie um arquivo .dwg."}, status=400)

        if not oda.is_oda_ready():
            iniciado = oda.install_as_admin()
            if not iniciado:
                return Response({"erro": "Falha ao solicitar privilégios de administrador."}, status=500)
            return Response({
                "mensagem": "Instalação do ODA iniciada. Aceite o prompt UAC e reenvie a requisição."
            }, status=202)

        input_dir = Path(tempfile.mkdtemp())
        output_dir = Path(tempfile.mkdtemp())

        try:
            dwg_path = input_dir / arquivo_dwg.name
            with open(dwg_path, "wb") as f:
                for chunk in arquivo_dwg.chunks():
                    f.write(chunk)

            result = subprocess.run(
                [
                    str(oda.ODA_EXE),
                    str(input_dir),
                    str(output_dir),
                    "ACAD2018",
                    "DXF",
                    "0",
                    "1",
                ],
                capture_output=True,
                text=True,
                timeout=120
            )

            dxf_files = list(output_dir.glob("*.dxf"))

            if not dxf_files:
                return Response({
                    "erro": "Nenhum arquivo DXF gerado.",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                }, status=500)

            dxf_content = dxf_files[0].read_bytes()
            dxf_name = dxf_files[0].name

            from django.http import HttpResponse
            response = HttpResponse(dxf_content, content_type="application/octet-stream")
            response["Content-Disposition"] = f'attachment; filename="{dxf_name}"'
            return response

        finally:
            for f in input_dir.iterdir():
                f.unlink()
            input_dir.rmdir()
            for f in output_dir.iterdir():
                f.unlink()
            output_dir.rmdir()



            