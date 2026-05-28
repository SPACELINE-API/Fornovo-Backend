from django.shortcuts import render
from rest_framework.views import APIView
from django.db.models import Prefetch
from rest_framework.permissions import AllowAny, IsAuthenticated
from apps.usuarios.auth.permissions import IsAdm
from rest_framework.response import Response
from .models import Projeto, Arquivo, padraoStatus, EspecificacaoIA, ProjetoNorma, Notificacao, NotificacaoLeitura
from .services.notificacoes import (
    usuario_da_requisicao,
    registrar_novo_projeto,
    registrar_mudanca_status_projeto,
    registrar_arquivo_projeto,
    registrar_projetos_atrasados,
    popular_historico_inicial,
)
from .services.atividade import atividade_ultimos_meses
from django.core.exceptions import ValidationError
from apps.usuarios.models import Usuario
from .serializers import ProjetoSerializer, EspecificacaoIASerializer
from django.http import FileResponse
import hashlib

class cadastrarProjeto(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        engenheiro_id = request.data.get("engenheiro")
        serializer = ProjetoSerializer(data=request.data)

        if serializer.is_valid():
            try:

                usuario_selecionado = Usuario.objects.get(id_usuario=engenheiro_id)

                projeto = serializer.save(engenheiro=usuario_selecionado)
                registrar_novo_projeto(projeto, usuario_da_requisicao(request))

                return Response({
                        "mensagem": "Projeto criado com sucesso",
                        "dados": serializer.data
                    }, status=201)
            except Usuario.DoesNotExist:
                return Response({"erro": "O engenheiro selecionado não existe."}, status=400)
            except Exception as e:
                return Response({"erro": str(e)}, status=400)

        return Response(serializer.errors, status=400)

class listarProjetos(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projetos = Projeto.objects.all()
        serializer = ProjetoSerializer(projetos, many=True)

        return Response(serializer.data)   

class listarQuantidadeProjeto(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projetos = Projeto.objects.all()
        return Response({"total": projetos.count()})

class listarQuantidadeProjetoPorStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        projetos = Projeto.objects.all()
        return Response({
            "Concluído": projetos.filter(status="Concluído").count(),
            "Em andamento": projetos.filter(status="Em andamento").count(),
            "Em revisão": projetos.filter(status="Em revisão").count(),
            "Pendente": projetos.filter(status="Pendente").count(),
        })

class listarQuantidadeProjetoPorPrazo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contagem = Projeto.contagem_por_prazo()
        total = contagem['total']

        if total == 0:
            return Response({
                **contagem,
                'percentual_no_prazo': 0,
                'percentual_atrasados': 0,
            })

        return Response({
            **contagem,
            'percentual_no_prazo': round((contagem['no_prazo'] / total) * 100),
            'percentual_atrasados': round((contagem['atrasados'] / total) * 100),
        })

class listarTopNormasUtilizadas(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProjetoNorma.top_normas_utilizadas(limite=5))

class contagemNotificacoesNaoLidas(APIView):
    """Contagem para o badge do sino. Não marca como lida (task do dropdown)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nao_lidas = Notificacao.objects.exclude(
            notificacaoleitura__usuario=request.user
        ).count()
        return Response({'nao_lidas': nao_lidas})

class listarNotificacoes(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        popular_historico_inicial()
        registrar_projetos_atrasados()

        limite = min(int(request.query_params.get('limite', 20)), 50)
        notificacoes = Notificacao.listar_recentes(limite=limite).prefetch_related(
            Prefetch(
                'notificacaoleitura_set',
                queryset=NotificacaoLeitura.objects.filter(usuario=request.user),
                to_attr='leituras_do_usuario'
            )
        )

        return Response([
            {
                'id': n.id,
                'mensagem': n.mensagem,
                'tipo': n.tipo,
                'data': n.data_formatada(),
                'usuario': n.usuario,
                'lida': n.notificacaoleitura_set.filter(usuario=request.user).exists(),
            }
            for n in notificacoes
        ])

class alterarStatusNotificacao(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        notificacoes = Notificacao.objects.all()
        for notificacao in notificacoes:
            NotificacaoLeitura.objects.get_or_create(
            notificacao=notificacao,
            usuario=request.user
        )
        return Response({"mensagem": "Notificações marcadas como lidas."})

class listarAtividadeUltimosMeses(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        meses = min(int(request.query_params.get('meses', 6)), 12)
        return Response(atividade_ultimos_meses(meses=meses))

class buscarProjeto(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_projeto):
        projeto = Projeto.objects.get(id_projeto = id_projeto)
        serializer = ProjetoSerializer(projeto)

        return Response(serializer.data) 

class ProjetoDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)
            projeto.delete()
            return Response(status=204)

        except Projeto.DoesNotExist:
            return Response(
                {"erro": "Projeto não encontrado"},
                status=404
            )

class AtualizarStatusProjeto(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)

            novo_status = request.data.get("status")

            if novo_status not in dict(padraoStatus):
                return Response(
                    {"erro": "Status inválido"},
                    status=400
                )

            status_anterior = projeto.status
            projeto.status = novo_status
            projeto.save()

            if novo_status != status_anterior:
                registrar_mudanca_status_projeto(
                    projeto, novo_status, usuario_da_requisicao(request)
                )

            return Response({
                "mensagem": "Status atualizado com sucesso",
                "dados": ProjetoSerializer(projeto).data
            }, status=200)

        except Projeto.DoesNotExist:
            return Response(
                {"erro": "Projeto não encontrado"},
                status=404
            )

        except ValidationError as e:
            return Response(
                {"erro": str(e)},
                status=400
            )
        
class ProjetoUpdate(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)
            status_anterior = projeto.status

            serializer = ProjetoSerializer(
                projeto,
                data=request.data,
                partial=True
            )

            if serializer.is_valid():
                projeto = serializer.save()
                novo_status = projeto.status

                if novo_status != status_anterior:
                    registrar_mudanca_status_projeto(
                        projeto, novo_status, usuario_da_requisicao(request)
                    )

                return Response({
                    "mensagem": "Projeto atualizado com sucesso",
                    "dados": serializer.data
                })

            return Response(serializer.errors, status=400)

        except Projeto.DoesNotExist:
            return Response(
                {"erro": "Projeto não encontrado"},
                status=404
            )

class uploadArquivo(APIView): 
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            arquivo = request.FILES.get("arquivo")

            if not arquivo:
                return Response({"erro": "Nenhum arquivo enviado"}, status=400)

            projeto_id = request.data.get("projeto_id")
            if not projeto_id:
                return Response({"erro": "ID do projeto é obrigatório"}, status=400)

            projeto = Projeto.objects.get(id_projeto=projeto_id)

            ext_permitidas = ["pdf", "dwg", "dxf"]
            ext = arquivo.name.split(".")[-1].lower()

            if ext not in ext_permitidas:
                return Response({"erro": f"Extensão '{ext}' não permitida"}, status=400)

            hash_arquivo = hashlib.sha256(arquivo.read()).hexdigest()
            arquivo.seek(0)  

            novo_arquivo = Arquivo.objects.create(
                projeto=projeto,
                nome_arquivo=arquivo.name,
                caminho_arquivo=arquivo,
                tipo_arquivo=ext,
                hash_arquivo=hash_arquivo
            )
            registrar_arquivo_projeto(
                projeto, arquivo.name, ext, usuario_da_requisicao(request)
            )
            return Response({
                "mensagem": "Arquivo enviado com sucesso",
                "id_arquivo": novo_arquivo.id_arquivo,
                "nome": novo_arquivo.nome_arquivo,
                "caminho": novo_arquivo.caminho_arquivo.url,
                "tipo": novo_arquivo.tipo_arquivo,
                "hash": novo_arquivo.hash_arquivo,
                "projeto_id": str(novo_arquivo.projeto.id_projeto)
            }, status=201)

        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)

        except Exception as e:
            return Response({"erro": str(e)}, status=400)        

class verificarArquivo(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_projeto):
        arquivo = Arquivo.objects.filter(
            projeto_id=id_projeto
        ).first()

        if not arquivo:
            return Response(
                {"existe": False},
                status=404
            )

        return Response(
            {
                "existe": True,
                "id_arquivo": arquivo.id_arquivo,
                "nome_arquivo": arquivo.nome_arquivo,
                "tipo_arquivo": arquivo.tipo_arquivo,
                "hash_arquivo": arquivo.hash_arquivo
            },
            status=200
        )

class buscarArquivo(APIView): 
    permission_classes = [IsAuthenticated]
    def get(self, request, projeto_id):
        try:
            arquivo = Arquivo.objects.filter(projeto_id=projeto_id).first()

            if not arquivo:
                return Response({"error": "Nenhum arquivo vinculado ao projeto"}, status=404)

            if not arquivo.caminho_arquivo:
                return Response(
                    {"erro": "Arquivo não encontrado"},
                    status=404
                )

            baixar = request.GET.get("download") == "1"

            extensao = arquivo.nome_arquivo.split(".")[-1].lower()

            if extensao in ["dwg", "dxf"]:
                baixar = True

            if extensao == "pdf":
                content_type = "application/pdf"
            else:
                content_type = "application/octet-stream"

            return FileResponse(
                arquivo.caminho_arquivo.open("rb"),
                as_attachment=baixar,
                filename=arquivo.nome_arquivo,
                content_type=content_type
            )

        except Arquivo.DoesNotExist:
            return Response(
                {"erro": "Arquivo não encontrado"},
                status=404
            )
        
class deletarArquivo(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):
        try:
            arquivo = Arquivo.objects.get(id_arquivo=id)
            arquivo.caminho_arquivo.delete(save=False)
            arquivo.delete()
            return Response({"mensagem": "Arquivo deletado com sucesso"}, status=200)
        except Arquivo.DoesNotExist:
            return Response({"erro": "Arquivo não encontrado"}, status=404)

class VerificarStatusIA(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)
            return Response({
                "id_projeto": projeto.id_projeto,
                "status": projeto.status  
            })
        except Projeto.DoesNotExist:
            return Response({"erro": "Projeto não encontrado"}, status=404)


class UploadEspecificacao(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        arquivo = request.FILES.get('arquivo')
        projeto_id = request.data.get('projeto_id')
        titulo = request.data.get('titulo')
        versao = request.data.get('versao', '1.0')
        descricao = request.data.get('descricao', '')

        if not arquivo:
            return Response({'erro': 'Nenhum arquivo enviado.'}, status=400)

        if not projeto_id:
            return Response({'erro': 'projeto_id é obrigatório.'}, status=400)

        if not titulo:
            return Response({'erro': 'titulo é obrigatório.'}, status=400)

        EXTENSOES_WORD = {'docx', 'doc', 'docm', 'dotx', 'dotm', 'dot', 'odt', 'rtf'}
        ext = arquivo.name.rsplit('.', 1)[-1].lower()
        if ext not in EXTENSOES_WORD:
            return Response(
                {'erro': f"Extensão '{ext}' não permitida. Formatos aceitos: {', '.join(sorted(EXTENSOES_WORD))}."},
                status=400
            )

        try:
            projeto = Projeto.objects.get(id_projeto=projeto_id)
        except Projeto.DoesNotExist:
            return Response(
                {'erro': 'Projeto não encontrado. A especificação deve estar vinculada a um projeto existente.'},
                status=404
            )

        try:
            especificacao = EspecificacaoIA.objects.create(
                projeto=projeto,
                arquivo=arquivo,       
                titulo=titulo,
                versao=versao,
                descricao=descricao,
            )
        except Exception as e:
            return Response({'erro': f'Erro ao salvar especificação: {str(e)}'}, status=500)

        serializer = EspecificacaoIASerializer(especificacao, context={'request': request})
        return Response(
            {
                'mensagem': 'Especificação salva com sucesso.',
                'dados': serializer.data,
            },
            status=201
        )


class BaixarEspecificacao(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_especificacao):
        try:
            especificacao = EspecificacaoIA.objects.get(id_especificacao=id_especificacao)
        except EspecificacaoIA.DoesNotExist:
            return Response({'erro': 'Especificação não encontrada.'}, status=404)

        if request.GET.get('download') == '1':
            if not especificacao.arquivo:
                return Response({'erro': 'Arquivo não encontrado no servidor.'}, status=404)
            nome_arquivo = especificacao.arquivo.name.split('/')[-1]
            ext_download = nome_arquivo.rsplit('.', 1)[-1].lower()
            CONTENT_TYPES = {
                'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'docm': 'application/vnd.ms-word.document.macroEnabled.12',
                'dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
                'dotm': 'application/vnd.ms-word.template.macroEnabled.12',
                'dot':  'application/msword',
                'doc':  'application/msword',
                'odt':  'application/vnd.oasis.opendocument.text',
                'rtf':  'application/rtf',
            }
            content_type = CONTENT_TYPES.get(ext_download, 'application/octet-stream')
            return FileResponse(
                especificacao.arquivo.open('rb'),
                as_attachment=True,
                filename=nome_arquivo,
                content_type=content_type
            )

        serializer = EspecificacaoIASerializer(especificacao, context={'request': request})
        return Response(serializer.data, status=200)


class ListarEspecificacoes(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)
        except Projeto.DoesNotExist:
            return Response({'erro': 'Projeto não encontrado.'}, status=404)

        especificacoes = EspecificacaoIA.objects.filter(projeto=projeto)
        serializer = EspecificacaoIASerializer(
            especificacoes, many=True, context={'request': request}
        )
        return Response(serializer.data, status=200)


class DownloadEspecificacao(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_especificacao):
        try:
            especificacao = EspecificacaoIA.objects.get(id_especificacao=id_especificacao)
        except EspecificacaoIA.DoesNotExist:
            return Response({'erro': 'Especificação não encontrada.'}, status=404)

        if not especificacao.arquivo:
            return Response({'erro': 'Arquivo físico não encontrado no servidor.'}, status=404)

        nome_arquivo = especificacao.arquivo.name.split('/')[-1]
        ext = nome_arquivo.rsplit('.', 1)[-1].lower()

        CONTENT_TYPES = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'docm': 'application/vnd.ms-word.document.macroEnabled.12',
            'dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
            'dotm': 'application/vnd.ms-word.template.macroEnabled.12',
            'dot':  'application/msword',
            'doc':  'application/msword',
            'odt':  'application/vnd.oasis.opendocument.text',
            'rtf':  'application/rtf',
        }
        content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')

        return FileResponse(
            especificacao.arquivo.open('rb'),
            as_attachment=True,
            filename=nome_arquivo,
            content_type=content_type
        )


class DownloadUltimaEspecificacao(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_projeto):
        try:
            projeto = Projeto.objects.get(id_projeto=id_projeto)
        except Projeto.DoesNotExist:
            return Response({'erro': 'Projeto não encontrado.'}, status=404)

        especificacao = EspecificacaoIA.objects.filter(projeto=projeto).first()

        if not especificacao or not especificacao.arquivo:
            return Response(
                {'erro': 'Nenhuma especificação encontrada ou arquivo ausente para este projeto.'},
                status=404
            )

        nome_arquivo = especificacao.arquivo.name.split('/')[-1]
        ext = nome_arquivo.rsplit('.', 1)[-1].lower()

        CONTENT_TYPES = {
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'docm': 'application/vnd.ms-word.document.macroEnabled.12',
            'dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
            'dotm': 'application/vnd.ms-word.template.macroEnabled.12',
            'dot':  'application/msword',
            'doc':  'application/msword',
            'odt':  'application/vnd.oasis.opendocument.text',
            'rtf':  'application/rtf',
        }
        content_type = CONTENT_TYPES.get(ext, 'application/octet-stream')

        return FileResponse(
            especificacao.arquivo.open('rb'),
            as_attachment=True,
            filename=nome_arquivo,
            content_type=content_type
        )
