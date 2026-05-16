import os
import subprocess
import tempfile
import traceback
import ctypes
import pickle
import re 
from pathlib import Path

from aiohttp import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser
from django.http import FileResponse, HttpResponse, JsonResponse
import time
import hashlib
from django.core.files.base import ContentFile

from .models import DadosExtraidos, LogValidacao, DadosInseridosManualmente, RelatorioConformidade
from apps.projetos.models import Projeto, Norma, Arquivo, ProjetoNorma
from .services import (chroma_normas as agente, oda_installer as oda, extractorDXF as extractor, 
                       ollama_installer)
from .services.chroma_normas import inserir_norma, apagar_norma
from .services.ollama_execute import executar_agente
import json
import threading
from rest_framework import status

from .utils.relatorio import gerar_docx_bytes

from apps.dados_ia.services.memorial.pandas.builder import gerar_memorial

_lock = threading.Lock()

BASE_DIR = Path(__file__).resolve().parents[2]
MEDIA_PATH = BASE_DIR / "media" / "nbr-pdf"

def ExtrairSalvarNormas(normas_codigos: list, projeto):
    try:
        from apps.normas.models import Norma as NormaCadastrada
        from apps.projetos.models import ProjetoNorma

        if not normas_codigos:
            print("Nenhuma norma utilizada na análise (ChromaDB vazio).")
            return

        print(f"Vinculando normas ao projeto: {normas_codigos}")

        for codigo in normas_codigos:
            codigo = codigo.strip()
            # busca no banco pelo código exato
            norma_bd = NormaCadastrada.objects.filter(codigo__iexact=codigo).first()
            nome_vinculo = norma_bd.codigo if norma_bd else codigo
            ProjetoNorma.objects.create(projeto=projeto, norma=nome_vinculo)
            print(f"Norma '{nome_vinculo}' vinculada com sucesso no banco!")

    except Exception as e:
        print(f"Erro ao vincular normas: {e}")


