import json
import re
import math

def auditar_estruturas_ambientes(caminho_json: str):
    print(f"A ler o ficheiro: {caminho_json}...")
    print("A analisar ambientes, pilares, vigas e lajes. Aguarde...\n")
    
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"❌ Erro: Ficheiro '{caminho_json}' não encontrado.")
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

    textos = dados.get('textos', []) or [e for e in dados.get('entidades', []) if e.get('tipo') in ('MTEXT', 'TEXT')]
    entidades = dados.get('entidades', [])
    
    ambientes = []
    kw_ambientes = ['SALA', 'CIRCULAÇ', 'CIRCULAC', 'CENTRO', 'BANHEIRO', 'QUARTO', 'COZINHA', 'DEPÓSITO', 'DEPOSITO', 'PÁTIO', 'PATIO', 'WC', 'COPA', 'AUDITÓRIO', 'BLOCO']
    
    for t in textos:
        c_raw = t.get('conteudo', '')
        c_limpo = re.sub(r'\{[^{}]*\}', '', c_raw)
        c_limpo = re.sub(r'\\[a-zA-Z0-9]+\d*\.?.?x?;', ' ', c_limpo).strip()
        c_upper = c_limpo.upper()
        
        if re.search(r'm[²2]', c_upper) or any(k in c_upper for k in kw_ambientes):
            nome_formatado = c_limpo.replace('\\P', ' ').replace('\\p', ' ').replace('\n', ' ')
            nome_final = re.sub(r'\s+', ' ', nome_formatado).strip()
            if nome_final:
                ambientes.append({
                    'nome': nome_final,
                    'posicao': t.get('posicao', [0, 0, 0])
                })

    estruturas = []
    for e in entidades:
        layer = e.get('layer', '').upper()
        tipo_est = None
        
        if 'PILAR' in layer: tipo_est = 'PILAR'
        elif 'VIGA' in layer: tipo_est = 'VIGA'
        elif 'LAJE' in layer: tipo_est = 'LAJE'
            
        if tipo_est:
            d = e.get('dados', {})
            tipo = e.get('tipo', '')
            pos = [0, 0, 0]
            medida = 0.0
            
            if tipo == 'LINE':
                medida = d.get('comprimento', 0.0)
                pos = d.get('inicio', [0, 0, 0])
            elif tipo in ('LWPOLYLINE', 'POLYLINE'):
                pts = d.get('pontos', [])
                if pts:
                    pos = pts[0]
                    total = 0.0
                    for i in range(len(pts) - 1):
                        total += math.sqrt((pts[i+1][0] - pts[i][0])**2 + (pts[i+1][1] - pts[i][1])**2)
                    medida = total
                    
            if medida > 0:
                estruturas.append({
                    'tipo': tipo_est,
                    'layer': e.get('layer', ''),
                    'medida': round(medida, 2),
                    'posicao': pos
                })

    resultado = {a['nome']: {'PILAR': [], 'VIGA': [], 'LAJE': []} for a in ambientes}
    if not ambientes:
        resultado['SEM AMBIENTE'] = {'PILAR': [], 'VIGA': [], 'LAJE': []}

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

    for amb_nome, dados_est in resultado.items():
        total_p = len(dados_est['PILAR'])
        total_v = len(dados_est['VIGA'])
        total_l = len(dados_est['LAJE'])
        
        if total_p == 0 and total_v == 0 and total_l == 0:
            continue
            
        print(f"\n🔹 Ambiente: '{amb_nome}'")
        
        if total_p > 0:
            print("   🔸 Pilares:")
            for p in dados_est['PILAR']:
                print(f"      - Layer: {p['layer']} | Medida/Perímetro: {p['medida']} unidades")
                
        if total_v > 0:
            print("   🔸 Vigas:")
            for v in dados_est['VIGA']:
                print(f"      - Layer: {v['layer']} | Comprimento: {v['medida']} unidades")
                
        if total_l > 0:
            print("   🔸 Lajes:")
            for l in dados_est['LAJE']:
                print(f"      - Layer: {l['layer']} | Perímetro: {l['medida']} unidades")
                
        print("-" * 60)

    print("\n" + "=" * 80)

if __name__ == "__main__":
    JSON_ENTRADA = r"C:\Users\vinic\Downloads\teste.JSON" 
    auditar_estruturas_ambientes(JSON_ENTRADA)