import json
import re
import math
from pathlib import Path

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

def extrair_tudo_sobre_solo(entidades, textos, blocos):
    keywords_solo = [
        'TERRAPL', 'CORTE', 'ATERRO', 'ESCAVA', 'ENROCAMENTO', 
        'CONTEN', 'ARRIMO', 'TALUD', 'NIVELAMENTO', 'COMPACTA', 
        'SOLO', 'TERRENO', 'GLEBA', 'LOTE', 'VOLUME', 'COTA'
    ]

    resultados = {
        'textos': [],
        'geometria': [],
        'blocos': []
    }

    # 1. VARREDURA DE TEXTOS
    for t in textos:
        conteudo_raw = t.get('conteudo', '')
        conteudo_limpo = _limpar_texto(conteudo_raw).upper()
        
        if any(kw in conteudo_limpo for kw in keywords_solo):
            valores_extraidos = re.findall(r'(\d+[.,]?\d*)\s*(m³|m3|m²|m2|m|%)', conteudo_limpo, re.IGNORECASE)
            
            resultados['textos'].append({
                'texto_original': conteudo_raw.replace('\n', ' ').replace('\r', ''),
                'texto_limpo': conteudo_limpo,
                'layer': t.get('layer', 'DESCONHECIDO'),
                'valores': valores_extraidos,
                'posicao': _pos_entidade(t)
            })

    # 2. VARREDURA DE GEOMETRIAS
    for e in entidades:
        layer = e.get('layer', '').upper()
        if any(kw in layer for kw in keywords_solo):
            comp = _comp_entidade(e)
            if comp > 0:
                resultados['geometria'].append({
                    'tipo': e.get('tipo', 'DESCONHECIDO'),
                    'layer': e.get('layer', ''),
                    'medida_linear': comp,
                    'posicao': _pos_entidade(e)
                })

    # 3. VARREDURA DE BLOCOS
    for b in blocos:
        layer = b.get('layer', '').upper()
        attrs = b.get('atributos', {})
        relevante = any(kw in layer for kw in keywords_solo)
        
        for k, v in attrs.items():
            k_upper, v_upper = str(k).upper(), str(v).upper()
            if any(kw in k_upper for kw in keywords_solo) or any(kw in v_upper for kw in keywords_solo):
                relevante = True
                break
        
        if relevante:
            resultados['blocos'].append({
                'nome_bloco': b.get('nome', 'N/A'),
                'layer': b.get('layer', ''),
                'atributos': attrs,
                'posicao': _pos_entidade(b)
            })

    return resultados

def auditar_movimentos_solo(caminho_json: str):
    caminho_obj = Path(caminho_json)
    # Cria o ficheiro TXT na mesma pasta do JSON, com o prefixo 'relatorio_solo_'
    caminho_txt = caminho_obj.with_name(f"relatorio_solo_{caminho_obj.stem}.txt")

    linhas_relatorio = []
    linhas_relatorio.append(f"A ler o ficheiro: {caminho_json}...")
    
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"Erro: O ficheiro '{caminho_json}' não foi encontrado.")
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

    linhas_relatorio.append("A extrair todos os dados de Movimento de Solo...\n")
    extraido = extrair_tudo_sobre_solo(entidades, textos, blocos)

    linhas_relatorio.append("=" * 80)
    linhas_relatorio.append(" RELATÓRIO DE EXTRAÇÃO: MOVIMENTO DE SOLO")
    linhas_relatorio.append("=" * 80)

    # IMPRIMIR TEXTOS ENCONTRADOS
    linhas_relatorio.append(f"\n[1] TEXTOS ENCONTRADOS ({len(extraido['textos'])} itens)")
    if not extraido['textos']:
        linhas_relatorio.append("    Nenhum texto sobre solo encontrado.")
    for t in extraido['textos']:
        linhas_relatorio.append(f"    - Layer: {t['layer']}")
        linhas_relatorio.append(f"      Texto: '{t['texto_original']}'")
        if t['valores']:
            vals = " | ".join([f"{v[0]}{v[1]}" for v in t['valores']])
            linhas_relatorio.append(f"      Valores/Medidas detectadas: -> {vals}")
        linhas_relatorio.append("")

    # IMPRIMIR GEOMETRIAS ENCONTRADAS
    linhas_relatorio.append(f"[2] GEOMETRIA EM LAYERS DE SOLO ({len(extraido['geometria'])} itens)")
    if not extraido['geometria']:
        linhas_relatorio.append("    Nenhuma linha ou polilinha em layers de solo.")
    for g in extraido['geometria']:
        linhas_relatorio.append(f"    - Tipo: {g['tipo']} | Layer: {g['layer']} | Perímetro/Comprimento: {g['medida_linear']}m")

    # IMPRIMIR BLOCOS ENCONTRADOS
    linhas_relatorio.append(f"\n[3] BLOCOS COM DADOS DE SOLO ({len(extraido['blocos'])} itens)")
    if not extraido['blocos']:
        linhas_relatorio.append("    Nenhum bloco/tabela sobre solo encontrado.")
    for b in extraido['blocos']:
        linhas_relatorio.append(f"    - Bloco: {b['nome_bloco']} | Layer: {b['layer']}")
        linhas_relatorio.append(f"      Atributos:")
        for k, v in b['atributos'].items():
            linhas_relatorio.append(f"        > {k}: {v}")
        linhas_relatorio.append("")

    linhas_relatorio.append("=" * 80)

    # Gravar tudo no ficheiro .txt
    with open(caminho_txt, 'w', encoding='utf-8') as f_out:
        f_out.write("\n".join(linhas_relatorio))

    # Avisa o utilizador no terminal que o processo terminou e onde está o ficheiro
    print(f"Sucesso! O output era muito grande e foi guardado em:")
    print(f"-> {caminho_txt}")

if __name__ == "__main__":
    # Substitua pelo caminho correto do seu ficheiro JSON gerado pelo AutoCAD
    JSON_ENTRADA = r"C:\Users\vinic\Downloads\teste.JSON"
    auditar_movimentos_solo(JSON_ENTRADA)