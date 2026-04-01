import json
import re
import math


def _limpar_texto(raw):
    if not raw:
        return ""
    t = re.sub(r'\{[^{}]*\}', '', raw)
    t = re.sub(r'\\[a-zA-Z0-9]+\d*\.?.?x?;', ' ', t)
    t = t.replace('\\P', ' ').replace('\\p', ' ').replace('\n', ' ')
    t = re.sub(r'\s+', ' ', t)
    return t.strip().strip('\\{}()[]').strip()


def _comp_entidade(e):
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


def _pos_entidade(e):
    d = e.get('dados', {})
    tipo = e.get('tipo', '')
    if tipo == 'LINE':
        return d.get('inicio', [0, 0, 0])
    if tipo in ('LWPOLYLINE', 'POLYLINE'):
        pts = d.get('pontos', [])
        if pts:
            return pts[0]
    if tipo in ('CIRCLE', 'ARC', 'INSERT'):
        return d.get('centro') or d.get('insercao') or [0, 0, 0]
    if tipo in ('MTEXT', 'TEXT'):
        return d.get('posicao') or [0, 0, 0]
    return [0, 0, 0]


def _match_layer(layer, palavra):
    l = layer.upper()
    p = palavra.upper()
    return p in l or p.replace('Ê', 'E').replace('Ç', 'C') in l


def _extrair_ambientes(textos):
    ambientes = []
    seen = set()
    kw_ambientes = [
        'SALA', 'CIRCULAÇÃO', 'CIRCULAC', 'CENTRO', 'BANHEIRO', 'QUARTO',
        'COZINHA', 'DEPÓSITO', 'DEPOSITO', 'ÁREA', 'AREA', 'PÁTIO', 'PATIO',
        'WC', 'COPA', 'AUDITÓRIO', 'BLOCO', 'ALOJAMENTO', 'TELHADO',
    ]

    for t in textos:
        c_raw = t.get('conteudo', '')
        c_limpo = _limpar_texto(c_raw)
        c_upper = c_limpo.upper()

        if len(c_limpo) < 2 or c_upper in seen:
            continue

        area_match = re.search(r'm[²2]', c_upper)
        tem_kw = any(k in c_upper for k in kw_ambientes)

        if area_match or tem_kw:
            nome_final = c_limpo.strip()
            if nome_final:
                area_search = re.search(r'(\d+[.,]?\d*)\s*m[²2]', c_limpo, re.IGNORECASE)
                area_val = float(area_search.group(1).replace(',', '.')) if area_search else 0.0
                ambientes.append({
                    'nome': nome_final,
                    'posicao': t.get('posicao', [0, 0, 0]),
                    'area': area_val,
                })
                seen.add(nome_final.upper())

    return ambientes


def _extrair_estruturas(entidades):
    estruturas = []
    for e in entidades:
        layer = e.get('layer', '').upper()
        tipo_est = None

        if 'PILAR' in layer: tipo_est = 'PILAR'
        elif 'VIGA' in layer: tipo_est = 'VIGA'
        elif 'LAJE' in layer: tipo_est = 'LAJE'

        if tipo_est:
            comp = _comp_entidade(e)
            if comp > 0:
                estruturas.append({
                    'tipo': tipo_est,
                    'layer': e.get('layer', ''),
                    'medida': round(comp, 2),
                    'posicao': _pos_entidade(e),
                })
    return estruturas


def _extrair_componentes_eletricos(entidades, textos, blocos):
    padroes_texto = {
        'QUADROS': r'\bQD\.?\b|\bQDG\b|\bQDC\b|\bQGBT\b|\bQUADROS?\b|\bQUADRO\s+DE\s+(?:DISTRIBUI[ÇC][ÃA]O|FOR[ÇC]A)\b|\bDISJUNTOR\b|\bDISJ\.?\b',
        'CONDULETES': r'\bCONDULET[ES]*\b|\bCX\.?\s*MOLDADA\b|\bCAIXA\s+MOLDADA\b',
        'TOMADAS': r'\bTOM\.?\s*(?:AR|BAIXA|M[ÉE]DIA|ALTA)?\b|\bTOMADAS?\b|\bTUGS?\b|\bTUES?\b|\bTOMADA\s+DE\s+FOR[ÇC]A\b|\bTF\b',
        'INTERRUPTORES': r'\bINTERRUPTORES?\b|\bINT\.?\b|\bCHAVES?\b|\bCHAVE\s+(?:SIMPLES|PARALELA|INTERMEDI[ÁA]RIA)\b',
        'LUMINÁRIAS': r'\bLUMIN[ÁA]RIAS?\b|\bLUM\.?\b|\bILUM(?:INA[ÇC][ÃA]O)?\.?\b|\bL[ÂA]MPADAS?\b|\bLAMP\.?\b|\bPLAFON\b|\bSPOT\b',
    }

    componentes = {cat: [] for cat in padroes_texto}
    componentes['DUTOS'] = []
    componentes['CABOS'] = []

    for t in textos:
        conteudo = _limpar_texto(t.get('conteudo', ''))
        if not conteudo:
            continue
        for categoria, padrao in padroes_texto.items():
            if re.search(padrao, conteudo, re.IGNORECASE):
                componentes[categoria].append({
                    'descricao': conteudo,
                    'layer': t.get('layer', ''),
                    'posicao': t.get('posicao', [0, 0, 0]),
                })
                break

    for b in blocos:
        attrs = b.get('atributos', {})
        if attrs:
            placa = attrs.get('PLACA', '')
            if placa:
                componentes['QUADROS'].append({
                    'descricao': f"Quadro: {placa}",
                    'layer': b.get('layer', ''),
                    'posicao': b.get('insercao', [0, 0, 0]),
                    'atributos': attrs,
                })

    keywords_dutos = ['DUTO', 'ELETRODUTO', 'ELETROCALHA', 'CONDUITE', 'CONDUTE', 'TUBULACAO', 'TUBULAÇÃO']
    keywords_cabos = ['CABO', 'FIAÇÃO', 'FIACAO', 'REDE LÓGICA', 'REDE LOGICA', 'TELEFONIA', 'CFTV']

    for e in entidades:
        layer = e.get('layer', '').upper()
        comp = _comp_entidade(e)
        pos = _pos_entidade(e)

        if any(p in layer for p in keywords_dutos) and comp > 0:
            componentes['DUTOS'].append({
                'layer': e.get('layer', ''),
                'comprimento': round(comp, 2),
                'posicao': pos,
                'tipo_entidade': e.get('tipo', ''),
            })
        elif any(p in layer for p in keywords_cabos) and comp > 0:
            componentes['CABOS'].append({
                'layer': e.get('layer', ''),
                'comprimento': round(comp, 2),
                'posicao': pos,
                'tipo_entidade': e.get('tipo', ''),
            })

    return componentes


def _associar_por_ambiente(componentes, ambientes):
    categorias = ['QUADROS', 'CONDULETES', 'TOMADAS', 'INTERRUPTORES', 'LUMINÁRIAS', 'DUTOS', 'CABOS']
    por_ambiente = {}

    for amb in ambientes:
        nome = amb.get('nome', '')
        if nome:
            por_ambiente[nome] = {cat: [] for cat in categorias}

    for cat in categorias:
        for comp in componentes.get(cat, []):
            pos_comp = comp.get('posicao', [0, 0, 0])
            if not ambientes:
                continue

            menor_dist = float('inf')
            amb_alvo = None
            for amb in ambientes:
                pos_amb = amb.get('posicao', [0, 0, 0])
                dist = math.sqrt(
                    (pos_comp[0] - pos_amb[0])**2 + (pos_comp[1] - pos_amb[1])**2
                )
                if dist < menor_dist:
                    menor_dist = dist
                    amb_alvo = amb.get('nome')

            if amb_alvo and amb_alvo in por_ambiente:
                por_ambiente[amb_alvo][cat].append(comp)

    return por_ambiente


def auditar_estruturas_ambientes(caminho_json: str):
    print(f"A ler o ficheiro: {caminho_json}...")
    print("A analisar ambientes, estruturas e componentes elétricos. Aguarde...\n")

    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Ficheiro '{caminho_json}' nao encontrado.")
        return

    if 'entidades' not in dados:
        for val in dados.values():
            if isinstance(val, dict) and 'entidades' in val:
                dados = val; break
            if isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    if 'entidades' in parsed: dados = parsed; break
                except: pass

    entidades = dados.get('entidades', [])
    textos = dados.get('textos', []) or [e for e in entidades if e.get('tipo') in ('MTEXT', 'TEXT')]
    blocos = dados.get('blocos', [])

    ambientes = _extrair_ambientes(textos)
    estruturas = _extrair_estruturas(entidades)
    componentes = _extrair_componentes_eletricos(entidades, textos, blocos)
    por_ambiente = _associar_por_ambiente(componentes, ambientes)

    categorias_estrutura = ['PILAR', 'VIGA', 'LAJE']
    resultado = {a['nome']: {**{est: [] for est in categorias_estrutura}, **{cat: [] for cat in ['QUADROS', 'CONDULETES', 'TOMADAS', 'INTERRUPTORES', 'LUMINÁRIAS', 'DUTOS', 'CABOS']}} for a in ambientes}
    if not ambientes:
        resultado['SEM AMBIENTE'] = {**{est: [] for est in categorias_estrutura}, **{cat: [] for cat in ['QUADROS', 'CONDULETES', 'TOMADAS', 'INTERRUPTORES', 'LUMINÁRIAS', 'DUTOS', 'CABOS']}}

    for est in estruturas:
        if not ambientes:
            resultado['SEM AMBIENTE'][est['tipo']].append(est)
            continue
        menor_distancia = float('inf')
        amb_mais_proximo = None
        for amb in ambientes:
            pos_amb = amb['posicao']
            pos_est = est['posicao']
            dist = math.sqrt((pos_est[0] - pos_amb[0])**2 + (pos_est[1] - pos_amb[1])**2)
            if dist < menor_distancia:
                menor_distancia = dist
                amb_mais_proximo = amb['nome']
        if amb_mais_proximo:
            resultado[amb_mais_proximo][est['tipo']].append(est)

    for amb_nome, comps in por_ambiente.items():
        if amb_nome in resultado:
            for cat in comps:
                resultado[amb_nome][cat].extend(comps[cat])

    print("=" * 80)
    print("RESUMO GERAL")
    print("=" * 80)

    categorias_ele = ['QUADROS', 'CONDULETES', 'TOMADAS', 'INTERRUPTORES', 'LUMINÁRIAS']
    for cat in categorias_ele:
        total = len(componentes.get(cat, []))
        if total > 0:
            print(f"  {cat}: {total} itens encontrados")

    dutos_total = round(sum(d.get('comprimento', 0) for d in componentes.get('DUTOS', [])), 2)
    cabos_total = round(sum(c.get('comprimento', 0) for c in componentes.get('CABOS', [])), 2)
    if dutos_total > 0:
        print(f"  DUTOS: {len(componentes['DUTOS'])} segmentos | Total: {dutos_total} unidades")
    if cabos_total > 0:
        print(f"  CABOS: {len(componentes['CABOS'])} segmentos | Total: {cabos_total} unidades")

    print("=" * 80)

    for amb_nome, dados_amb in resultado.items():
        tem_conteudo = any(len(v) > 0 for v in dados_amb.values())
        if not tem_conteudo:
            continue

        print(f"\n{'=' * 80}")
        print(f"  Ambiente: '{amb_nome}'")
        print(f"{'=' * 80}")

        for est_tipo in categorias_estrutura:
            itens = dados_amb[est_tipo]
            if not itens:
                continue
            print(f"\n  [{est_tipo}] ({len(itens)} itens)")
            for item in itens:
                print(f"    - Layer: {item['layer']} | Medida: {item['medida']} unidades")

        for cat in categorias_ele:
            itens = dados_amb[cat]
            if not itens:
                continue
            print(f"\n  [{cat}] ({len(itens)} itens)")
            for item in itens:
                desc = item.get('descricao', '')
                layer = item.get('layer', '')
                if desc:
                    print(f"    - {desc} (Layer: {layer})")
                else:
                    print(f"    - Layer: {layer}")

        dutos_amb = dados_amb.get('DUTOS', [])
        if dutos_amb:
            total_d = round(sum(d.get('comprimento', 0) for d in dutos_amb), 2)
            print(f"\n  [DUTOS] ({len(dutos_amb)} segmentos | Total: {total_d} unidades)")
            for d in dutos_amb:
                print(f"    - Layer: {d['layer']} | Comprimento: {d['comprimento']} unidades")

        cabos_amb = dados_amb.get('CABOS', [])
        if cabos_amb:
            total_c = round(sum(c.get('comprimento', 0) for c in cabos_amb), 2)
            print(f"\n  [CABOS] ({len(cabos_amb)} segmentos | Total: {total_c} unidades)")
            for c in cabos_amb:
                print(f"    - Layer: {c['layer']} | Comprimento: {c['comprimento']} unidades")

        print("-" * 80)

    print("\n" + "=" * 80)
    print("AMBIENTES QUE CONTÉM COMPONENTES ELÉTRICOS")
    print("=" * 80)

    ambientes_com_eletricos = []
    for amb_nome, dados_amb in resultado.items():
        itens_ele = []
        for cat in categorias_ele + ['DUTOS', 'CABOS']:
            qtd = len(dados_amb.get(cat, []))
            if qtd > 0:
                if cat == 'DUTOS':
                    total_d = round(sum(d.get('comprimento', 0) for d in dados_amb[cat]), 2)
                    itens_ele.append(f"{cat}: {qtd} seg ({total_d}u)")
                elif cat == 'CABOS':
                    total_c = round(sum(c.get('comprimento', 0) for c in dados_amb[cat]), 2)
                    itens_ele.append(f"{cat}: {qtd} seg ({total_c}u)")
                else:
                    itens_ele.append(f"{cat}: {qtd}")
        if itens_ele:
            ambientes_com_eletricos.append((amb_nome, itens_ele))

    if ambientes_com_eletricos:
        for amb_nome, itens in ambientes_com_eletricos:
            print(f"\n  '{amb_nome}'")
            for item in itens:
                print(f"    - {item}")
    else:
        print("\n  Nenhum ambiente com componentes elétricos encontrado.")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    JSON_ENTRADA = r"C:\Users\vinic\Downloads\teste.JSON"
    auditar_estruturas_ambientes(JSON_ENTRADA)