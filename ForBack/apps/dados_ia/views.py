import os
import subprocess
import tempfile
import ctypes
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser
from django.http import FileResponse, HttpResponse
import json
import threading
import time

from .models import DadosExtraidos, LogValidacao, DadosInseridosManualmente
from apps.projetos.models import Projeto, Norma, Arquivo
from .services import (chroma_normas as agente, oda_installer as oda, extractorDXF as extractor, 
                       ollama_installer)
from .services.chroma_normas import inserir_norma
from .services.ollama_execute import executar_agente
import json
from django.http import HttpResponse
import threading
from .services.memorial.levantamento_campo import extrair_levantamento_campo_para_xlsx, mesclar_form_com_dxf
from rest_framework import status
from django.http import FileResponse


from .services import oda_installer as oda, extractorDXF as extractor
from .services import ollama_installer
from .services.ollama_execute import executar_agente
from .services.chroma_normas import inserir_norma
from .services.memorial.serviços_preliminares import extrair_servicos_preliminares_para_xlsx
from .services.memorial.memorial_calculo import extrair_memorial_calculo
from .services.memorial.movimento_solo import extrair_movimento_solo

import sys

_lock = threading.Lock()

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

        # Buscar projeto
        try:
            projeto = Projeto.objects.get(id_projeto=projeto_id)
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado."}, status=404)

        # Atualizando status via CA.4 e Timeout handling implícito por endpoint longo
        projeto.status = 'Em andamento'
        projeto.save()

        # RN.1: Verificar o arquivo CAD importado
        arquivo = Arquivo.objects.filter(projeto=projeto).last()
        if not arquivo:
            projeto.status = 'Pendente'
            projeto.save()
            return Response({"erro": "Nenhum arquivo CAD associado (RN.1)."}, status=404)

        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(BASE_DIR, "services", "oda_installer.py")
            
            start_time = time.time()
            arquivo_path = str(arquivo.caminho_arquivo.path)
            dxf_path = arquivo_path

            input_dir = None
            output_dir = None
            if arquivo_path.lower().endswith(".dwg"):
                subprocess.Popen([sys.executable, script_path])
                
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
            
            # Disparar a extração de dados (CA.3 trata a geometria inválida ou corrupção)
            try:
                dados_json = extractor.processar_dxf_para_json(str(dxf_path), gerar_chunks=False)
            except Exception as e:
                projeto.status = 'Pendente'
                projeto.save()
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

            # Enviar dados ao IA Module Real (Ollama Ollama_execute)
            normas_projeto = projeto.normas.all()
            
            try:
                ollama_installer.ensure_ollama_ready()
                retorno_ia = executar_agente(dados_json)
            except Exception as e:
                projeto.status = 'Pendente'
                projeto.save()
                return Response({"erro": "Falha na execução do agente da IA", "detalhe": str(e)}, status=500)
            
            # Timeouts monitorados - Logs (CA.4 time monitoring)
            response_time = time.time() - start_time
            if response_time > 60:
                print(f"Alerta: A extração e o processamento (Motor de IA Ollama) demoraram mais do que o normal ({response_time:.2f} s).")

            # Serviços de Salvamento - Tabelas de IA
            # Utilizar o model correto salvando no DB
            dados_bd = DadosExtraidos.objects.create(arquivo=arquivo, dados=dados_json)
            
            insights_bd = []
            for item in retorno_ia.get("insights", []):
                n_codigo = item.get("norma_codigo", "")
                norma_obj = normas_projeto.filter(codigo__icontains=n_codigo).first()
                if not norma_obj and normas_projeto.exists():
                    norma_obj = normas_projeto.first()
                    
                if norma_obj:
                    # Associação de insights (CA.2)
                    log = LogValidacao.objects.create(projeto=projeto, norma=norma_obj, dados=item)
                    insights_bd.append(log.id_log)
                    
            # Setando projeto concluído CA.4 endpoint terminando o processamento
            projeto.status = 'Concluído'
            projeto.save()

            retorno_ia["dados_extraidos_id"] = dados_bd.id_dados
            retorno_ia["validacoes_logs_ids"] = insights_bd
            retorno_ia["tempo_resposta"] = round(response_time, 2)

            return Response(retorno_ia, status=200)

        except Exception as generic_e:
            projeto.status = 'Pendente'
            projeto.save()
            return Response({"erro": "Falha interna do Motor de Processamento", "detalhe": str(generic_e)}, status=500)