class ConverterArquivo(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        arquivo = request.FILES.get("arquivo")
        if not arquivo:
            return Response(
                {"erro": "Nenhum arquivo enviado. Use o campo 'arquivo'."},
                status=400
            )

        nome_arquivo = arquivo.name.lower()

        if not (nome_arquivo.endswith(".dwg") or nome_arquivo.endswith(".dxf")):
            return Response(
                {"erro": "Formato inválido. Envie um arquivo .dwg ou .dxf."},
                status=400
            )

        input_dir = Path(tempfile.mkdtemp())
        output_dir = Path(tempfile.mkdtemp())

        try:
            file_path = input_dir / arquivo.name

            with open(file_path, "wb") as f:
                for chunk in arquivo.chunks():
                    f.write(chunk)

            if nome_arquivo.endswith(".dxf"):
                try:
                    dados_extraidos = extractor.processar_dxf_para_json(
                        str(file_path),
                        gerar_chunks=True
                    )
                    return Response(dados_extraidos, status=200)

                except Exception as e:
                    return Response({
                        "erro": "Falha ao processar o arquivo DXF.",
                        "detalhe": str(e)
                    }, status=500)

            if not oda.is_oda_ready():
                iniciado = oda.install_as_admin()
                if not iniciado:
                    return Response({
                        "erro": "Falha ao solicitar privilégios de administrador."
                    }, status=500)

                return Response({
                    "mensagem": "Instalação do ODA iniciada. Aceite o prompt UAC e reenvie a requisição."
                }, status=202)

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

            dxf_path = dxf_files[0]

            try:
                dados_extraidos = extractor.processar_dxf_para_json(
                    str(dxf_path),
                    gerar_chunks=True
                )
            except Exception as e:
                return Response({
                    "erro": "Conversão concluída, mas falha na extração do DXF.",
                    "detalhe": str(e)
                }, status=500)

            return Response(dados_extraidos, status=200)

        finally:
            for f in input_dir.iterdir():
                f.unlink()
            input_dir.rmdir()

            for f in output_dir.iterdir():
                f.unlink()
            output_dir.rmdir()


class ProcessarProjetoIA(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        projeto_id = request.data.get("projeto_id")
        if not projeto_id:
            return Response({"erro": "O campo 'projeto_id' é obrigatório."}, status=400)

        try:
            projeto = Projeto.objects.get(id_projeto=projeto_id)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado."}, status=404)

        arquivo = Arquivo.objects.filter(projeto=projeto).last()
        if not arquivo:
            return Response({"erro": "Nenhum arquivo CAD associado (RN.1)."}, status=404)

        try:
            start_time = time.time()
            arquivo_path = str(arquivo.caminho_arquivo.path)
            dxf_path = arquivo_path

            input_dir = None
            output_dir = None
            
            if arquivo_path.lower().endswith(".dwg"):
                if not oda.is_oda_ready():
                    return Response({"erro": "Conversor ODA não instalado."}, status=500)
                
                input_dir = Path(tempfile.mkdtemp())
                output_dir = Path(tempfile.mkdtemp())
                
                dwg_temp_path = input_dir / Path(arquivo_path).name
                with open(arquivo_path, "rb") as o_f, open(dwg_temp_path, "wb") as n_f:
                    n_f.write(o_f.read())

                result = subprocess.run(
                    [str(oda.ODA_EXE), str(input_dir), str(output_dir), "ACAD2018", "DXF", "0", "1"],
                    capture_output=True, text=True, timeout=120
                )
                
                dxf_files = list(output_dir.glob("*.dxf"))
                if not dxf_files:
                    for f in input_dir.iterdir(): f.unlink()
                    input_dir.rmdir()
                    for f in output_dir.iterdir(): f.unlink()
                    output_dir.rmdir()
                    return Response({"erro": "Conversão DWG->DXF do servidor falhou."}, status=500)
                
                dxf_path = str(dxf_files[0])
            
            try:
                dados_json = extractor.processar_dxf_para_json(str(dxf_path), gerar_chunks=False)
            except Exception as e:
                return Response({
                    "erro": "Falha na extração de geometria (arquivo corrompido ou inválido, CA.3)",
                    "detalhe": str(e)
                }, status=422)
            finally:
                if input_dir and input_dir.exists():
                    for f in input_dir.iterdir(): f.unlink()
                    input_dir.rmdir()
                if output_dir and output_dir.exists():
                    for f in output_dir.iterdir(): f.unlink()
                    output_dir.rmdir()
            
            try:
                ollama_installer.ensure_ollama_ready(['llama3.1:8b'])
                retorno_ia = executar_agente(dados_json)
            except Exception as e:
                return Response({"erro": "Falha na execução do agente da IA", "detalhe": str(e)}, status=500)

            relatorio_md = retorno_ia.get("relatorio_md", "")
            if relatorio_md:
                try:
                    nome = f"relatorio_{str(projeto_id)[:8]}.docx"
                    docx_bytes = gerar_docx_bytes(relatorio_md)
                    relatorio = RelatorioConformidade(projeto=projeto)
                    relatorio.arquivo.save(nome, ContentFile(docx_bytes), save=False)
                    relatorio.nome_arquivo = nome
                    relatorio.caminho_arquivo = relatorio.arquivo.name
                    relatorio.save()
                except Exception as e:
                    print(f"Erro ao salvar relatório: {e}")
                    
                normas_codigos = retorno_ia.get("normas_chroma_codigos", [])
                ExtrairSalvarNormas(normas_codigos, projeto)
            
            response_time = time.time() - start_time
            if response_time > 60:
                print(f"Alerta: A extração e o processamento (Motor de IA Ollama) demoraram mais do que o normal ({response_time:.2f} s).")

            dados_bd = DadosExtraidos.objects.create(arquivo=arquivo, dados=dados_json)
            
            insights_bd = []
            for item in retorno_ia.get("insights", []):
                n_codigo = item.get("norma_codigo", "")
                norma_obj = Norma.objects.filter(codigo__icontains=n_codigo).first()
                if not norma_obj:
                    norma_obj = Norma.objects.first()
                    
                if norma_obj:
                    log = LogValidacao.objects.create(projeto=projeto, norma=norma_obj, dados=item)
                    insights_bd.append(log.id_log)

            retorno_ia["dados_extraidos_id"] = dados_bd.id_dados
            retorno_ia["validacoes_logs_ids"] = insights_bd
            retorno_ia["tempo_resposta"] = round(response_time, 2)

            return Response(retorno_ia, status=200)

        except Exception as generic_e:
            import traceback
            traceback.print_exc()
            return Response({"erro": "Falha interna do Motor de Processamento", "detalhe": str(generic_e)}, status=500)

class DownloadRelatorio(APIView):
    def get(self, request):
        projeto_id = request.query_params.get("projeto_id")

        if not projeto_id:
            return Response({"erro": "O parâmetro 'projeto_id' é obrigatório"}, status=400)

        try:
            projeto = Projeto.objects.get(id_projeto=projeto_id)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado."}, status=404)

        relatorio = RelatorioConformidade.objects.filter(projeto=projeto).order_by('criado_em').last()

        if not relatorio:
            return Response({"erro": "Nenhum relatório encontrado."}, status=404)
        
        if not relatorio.caminho_arquivo:
            return Response({"erro": "Arquivo físico não encontrado."}, status=404)
        
        return FileResponse(
            relatorio.arquivo.open("rb"),
            as_attachment=True,
            filename=relatorio.nome_arquivo,
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )


class StatusRelatorio(APIView):
    def get(self, request):
        projeto_id = request.query_params.get("projeto_id")

        if not projeto_id:
            return Response({"erro": "O parâmetro 'projeto_id' é obrigatório"}, status=400)

        try:
            projeto = Projeto.objects.get(id_projeto=projeto_id)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado."}, status=404)

        relatorio = RelatorioConformidade.objects.filter(projeto=projeto).order_by('criado_em').first()

        if not relatorio:
            return Response({"status": "pendente"})
        
        return Response({"status": "concluido"})

class historicoRelatorio(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        projeto_id = request.query_params.get("projeto_id")

        if not projeto_id:
            return Response(
                {"erro": "O parâmetro 'projeto_id' é obrigatório"},
                status=400
            )

        try:
            projeto = Projeto.objects.get(id_projeto=projeto_id)
        except Projeto.DoesNotExist:
            return Response(
                {"erro": "Projeto não encontrado."},
                status=404
            )

        relatorios = (
            RelatorioConformidade.objects
            .filter(projeto=projeto)
            .order_by("-criado_em")
        )

        data = []

        for relatorio in relatorios:
            data.append({
                "id": relatorio.id,
                "nome_arquivo": relatorio.nome_arquivo,
                "criado_em": relatorio.criado_em,
            })

        return Response(data)
    

    def post(self, request):
        projeto_id = request.data.get("projeto_id")
        arquivo = request.FILES.get("arquivo")

        if not projeto_id:
            return Response(
                {"erro": "projeto_id é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not arquivo:
            return Response(
                {"erro": "arquivo é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            projeto = Projeto.objects.get(id_projeto=projeto_id)
        except Projeto.DoesNotExist:
            return Response(
                {"erro": "Projeto não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        relatorio = RelatorioConformidade.objects.create(
            projeto=projeto,
            nome_arquivo=arquivo.name,
            caminho_arquivo=f"relatorios/{arquivo.name}",
            arquivo=arquivo
        )

        return Response(
            {
                "mensagem": "Nova versão enviada",
                "relatorio_id": relatorio.id
            },
            status=status.HTTP_201_CREATED
        )

        
class inserirNorma(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    @staticmethod
    def decodificar_se_bytes(valor):
            if isinstance(valor, bytes):
                return valor.decode('utf-8')
            if isinstance(valor, list) and len(valor) > 0:
                item = valor[0]
                return item.decode('utf-8') if isinstance(item, bytes) else item
            return valor

    def post(self, request):

        codigo = self.decodificar_se_bytes(request.data.get("codigo"))
        nome = self.decodificar_se_bytes(request.data.get("nome"))
        ano = self.decodificar_se_bytes(request.data.get("ano"))
        serie = self.decodificar_se_bytes(request.data.get("serie"))
        descricao = self.decodificar_se_bytes(request.data.get("descricao"))

        meta_data = {
            "codigo": codigo,
            "nome": nome,
            "ano": ano,
            "serie": serie,
            "descricao": descricao
        }

        print("Metadados decodificados:", meta_data)

        arquivo = request.FILES.get("arquivo_pdf")

        if not arquivo:
            return Response({"erro": "Nenhum arquivo enviado."}, status=400)

        if getattr(arquivo, 'name', None) and not arquivo.name.lower().endswith(".pdf"):
            return Response({"erro": "Formato inválido. O arquivo deve ser um PDF."}, status=400)

        tmp_dir = Path(tempfile.mkdtemp())
        tmp_path = tmp_dir / arquivo.name
        resultado_insercao = {}

        try:
            with open(tmp_path, "wb") as f:
                for chunk in arquivo.chunks():
                    f.write(chunk)

            with _lock:
                resultado_insercao = inserir_norma(str(tmp_path), metadados=meta_data)
                print(resultado_insercao)

        except Exception as e:
            return Response({"erro": "Falha ao processar o arquivo", "detalhe": str(e)}, status=500)

        finally:
            if tmp_path.exists():
                tmp_path.unlink()
            if tmp_dir.exists():
                tmp_dir.rmdir()

        return Response({
            "resultados": [{
                "arquivo": arquivo.name,
                **resultado_insercao
            }]
        }, status=200)

    def delete(self, request, id):
        try:
            if not id:
                return Response({"erro":"erro de id"}, status = 400)
            
            try:
                norma = Norma.objects.get(id_norma = id)
            except Norma.DoesNotExist:
                return Response({"erro":"norma não encontrada"}, status=400)

            codigo = norma.codigo
            resultado = apagar_norma(codigo)

            if resultado:
                return Response({
                    "mensagem": "Norma removida com sucesso.",
                    "codigo": codigo
                }, status=200)

            return Response({
                "erro": "Falha ao remover no ChromaDB.",
                "codigo": codigo
            }, status=500)

        except Exception as e:
            return Response({
                "erro": "Falha ao remover a norma.",
                "detalhe": str(e)
            }, status=500)

class ativarNorma(APIView):
    permission_classes = [AllowAny]

    def post(self, request, id):
        try:
            if not id:
                return Response({"erro":"erro de id"}, status = 400)
            
            try:
                norma = Norma.objects.get(id_norma = id)
            except Norma.DoesNotExist:
                return Response({"erro":"norma não encontrada"}, status=400)

            norma = Norma.objects.get(id_norma = id)

            meta_data = {
            "codigo": norma.codigo,
            "nome": norma.nome,
            "ano": norma.ano,
            "serie": norma.serie,
            "descricao": norma.descricao
            }

            pdf_nome = Path(str(norma.arquivo_pdf)).name.lower()

            arquivo_encontrado = next(
                (f.resolve() for f in MEDIA_PATH.iterdir()
                if f.is_file() and f.name.lower() == pdf_nome),
                None)

            if not arquivo_encontrado:
                return Response({"erro": "arquivo PDF não encontrado no /media"}, status=404)

            resultado_insercao = inserir_norma(
                str(arquivo_encontrado),
                metadados=meta_data
            )

            if not resultado_insercao.get("ok"):
                return Response({"erro": "Falha ao inserir norma no ChromaDB",
                "resultado": resultado_insercao}, status=500)

            return Response({
                "mensagem": "Norma ativada com sucesso",
                "arquivo": pdf_nome,
                "resultado_insercao": {
                    "ok": resultado_insercao.get("ok"),
                    "chunks_inseridos": resultado_insercao.get("chunks_inseridos"),
                    "lotes": resultado_insercao.get("lotes")
                }
            }, status=200)         
            
        except Exception as e:
            return Response({
                "erro": "Falha ao ativar a norma.",
                "detalhe": str(e)
            }, status=500)


class SalvarMemorialCalculo(APIView):
    parser_classes = [MultiPartParser, JSONParser]

    def _parse_json_field(self, request, key):
        arquivo = request.FILES.get(key)
        if arquivo:
            return json.loads(arquivo.read().decode("utf-8"))
        valor = request.data.get(key)
        if valor:
            if isinstance(valor, str):
                return json.loads(valor)
            return valor
        return None

    def post(self, request, *args, **kwargs):
        try:
            projeto_id = request.data.get("projeto_id")
            if not projeto_id:
                return Response({"erro": "O campo 'projeto_id' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                projeto = Projeto.objects.get(id_projeto=projeto_id)
            except Projeto.DoesNotExist:
                return Response({"erro": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

            dados_arquivo = self._parse_json_field(request, "arquivo")
            dados_dxf = self._parse_json_field(request, "dxf")

            if not dados_arquivo:
                return Response({"erro": "Envie o JSON manual no campo 'arquivo'."}, status=status.HTTP_400_BAD_REQUEST)

            if not dados_dxf:
                return Response({"erro": "Envie o JSON do DXF no campo 'dxf'."}, status=status.HTTP_400_BAD_REQUEST)

            arquivo = gerar_memorial(dados_arquivo, dados_dxf)

            if not arquivo:
                return Response({"erro": "Falha na geração do arquivo Excel."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            arquivo.seek(0)
            arquivo_bytes = arquivo.getvalue()

            nome_arquivo = f"memorial_calculo_{projeto_id[:8]}.xlsx"
            hash_arquivo = hashlib.sha256(arquivo_bytes).hexdigest()

            novo_arquivo = Arquivo.objects.create(
                projeto=projeto,
                nome_arquivo=nome_arquivo,
                hash_arquivo=hash_arquivo,
                tipo_arquivo='xlsx',
                caminho_arquivo=ContentFile(arquivo_bytes, name=nome_arquivo)
            )

            return Response({
                "mensagem": "Memorial de cálculo salvo com sucesso!",
                "id_arquivo": novo_arquivo.id_arquivo,
                "nome_arquivo": novo_arquivo.nome_arquivo
            }, status=status.HTTP_201_CREATED)

        except json.JSONDecodeError as e:
            return Response({"erro": "JSON inválido.", "detalhe": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        try:
            projeto_id = request.query_params.get("projeto_id")
            if not projeto_id:
                return Response({"erro": "O parâmetro 'projeto_id' é obrigatório na URL (query string)."}, status=status.HTTP_400_BAD_REQUEST)

            arquivo = Arquivo.objects.filter(projeto_id=projeto_id, tipo_arquivo='xlsx').last()

            if not arquivo:
                return Response({"erro": "Nenhum memorial de cálculo salvo para este projeto."}, status=status.HTTP_404_NOT_FOUND)

            if not arquivo.caminho_arquivo:
                return Response({"erro": "Arquivo físico não encontrado."}, status=status.HTTP_404_NOT_FOUND)

            return FileResponse(
                arquivo.caminho_arquivo.open("rb"),
                as_attachment=True,
                filename=arquivo.nome_arquivo,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StatusMemCal(APIView):
    def get(self, request): 
        projeto_id = request.query_params.get("projeto_id")
        
        if not projeto_id:
            return Response({"erro": "O parâmetro 'projeto_id' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            arquivos = Arquivo.objects.filter(projeto_id=projeto_id, tipo_arquivo='xlsx')
            
            if arquivos.exists():
                return Response({
                    "status": "concluido", 
                    "mensagem": "Memorial de cálculo já gerado e salvo."
                })
            else:
                return Response({
                    "status": "pendente", 
                    "mensagem": "Memorial de cálculo ainda não gerado ou salvo."
                })
        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ConsultarDadosProcessadosIA(APIView):
    permission_classes = [AllowAny]

    def carregar_dados(self, raw_data):
        if isinstance(raw_data, memoryview):
            raw_data = bytes(raw_data)

        try:
            import zlib
            raw_data = zlib.decompress(raw_data)
        except Exception:
            pass

        try:
            return pickle.loads(raw_data)
        except Exception:
            pass

        try:
            return json.loads(raw_data)
        except Exception:
            pass

        try:
            return json.loads(raw_data.decode("utf-8"))
        except Exception:
            pass

        try:
            primeiro = json.loads(raw_data.decode("utf-8"))
            if isinstance(primeiro, str):
                return json.loads(primeiro)
        except Exception:
            pass

        raise ValueError("Formato de dados desconhecido")

    def get(self, request, projeto_id):
        try:
            dados_obj = DadosExtraidos.objects.get(
                arquivo__projeto_id=projeto_id
            )

            raw_data = dados_obj.dados_binarios
            dados_final = self.carregar_dados(raw_data)

            if not isinstance(dados_final, dict):
                raise ValueError("Dados não são um objeto JSON válido")

            return Response(
                {
                    "status": "concluido",
                    "dados_dxf": dados_final,
                },
                status=status.HTTP_200_OK,
            )

        except DadosExtraidos.DoesNotExist:
            return Response(
                {
                    "status": "pendente",
                    "mensagem": "A IA ainda não processou este projeto.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            print(traceback.format_exc())
            return Response(
                {
                    "erro": "Falha ao carregar dados DXF",
                    "detalhe": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )