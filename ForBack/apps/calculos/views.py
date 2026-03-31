from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import (
    Projeto, Ambiente, PontoEletrico, Cabo, Disjuntor, TipoEletrico, Ramal, 
    Hidraulica, Reservatorio, SPDA, Telecom, Cabeamento, Extintor, Hidrante, 
    Duto, Cobertura, Peca, Canteiro, Residuo, Escavacao, Volume, Fundacao, 
    SuperEstrutura, EstruturaMetalica, EstruturaMadeira
)

from django.http import HttpResponse
import io
import os 
from django.conf import settings
from django.db import transaction
import json
from rest_framework.parsers import MultiPartParser

try:
    from apps.dados_ia.services.memorial.levantamento_campo import (
    extrair_levantamento_campo_para_xlsx,
    mesclar_form_com_dxf,
)
except ImportError:
    extrair_levantamento_campo_para_xlsx = None

def to_int(value):
    return int(value) if value not in ["", None] else 0

def to_float(value):
    return float(value) if value not in ["", None] else 0.0

class levantamentoCampo(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        try:
           with transaction.atomic():
            projeto_id = data.get("projeto_id")
            if not projeto_id:
                return Response({"error": "projeto_id é obrigatório"}, status=400)
            try:
                projeto = Projeto.objects.get(id_projeto=projeto_id)
            except Projeto.DoesNotExist:
                return Response({"error": "Projeto não encontrado"}, status=404)
            ambiente = Ambiente.objects.create(
                nome=data.get("nome"),
                comprimento=to_float(data.get("comprimento")),
                largura=to_float(data.get("largura")),
                altura=to_float(data.get("altura")),
                area=to_float(data.get("comprimento")) * to_float(data.get("largura")),
                projeto=projeto
            )

            PontoEletrico.objects.create(
                ambiente=ambiente,
                tomadas=to_int(data.get("tomadas")),
                pontos_iluminacao=to_int(data.get("iluminacao")),
                interruptores=to_int(data.get("interruptores")),
            )

            for cabo in data.get("cabos", []):
                Cabo.objects.create(
                    ambiente=ambiente,
                    circuito=cabo.get("circuito"),
                    secao_mm2=to_float(cabo.get("secao"))
                )

            for d in data.get("disjuntores", []):
                Disjuntor.objects.create(
                    ambiente=ambiente,
                    amperagem=to_float(d.get("amperagem")),
                    quantidade=to_int(d.get("quantidade"))
                )

            TipoEletrico.objects.create(
                ambiente=ambiente,
                tipo_tomada=data.get("tipoTomada"),
                tipo_interruptor=data.get("tipoInterruptor"),
                tipo_luminaria=data.get("tipoLuminaria"),
                altura_instalacao=to_float(data.get("alturaInstalacao"))
            )

            for r in data.get("ramais", []):
                Ramal.objects.create(
                    ambiente=ambiente,
                    nome=r.get("nome"),
                    diametro=r.get("diametro"),
                    comprimento_m=to_float(r.get("comprimento"))
                )

            Hidraulica.objects.create(
                ambiente=ambiente,
                registros=to_int(data.get("registros")),
                valvulas=to_int(data.get("valvulas")),
                conexoes=to_int(data.get("conexoes"))
            )

            reservat = data.get("reservatorio", {})
            if reservat:
                Reservatorio.objects.create(
                    ambiente=ambiente,
                    tipo=reservat.get("tipo"),
                    capacidade_l=to_float(reservat.get("capacidade"))
                )

            SPDA.objects.create(
                ambiente=ambiente,
                hastes=to_int(data.get("hastesAterramento")),
                caixas_inspecao=to_int(data.get("caixasInspecao")),
                terminais_aereos=to_int(data.get("terminaisAereos"))
            )

            Telecom.objects.create(
                ambiente=ambiente,
                quadros_rede=to_int(data.get("quadrosRede")),
                patch_cords=to_int(data.get("patchCords")),
                cameras=to_int(data.get("cameras"))
            )

            for cab in data.get("cabeamentos", []):
                Cabeamento.objects.create(
                    ambiente=ambiente,
                    circuito=cab.get("circuito"),
                    comprimento_m=to_float(cab.get("comprimento")),
                    tomadas=to_int(cab.get("tomadas"))
                )

            for e in data.get("extintores", []):
                Extintor.objects.create(
                    ambiente=ambiente,
                    tipo=e.get("tipo"),
                    peso_kg=to_float(e.get("peso")),
                    capacidade_l=to_float(e.get("capacidade"))
                )

            for h in data.get("hidrantes", []):
                Hidrante.objects.create(
                    ambiente=ambiente,
                    localizacao=h.get("localizacao"),
                    diametro=h.get("diametro"),
                    conexoes=to_int(h.get("conexoes"))
                )
            for duto in data.get("dutos", []):
                Duto.objects.create(
                    ambiente=ambiente,
                    diametro=duto.get("diametro"),
                    comprimento_m=to_float(duto.get("comprimento"))
                )

            Cobertura.objects.create(
                ambiente=ambiente,
                estrutura=data.get("tipoEstrutura"),
                telhamento=data.get("tipoTelhamento"),
                espessura_cm=to_float(data.get("espessura")),
                inclinacao_percent=to_float(data.get("inclinacao")),
            )

            for p in data.get("pecas", []):
                Peca.objects.create(
                    ambiente=ambiente,
                    descricao=p.get("descricao"),
                    secao=p.get("secao")
                )

            Canteiro.objects.create(
                ambiente=ambiente,
                conteineres=to_int(data.get("conteineres")),
                banheiros=to_int(data.get("banheirosQuimicos")),
                andaimes=to_int(data.get("andaimes")),
            )

            Residuo.objects.create(
                ambiente=ambiente,
                comum_m3=to_float(data.get("residuoComum")),
                contaminado_m3=to_float(data.get("residuoContaminado")),
                destinacao=data.get("destinacaoResiduo"),
            )

            Escavacao.objects.create(
                ambiente=ambiente,
                profundidade_m=to_float(data.get("profundidadeEscavacao")),
                inclinacao_percent=to_float(data.get("inclinacaoTerreno")),
            )

            v = data.get("volumes", {})
            if v:
                Volume.objects.create(
                    ambiente=ambiente,
                    terraplanagem_m3=to_float(v.get("terraplanagem")),
                    escavacao_m3=to_float(v.get("escavacao")),
                    aterro_m3=to_float(v.get("aterro")),
                    enrocamento_m3=to_float(v.get("enrocamento")),
                    contencao_m3=to_float(v.get("contencao")),
                    taludamento_m3=to_float(v.get("taludamento")),
                    nivelamento_m3=to_float(v.get("nivelamento")),
                    compactacao_m3=to_float(v.get("compactacao")),
                )

            for f in data.get("fundacoes", []):
                Fundacao.objects.create(
                    ambiente=ambiente,
                    tipo=f.get("tipo"),
                    profundidade_m=to_float(f.get("profundidade")),
                    volume_lastro_m3=to_float(f.get("volumeLastro")),
                    volume_concreto_m3=to_float(f.get("volumeConcreto")),
                    ferragem_kgf=to_float(f.get("pesoFerragem")),
                    estribo_kgf=to_float(f.get("pesoEstribo")),
                    forma_m2=to_float(f.get("areaForma")),
                )

            for s in data.get("superestrutura", []):
                SuperEstrutura.objects.create(
                    ambiente=ambiente,
                    tipo=s.get("tipo"),
                    largura_m=to_float(s.get("largura")),
                    altura_m=to_float(s.get("altura")),
                    volume_concreto_m3=to_float(s.get("volumeConcreto")),
                    ferragem_kgf=to_float(s.get("pesoFerragem")),
                    estribo_kgf=to_float(s.get("pesoEstribo")),
                    forma_m2=to_float(s.get("areaForma")),
                )

            for m in data.get("metalicas", []):
                EstruturaMetalica.objects.create(
                    ambiente=ambiente,
                    tipo=m.get("tipo"),
                    perfil=m.get("tipoPerfil"),
                    secao=m.get("secao"),
                    peso_kgf=to_float(m.get("peso")),
                    elastomero=to_float(m.get("elastomero")),
                )

            for m in data.get("madeira", []):
                EstruturaMadeira.objects.create(
                    ambiente=ambiente,
                    peca=m.get("tipoPeca"),
                    secao=m.get("secao"),
                    peso_kgf=to_float(m.get("pesoTotal")),
                    telhamento=m.get("tipoTelhamento"),
                )

            return Response({"message": "Salvo com sucesso"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def get(self, request, projeto_id=None):
        try:
            export_excel = request.query_params.get('export') == 'true'
            if projeto_id:
                ambientes = Ambiente.objects.filter(projeto__id_projeto=projeto_id)
                if not ambientes.exists():
                    return Response({"error": "Ambiente não encontrado"}, status=404)
            else:
                ambientes = Ambiente.objects.all()
            results = []
            for a in ambientes:
                ponto_ele = a.pontoeletrico_set.first()
                tipo_ele = a.tipoeletrico_set.first()
                hidra = a.hidraulica_set.first()
                reserva = a.reservatorio_set.first()
                spda = a.spda_set.first()
                telecom = a.telecom_set.first()
                cobertura = a.cobertura_set.first()
                canteiro = a.canteiro_set.first()
                residuo = a.residuo_set.first()
                escavacao = a.escavacao_set.first()
                volume = a.volume_set.first()
                results.append({
                    "projeto_id": a.projeto.id_projeto,
                    "nome": a.nome,
                    "comprimento": a.comprimento,
                    "largura": a.largura,
                    "altura": a.altura,
                    "area": a.area,
                    "tomadas": ponto_ele.tomadas if ponto_ele else 0,
                    "iluminacao": ponto_ele.pontos_iluminacao if ponto_ele else 0,
                    "interruptores": ponto_ele.interruptores if ponto_ele else 0,
                    "tipoTomada": tipo_ele.tipo_tomada if tipo_ele else "",
                    "tipoInterruptor": tipo_ele.tipo_interruptor if tipo_ele else "",
                    "tipoLuminaria": tipo_ele.tipo_luminaria if tipo_ele else "",
                    "alturaInstalacao": tipo_ele.altura_instalacao if tipo_ele else 0,
                    "cabos": [{"circuito": c.circuito, "secao": c.secao_mm2} for c in a.cabo_set.all()],
                    "disjuntores": [{"amperagem": d.amperagem, "quantidade": d.quantidade} for d in a.disjuntor_set.all()],
                    "registros": hidra.registros if hidra else 0,
                    "valvulas": hidra.valvulas if hidra else 0,
                    "conexoes": hidra.conexoes if hidra else 0,
                    "ramais": [{"nome": r.nome, "diametro": r.diametro, "comprimento": r.comprimento_m} for r in a.ramal_set.all()],
                    "reservatorio": {"tipo": reserva.tipo, "capacidade": reserva.capacidade_l} if reserva else None,
                    "hidrantes": [{"localizacao": h.localizacao, "diametro": h.diametro, "conexoes": h.conexoes} for h in a.hidrante_set.all()],
                    "extintores": [{"tipo": e.tipo, "peso": e.peso_kg, "capacidade": e.capacidade_l} for e in a.extintor_set.all()],
                    "dutos":[{"diametro": d.diametro, "comprimento":d.comprimento_m}for d in a.duto_set.all()],
                    "hastesAterramento": spda.hastes if spda else 0,
                    "caixasInspecao": spda.caixas_inspecao if spda else 0,
                    "terminaisAereos": spda.terminais_aereos if spda else 0,
                    "quadrosRede": telecom.quadros_rede if telecom else 0,
                    "patchCords": telecom.patch_cords if telecom else 0,
                    "cameras": telecom.cameras if telecom else 0,
                    "cabeamentos": [{"circuito": cb.circuito, "comprimento": cb.comprimento_m, "tomadas": cb.tomadas} for cb in a.cabeamento_set.all()],
                    "tipoEstrutura": cobertura.estrutura if cobertura else "",
                    "tipoTelhamento": cobertura.telhamento if cobertura else "",
                    "espessura": cobertura.espessura_cm if cobertura else 0,
                    "inclinacao": cobertura.inclinacao_percent if cobertura else 0,
                    "pecas": [{"descricao": p.descricao, "secao": p.secao} for p in a.peca_set.all()],
                    "conteineres": canteiro.conteineres if canteiro else 0,
                    "banheirosQuimicos": canteiro.banheiros if canteiro else 0,
                    "andaimes": canteiro.andaimes if canteiro else 0,
                    "residuoComum": residuo.comum_m3 if residuo else 0,
                    "residuoContaminado": residuo.contaminado_m3 if residuo else 0,
                    "destinacaoResiduo": residuo.destinacao if residuo else "",
                    "profundidadeEscavacao": escavacao.profundidade_m if escavacao else 0,
                    "inclinacaoTerreno": escavacao.inclinacao_percent if escavacao else 0,
                    "volumes": {
                        "terraplanagem": volume.terraplanagem_m3, "escavacao": volume.escavacao_m3,
                        "aterro": volume.aterro_m3, "enrocamento": volume.enrocamento_m3,
                        "contencao": volume.contencao_m3, "taludamento": volume.taludamento_m3,
                        "nivelamento": volume.nivelamento_m3, "compactacao": volume.compactacao_m3
                    } if volume else {},
                    "fundacoes": [
                        {"tipo": f.tipo, "profundidade": f.profundidade_m, "volumeLastro": f.volume_lastro_m3, 
                         "volumeConcreto": f.volume_concreto_m3, "pesoFerragem": f.ferragem_kgf, "pesoEstribo":f.estribo_kgf, "areaForma":f.forma_m2} 
                        for f in a.fundacao_set.all()
                    ],
                    "superestrutura": [
                        {"tipo": s.tipo, "largura": s.largura_m, "altura": s.altura_m, 
                         "volumeConcreto": s.volume_concreto_m3, "pesoFerragem": s.ferragem_kgf, "pesoEstribo":s.estribo_kgf, "areaForma":s.forma_m2} 
                        for s in a.superestrutura_set.all()
                    ],
                    "metalicas": [
                        {"tipo": m.tipo, "tipoPerfil": m.perfil, "secao": m.secao, "peso": m.peso_kgf, "elastomero":m.elastomero} 
                        for m in a.estruturametalica_set.all()
                    ],
                    "madeira": [
                        {"tipoPeca": md.peca, "secao": md.secao, "pesoTotal": md.peso_kgf, "tipoTelhamento": md.telhamento} 
                        for md in a.estruturamadeira_set.all()
                    ],
                })
            return Response(results[0] if projeto_id else results)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class GerarMemorialExcel(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser]

    def get(self, request, projeto_id):
        """
        Geração via banco de dados (projeto_id)
        """
        try:
            if extrair_levantamento_campo_para_xlsx is None:
                return Response({"error": "Serviço de extração não localizado."}, status=500)

            path_template = os.path.join(
                settings.BASE_DIR, 'apps', 'dados_ia', 'services',
                'memorial', 'templates_excel', 'Memorial de Cálculo - Modelo.xlsx'
            )

            if not os.path.exists(path_template):
                return Response({"error": f"Template não encontrado: {path_template}"}, status=500)

            ambientes_db = Ambiente.objects.filter(projeto__id_projeto=projeto_id)
            if not ambientes_db.exists():
                return Response({"error": "Nenhum ambiente encontrado para este projeto."}, status=404)

            lista_ambientes = []

            for a in ambientes_db:
                ponto_ele = a.pontoeletrico_set.first()
                tipo_ele  = a.tipoeletrico_set.first()
                hidra     = a.hidraulica_set.first()
                reserva   = a.reservatorio_set.first()
                spda      = a.spda_set.first()
                telecom   = a.telecom_set.first()
                cobertura = a.cobertura_set.first()
                canteiro  = a.canteiro_set.first()
                residuo   = a.residuo_set.first()
                escavacao = a.escavacao_set.first()
                volume    = a.volume_set.first()

                lista_ambientes.append({
                    "nome": a.nome,
                    "comprimento": float(a.comprimento or 0),
                    "largura": float(a.largura or 0),
                    "altura": float(a.altura or 0),
                    "area": float(a.area or 0),

                    "tomadas": ponto_ele.tomadas if ponto_ele else 0,
                    "iluminacao": ponto_ele.pontos_iluminacao if ponto_ele else 0,
                    "interruptores": ponto_ele.interruptores if ponto_ele else 0,

                    "tipoTomada": tipo_ele.tipo_tomada if tipo_ele else "",
                    "tipoInterruptor": tipo_ele.tipo_interruptor if tipo_ele else "",
                    "tipoLuminaria": tipo_ele.tipo_luminaria if tipo_ele else "",
                    "alturaInstalacao": float(tipo_ele.altura_instalacao) if tipo_ele else 0,

                    "cabos": [
                        {"circuito": c.circuito, "secao": float(c.secao_mm2)}
                        for c in a.cabo_set.all()
                    ],
                    "disjuntores": [
                        {"amperagem": float(d.amperagem), "quantidade": d.quantidade}
                        for d in a.disjuntor_set.all()
                    ],
                    "cabeamentos": [
                        {"circuito": cb.circuito, "comprimento": float(cb.comprimento_m), "tomadas": cb.tomadas}
                        for cb in a.cabeamento_set.all()
                    ],

                    "hastesAterramento": spda.hastes if spda else 0,
                    "caixasInspecao": spda.caixas_inspecao if spda else 0,
                    "terminaisAereos": spda.terminais_aereos if spda else 0,

                    "quadrosRede": telecom.quadros_rede if telecom else 0,
                    "patchCords": telecom.patch_cords if telecom else 0,
                    "cameras": telecom.cameras if telecom else 0,

                    "registros": hidra.registros if hidra else 0,
                    "valvulas": hidra.valvulas if hidra else 0,
                    "conexoes": hidra.conexoes if hidra else 0,

                    "ramais": [
                        {"nome": r.nome, "diametro": r.diametro, "comprimento": float(r.comprimento_m)}
                        for r in a.ramal_set.all()
                    ],

                    "reservatorio": {
                        "tipo": reserva.tipo,
                        "capacidade": float(reserva.capacidade_l)
                    } if reserva else None,

                    "extintores": [
                        {"tipo": e.tipo, "peso": float(e.peso_kg), "capacidade": float(e.capacidade_l)}
                        for e in a.extintor_set.all()
                    ],
                    "dutos": [
                        {"diametro": d.diametro, "comprimento": float(d.comprimento_m)}
                        for d in a.duto_set.all()
                    ],
                    "hidrantes": [
                        {"localizacao": h.localizacao, "diametro": h.diametro, "conexoes": h.conexoes}
                        for h in a.hidrante_set.all()
                    ],

                    "tipoEstrutura": cobertura.estrutura if cobertura else "",
                    "tipoTelhamento": cobertura.telhamento if cobertura else "",
                    "espessura": float(cobertura.espessura_cm) if cobertura else 0,
                    "inclinacao": float(cobertura.inclinacao_percent) if cobertura else 0,

                    "pecas": [
                        {"descricao": p.descricao, "secao": p.secao}
                        for p in a.peca_set.all()
                    ],

                    "conteineres": canteiro.conteineres if canteiro else 0,
                    "banheirosQuimicos": canteiro.banheiros if canteiro else 0,
                    "andaimes": canteiro.andaimes if canteiro else 0,

                    "residuoComum": float(residuo.comum_m3) if residuo else 0,
                    "residuoContaminado": float(residuo.contaminado_m3) if residuo else 0,
                    "destinacaoResiduo": residuo.destinacao if residuo else "",

                    "profundidadeEscavacao": float(escavacao.profundidade_m) if escavacao else 0,
                    "inclinacaoTerreno": float(escavacao.inclinacao_percent) if escavacao else 0,

                    "volumes": {
                        "terraplanagem": float(volume.terraplanagem_m3),
                        "escavacao": float(volume.escavacao_m3),
                        "aterro": float(volume.aterro_m3),
                        "enrocamento": float(volume.enrocamento_m3),
                        "contencao": float(volume.contencao_m3),
                        "taludamento": float(volume.taludamento_m3),
                        "nivelamento": float(volume.nivelamento_m3),
                        "compactacao": float(volume.compactacao_m3),
                    } if volume else {},
                    "fundacoes": [
                        {"tipo": f.tipo, "profundidade": f.profundidade_m, "volumeLastro": f.volume_lastro_m3,
                         "volumeConcreto": f.volume_concreto_m3, "pesoFerragem": f.ferragem_kgf,
                         "pesoEstribo": f.estribo_kgf, "areaForma": f.forma_m2}
                        for f in a.fundacao_set.all()
                    ],
                    "superestrutura": [
                        {"tipo": s.tipo, "largura": s.largura_m, "altura": s.altura_m,
                         "volumeConcreto": s.volume_concreto_m3, "pesoFerragem": s.ferragem_kgf,
                         "pesoEstribo": s.estribo_kgf, "areaForma": s.forma_m2}
                        for s in a.superestrutura_set.all()
                    ],
                    "metalicas": [
                        {"tipo": m.tipo, "tipoPerfil": m.perfil, "secao": m.secao, "peso": m.peso_kgf, "elastomero": m.elastomero}
                        for m in a.estruturametalica_set.all()
                    ],
                    "madeira": [
                        {"tipoPeca": md.peca, "secao": md.secao, "pesoTotal": md.peso_kgf, "tipoTelhamento": md.telhamento}
                        for md in a.estruturamadeira_set.all()
                    ],
                    
                })

            conteudo_excel = extrair_levantamento_campo_para_xlsx(
                dados_json={"ambientes": lista_ambientes},
                template_path=path_template
            )

            response = HttpResponse(
                conteudo_excel,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="Memorial_{projeto_id}.xlsx"'

            return response

        except Exception as e:
            return Response({"error": f"Erro na geração: {str(e)}"}, status=500)

    def post(self, request, *args, **kwargs):
        try:
            arquivo_form = request.FILES.get("form")
            arquivo_dxf = request.FILES.get("dxf")

            if not arquivo_form:
                return Response({"erro": "Envie o JSON do formulário no campo 'form'."}, status=400)

            if not arquivo_dxf:
                return Response({"erro": "Envie o JSON do DXF no campo 'dxf'."}, status=400)

            dados_form = json.loads(arquivo_form.read().decode("utf-8"))
            dados_dxf = json.loads(arquivo_dxf.read().decode("utf-8"))

            dados_mesclados = mesclar_form_com_dxf(dados_form, dados_dxf)

            arquivo_bytes = extrair_levantamento_campo_para_xlsx(dados_mesclados)

            response = HttpResponse(
                arquivo_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = 'attachment; filename="memorial_mesclado.xlsx"'

            return response

        except json.JSONDecodeError as e:
            return Response({"erro": "JSON inválido.", "detalhe": str(e)}, status=400)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"erro": str(e)}, status=500)

DICIONARIO_LAYERS_PATH = os.path.join(settings.MEDIA_ROOT, 'dicionario_layers.txt')


def _ler_dicionario():
    if os.path.exists(DICIONARIO_LAYERS_PATH):
        with open(DICIONARIO_LAYERS_PATH, 'r', encoding='utf-8') as f:
            return set(l.strip() for l in f if l.strip())
    return set()


def _salvar_dicionario(layers):
    os.makedirs(os.path.dirname(DICIONARIO_LAYERS_PATH), exist_ok=True)
    with open(DICIONARIO_LAYERS_PATH, 'w', encoding='utf-8') as f:
        for nome in sorted(layers):
            f.write(f"{nome}\n")


class GerenciarLayersView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        layers_recebidas = request.data.get("layers", [])
        if not layers_recebidas:
            return Response({"erro": "Envie {'layers': [...]} no body"}, status=400)

        dicionario = _ler_dicionario()
        novas = [l for l in layers_recebidas if l not in dicionario]

        if novas:
            dicionario.update(novas)
            _salvar_dicionario(dicionario)

        return Response({"layers": sorted(dicionario)})

    def get(self, request):
        return Response({"layers": sorted(_ler_dicionario())})