class executarAgente(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        arquivo = request.FILES.get("arquivo")

        if not arquivo:
            return Response({"erro": "Nenhum arquivo enviado. Use o campo 'arquivo'."}, status=400)

        if not arquivo.name.lower().endswith(".json"):
            return Response({"erro": "Formato inválido. Envie um arquivo .json."}, status=400)

        try:
            dados_extracao = json.loads(arquivo.read().decode("utf-8"))
        except Exception as e:
            return Response({"erro": "Falha ao ler o JSON.", "detalhe": str(e)}, status=400)

        ollama_installer.ensure_ollama_ready()

        try:
            resultado_ia = executar_agente(dados_extracao)
            relatorio_md = resultado_ia.get("relatorio_md", "Erro ao processar.")
        except Exception as e:
            return Response({"erro": "Falha na execução do agente.", "detalhe": str(e)}, status=500)

        response = HttpResponse(relatorio_md, content_type="text/markdown; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="relatorio_conformidade.md"'
        return response


class inserirNorma(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        arquivos = request.FILES.getlist("norma")

        if not arquivos:
            return Response({"erro": "Nenhum arquivo enviado."}, status=400)

        resultados = []

        for arquivo in arquivos:
            if not arquivo.name.lower().endswith(".pdf"):
                resultados.append({
                    "arquivo": arquivo.name,
                    "erro": "Formato inválido"
                })
                continue

            tmp_dir = Path(tempfile.mkdtemp())
            tmp_path = tmp_dir / arquivo.name

            try:
                with open(tmp_path, "wb") as f:
                    for chunk in arquivo.chunks():
                        f.write(chunk)

                with _lock:
                    resultado = inserir_norma(str(tmp_path))

                resultados.append({
                    "arquivo": arquivo.name,
                    **resultado
                })

            finally:
                if tmp_path.exists():
                    tmp_path.unlink()
                if tmp_dir.exists():
                    tmp_dir.rmdir()

        return Response({
            "resultados": resultados
        }, status=207)

class GerarPlanilhaEletrica(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def post(self, request):
        arquivo = request.FILES.get("arquivo")

        if not arquivo:
            return Response({"erro": "Nenhum arquivo enviado. Use o campo 'arquivo'."}, status=400)

        if not arquivo.name.lower().endswith(".json"):
            return Response({"erro": "Formato inválido. Envie um arquivo .json."}, status=400)

        try:
            dados_extracao = json.loads(arquivo.read().decode("utf-8"))
        except Exception as e:
            return Response({"erro": "Falha ao ler o JSON.", "detalhe": str(e)}, status=400)

        try:
            caminho_csv = p.extrair_dados_eletricos_para_csv(dados_extracao)
        except Exception as e:
            return Response({"erro": "Falha ao processar os dados elétricos.", "detalhe": str(e)}, status=500)

        try:
            with open(caminho_csv, 'rb') as f:
                response = HttpResponse(f.read(), content_type="text/csv; charset=utf-8")
                nome_arquivo_download = os.path.basename(caminho_csv)
                response["Content-Disposition"] = f'attachment; filename="{nome_arquivo_download}"'
                            
            return response

        except Exception as e:
            return Response({"erro": "Falha ao disponibilizar o arquivo para download.", "detalhe": str(e)}, status=500)

# class GerarMemorialCalculo(APIView):
#     permission_classes = [AllowAny]
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         try:
#             arquivo = request.FILES.get("arquivo")
            
#             if arquivo:
#                 dados_json = json.loads(arquivo.read().decode("utf-8"))
#             else:
#                 dados_json = request.data
                
#             if not dados_json:
#                 return Response({"erro": "Dados não fornecidos"}, status=400)

#             arquivo_bytes = p2.gerar_memorial_completo(dados_json)

#             response = HttpResponse(
#                 arquivo_bytes,
#                 content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )

#             response["Content-Disposition"] = 'attachment; filename="memorial.xlsx"'

#             return response

#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             return Response({"erro": str(e)}, status=500)

class GerarPlanilhaLevantamentoAPIView(APIView):
    parser_classes = [MultiPartParser]

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
            dados_arquivo = self._parse_json_field(request, "arquivo")
            dados_dxf = self._parse_json_field(request, "dxf")

            if not dados_arquivo:
                return Response({"erro": "Envie o JSON manual no campo 'arquivo'."}, status=status.HTTP_400_BAD_REQUEST)
            if not dados_dxf:
                return Response({"erro": "Envie o JSON do DXF no campo 'dxf'."}, status=status.HTTP_400_BAD_REQUEST)

            dados_mesclados = mesclar_form_com_dxf(dados_arquivo, dados_dxf)

            arquivo_bytes = extrair_levantamento_campo_para_xlsx(dados_mesclados)
            if not arquivo_bytes:
                return Response({"erro": "Falha na geração do arquivo Excel em memória."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            response = HttpResponse(
                arquivo_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="levantamento_campo_unificado.xlsx"'
            return response

        except json.JSONDecodeError as e:
            return Response({"erro": "JSON inválido.", "detalhe": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExtrairDadosDXFAPIView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        from .services.memorial.extrair_dados_dxf import extrair_dados_completos_dxf

        try:
            dxf_file = request.FILES.get("dxf")
            if not dxf_file:
                return Response({"erro": "Envie o JSON do DXF no campo 'dxf'."}, status=status.HTTP_400_BAD_REQUEST)

            dados_dxf = json.loads(dxf_file.read().decode("utf-8"))
            resultado = extrair_dados_completos_dxf(dados_dxf)
            return Response(resultado, status=status.HTTP_200_OK)

        except json.JSONDecodeError as e:
            return Response({"erro": "JSON inválido.", "detalhe": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DebugEletricaView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        try:
            dxf_file = request.FILES.get("dxf")
            if not dxf_file:
                return Response({"erro": "Envie o JSON do DXF no campo 'dxf'."}, status=400)
            dados = json.loads(dxf_file.read().decode("utf-8"))

            from .services.memorial.levantamento_campo import _extrair_dxf_por_ambiente, _extrair_ambientes_super

            entidades = dados.get("entidades", [])
            textos = dados.get("textos", []) or [e for e in entidades if e.get("tipo") in ("MTEXT", "TEXT")]
            blocos = dados.get("blocos", [])
            ambientes = _extrair_ambientes_super(textos)
            ambientes = [a for a in ambientes if a.get("area", 0) > 0]

            dxf_por_amb = _extrair_dxf_por_ambiente(entidades, textos, blocos, ambientes)

            saida = []
            for amb in ambientes:
                nome = amb.get("nome", "")
                dxf = dxf_por_amb.get(nome, {})
                ele = dxf.get("eletrica", {})
                saida.append({
                    "ambiente": nome,
                    "area_m2": amb.get("area"),
                    "quadros": ele.get("quadros"),
                    "conduletes": ele.get("conduletes"),
                    "tomadas": ele.get("tomadas"),
                    "interruptores": ele.get("interruptores"),
                    "luminarias": ele.get("luminarias"),
                    "dutos_m": ele.get("dutos_m"),
                    "cabos_m": ele.get("cabos_m"),
                })

            for s in saida:
                print(f"AMBIENTE: {s['ambiente']} | area={s['area_m2']}m² | quadros={s['quadros']} | conduletes={s['conduletes']} | tomadas={s['tomadas']} | interruptores={s['interruptores']} | luminarias={s['luminarias']} | dutos={s['dutos_m']}m | cabos={s['cabos_m']}m")

            return Response({"ambientes": saida, "total": len(saida)})

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=500)


class GerarPlanilhaServicosPreliminaresAPIView(APIView):
    parser_classes = [MultiPartParser] 

    def post(self, request, *args, **kwargs):
        try:
            arquivo = request.FILES.get("arquivo")
            
            if arquivo:
                dados = json.loads(arquivo.read().decode("utf-8"))
            else:
                dados = request.data
                
            if not dados:
                return Response({"erro": "Nenhum dado ou arquivo JSON fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
            arquivo_bytes = extrair_servicos_preliminares_para_xlsx(dados)
            
            if not arquivo_bytes:
                return Response({"erro": "Falha na geração do arquivo Excel em memória."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            response = HttpResponse(
                arquivo_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="servicos_preliminares.xlsx"'
            
            return response
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MemorialCalculo(APIView):
    parser_classes = [MultiPartParser]

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
            dados_arquivo = self._parse_json_field(request, "arquivo")
            dados_dxf = self._parse_json_field(request, "dxf")

            if not dados_arquivo:
                return Response({"erro": "Envie o JSON manual no campo 'arquivo'."}, status=status.HTTP_400_BAD_REQUEST)
            if not dados_dxf:
                return Response({"erro": "Envie o JSON do DXF no campo 'dxf'."}, status=status.HTTP_400_BAD_REQUEST)

            dados_mesclados = mesclar_form_com_dxf(dados_arquivo, dados_dxf)

            arquivo_bytes = extrair_memorial_calculo(dados_mesclados)
            if not arquivo_bytes:
                return Response({"erro": "Falha na geração do arquivo Excel em memória."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            response = HttpResponse(
                arquivo_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="memorial_calculo_completo.xlsx"'
            return response

        except json.JSONDecodeError as e:
            return Response({"erro": "JSON inválido.", "detalhe": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GerarPlanilhaMovimentoSolo(APIView):
    parser_classes = [MultiPartParser] 

    def post(self, request, *args, **kwargs):
        try:
            arquivo = request.FILES.get("arquivo")
            
            if arquivo:
                dados = json.loads(arquivo.read().decode("utf-8"))
            else:
                dados = request.data
                
            if not dados:
                return Response({"erro": "Nenhum dado ou arquivo JSON fornecido."}, status=status.HTTP_400_BAD_REQUEST)
            
            arquivo_bytes = extrair_movimento_solo(dados)
            
            if not arquivo_bytes:
                return Response({"erro": "Falha na geração do arquivo Excel em memória."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            response = HttpResponse(
                arquivo_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Altera o nome do ficheiro de saída
            response["Content-Disposition"] = 'attachment; filename="movimento_solo.xlsx"'
            
            return response
            
        except Exception as e:
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class deletarArquivo(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, id):
        try:
            arquivo = Arquivo.objects.get(id_arquivo=id)
            arquivo.caminho_arquivo.delete(save=False)
            arquivo.delete()

            return Response({
                "mensagem": "Arquivo deletado com sucesso"
            })

        except Arquivo.DoesNotExist:
            return Response({"erro": "Arquivo não encontrado"}, status=404)
