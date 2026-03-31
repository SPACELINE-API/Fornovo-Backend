import re
import math
from collections import defaultdict


def _limpar_texto(raw):
    if not raw:
        return ""
    t = re.sub(r'\{[^{}]*\}', '', raw)
    t = re.sub(r'\\[a-zA-Z0-9]+\d*\.?.?x?;', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip().strip('\\{}()[]').strip()


def _match_layer(layer, palavra):
    l = layer.upper()
    p = palavra.upper()
    return p in l or p.replace('Ê', 'E').replace('Ç', 'C') in l


def _comprimento_entidade(e):
    d = e.get('dados', {})
    tipo = e.get('tipo', '')
    if tipo == 'LINE':
        return d.get('comprimento', 0.0)
    if tipo in ('LWPOLYLINE', 'POLYLINE'):
        pts = d.get('pontos', [])
        total = 0.0
        for i in range(len(pts) - 1):
            total += math.sqrt((pts[i+1][0] - pts[i][0])**2 + (pts[i+1][1] - pts[i][1])**2)
        return round(total, 2)
    return 0.0


def _bbox_pontos(pts):
    if not pts:
        return None
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return {
        'x_min': round(min(xs), 2), 'x_max': round(max(xs), 2),
        'y_min': round(min(ys), 2), 'y_max': round(max(ys), 2),
        'largura': round(max(xs) - min(xs), 2),
        'altura': round(max(ys) - min(ys), 2),
    }


def _extrair_elementos_por_layer(entidades, palavra_chave):
    elementos = []
    for e in entidades:
        layer = e.get('layer', '')
        if not _match_layer(layer, palavra_chave):
            continue
        d = e.get('dados', {})
        tipo = e.get('tipo', '')
        elem = {
            'tipo': tipo,
            'layer': layer,
            'comprimento': _comprimento_entidade(e),
        }
        if tipo == 'LINE':
            elem['inicio'] = d.get('inicio')
            elem['fim'] = d.get('fim')
        elif tipo in ('LWPOLYLINE', 'POLYLINE'):
            pts = d.get('pontos', [])
            elem['bbox'] = _bbox_pontos(pts)
            elem['fechada'] = d.get('fechada', False)
        elif tipo == 'CIRCLE':
            elem['raio'] = d.get('raio')
        elif tipo == 'ARC':
            elem['raio'] = d.get('raio')
            elem['angulo_inicio'] = d.get('angulo_inicio')
            elem['angulo_fim'] = d.get('angulo_fim')
        elementos.append(elem)
    return elementos


def _extrair_componentes_eletricos(textos, blocos):
    padroes = {
        'tomadas': r'\bTOM\.?\s*(?:AR|BAIXA|M[ÉE]DIA|ALTA)?\b|\bTOMADAS?\b|\bTUGS?\b|\bTUES?\b|\bTOMADA\s+DE\s+FOR[ÇC]A\b|\bTF\b',
        'interruptores': r'\bINTERRUPTORES?\b|\bINT\.?\b|\bCHAVES?\b|\bCHAVE\s+(?:SIMPLES|PARALELA|INTERMEDI[ÁA]RIA)\b',
        'luminarias': r'\bLUMIN[ÁA]RIAS?\b|\bLUM\.?\b|\bILUM(?:INA[ÇC][ÃA]O)?\.?\b|\bL[ÂA]MPADAS?\b|\bLAMP\.?\b|\bPLAFON\b|\bSPOT\b',
        'quadros': r'\bQD\.?\b|\bQDG\b|\bQDC\b|\bQGBT\b|\bQUADROS?\b|\bQUADRO\s+DE\s+(?:DISTRIBUI[ÇC][ÃA]O|FOR[ÇC]A)\b|\bDISJUNTOR\b|\bDISJ\.?\b',
        'conduletes': r'\bCONDULET[ES]*\b|\bCX\.?\s*MOLDADA\b|\bCAIXA\s+MOLDADA\b',
    }

    componentes = defaultdict(list)
    for t in textos:
        conteudo = _limpar_texto(t.get('conteudo', ''))
        if not conteudo:
            continue
        for categoria, padrao in padroes.items():
            if re.search(padrao, conteudo, re.IGNORECASE):
                componentes[categoria].append({
                    'descricao': conteudo,
                    'layer': t.get('layer', ''),
                    'posicao': t.get('posicao', []),
                })
                break

    for b in blocos:
        attrs = b.get('atributos', {})
        if attrs:
            componentes['blocos'].append({
                'nome': b.get('nome', ''),
                'layer': b.get('layer', ''),
                'atributos': attrs,
                'posicao': b.get('insercao', []),
            })

    return dict(componentes)


def _associar_por_ambiente(componentes, ambientes):
    por_ambiente = {}
    for amb in ambientes:
        nome = amb.get('nome', '')
        if not nome:
            continue
        por_ambiente[nome] = {
            'tomadas': [], 'interruptores': [], 'luminarias': [],
            'quadros': [], 'conduletes': [],
        }

    for categoria in ['tomadas', 'interruptores', 'luminarias', 'quadros', 'conduletes']:
        for comp in componentes.get(categoria, []):
            desc = comp.get('descricao', '').upper()
            associado = False
            for nome_amb in por_ambiente:
                if nome_amb.upper() in desc:
                    por_ambiente[nome_amb][categoria].append(comp)
                    associado = True
                    break
            if not associado:
                for nome_amb in por_ambiente:
                    if any(p in desc for p in nome_amb.upper().split()):
                        por_ambiente[nome_amb][categoria].append(comp)
                        break

    return por_ambiente


def extrair_dados_completos_dxf(dados_dxf: dict) -> dict:
    entidades = dados_dxf.get('entidades', [])
    textos = dados_dxf.get('textos', [])
    blocos = dados_dxf.get('blocos', [])

    if not textos:
        textos = [e for e in entidades if e.get('tipo') in ('MTEXT', 'TEXT')]

    from .levantamento_campo import _extrair_ambientes_super
    ambientes = _extrair_ambientes_super(textos)
    ambientes_validos = [a for a in ambientes if a.get('area', 0) > 0]

    estruturas = {
        'pilares': _extrair_elementos_por_layer(entidades, 'PILAR'),
        'vigas': _extrair_elementos_por_layer(entidades, 'VIGA'),
        'lajes': _extrair_elementos_por_layer(entidades, 'LAJE'),
    }

    totais_estrutura = {}
    for chave, elems in estruturas.items():
        comp_total = round(sum(e['comprimento'] for e in elems), 2)
        totais_estrutura[chave] = {
            'quantidade': len(elems),
            'comprimento_total_m': comp_total,
            'elementos': elems,
        }

    dutos_total = 0.0
    cabos_total = 0.0
    for e in entidades:
        layer = e.get('layer', '').upper()
        comp = _comprimento_entidade(e)
        if any(p in layer for p in ['DUTO', 'ELETRODUTO', 'ELETROCALHA', 'CONDUITE', 'CONDUTE', 'TUBULACAO', 'TUBULAÇÃO']):
            dutos_total += comp
        elif any(p in layer for p in ['CABO', 'FIAÇÃO', 'FIACAO', 'REDE LÓGICA', 'REDE LOGICA', 'TELEFONIA', 'CFTV']):
            cabos_total += comp

    componentes = _extrair_componentes_eletricos(textos, blocos)
    por_ambiente = _associar_por_ambiente(componentes, ambientes_validos)

    return {
        'ambientes': ambientes_validos,
        'total_ambientes': len(ambientes_validos),
        'estruturas': totais_estrutura,
        'eletrica': {
            'dutos_total_m': round(dutos_total, 2),
            'cabos_total_m': round(cabos_total, 2),
            'componentes': componentes,
            'por_ambiente': por_ambiente,
        },
    }
