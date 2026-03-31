import json
import re

def auditar_limpeza_interdicoes(caminho_json: str):
    print(f"A ler o ficheiro: {caminho_json}...")
    print("A analisar dados sobre Limpeza e Interdições. Aguarde...\n")
    
    try:
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"❌ Erro: Ficheiro '{caminho_json}' não encontrado.")
        return

    # Desempacota o JSON caso esteja encapsulado
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
    blocos = dados.get('blocos', []) + [e for e in dados.get('entidades', []) if e.get('tipo') in ('INSERT', 'BLOCK')]
    layers_projeto = dados.get('layers', [])
    
    # Palavras-chave abrangentes (sem acentos para facilitar a busca)
    kw_limpeza = ['LIMPEZ', 'LIMPAR', 'ROCAD', 'ROÇAD', 'CAPIN']
    kw_interdicao = ['INTERDIC', 'INTERDIÇ', 'ISOLAMENT', 'TAPUME', 'BLOQUEI', 'ADJACENCI', 'ADJACÊNCI']
    
    print("=" * 80)
    print(" 🧹 RELATÓRIO: LIMPEZA E INTERDIÇÕES DE OBRA 🚧 ")
    print("=" * 80)
    
    # ---------------------------------------------------------
    # 1. Busca em Layers
    # ---------------------------------------------------------
    layers_encontradas = []
    for l in layers_projeto:
        l_upper = l.upper()
        if any(k in l_upper for k in kw_limpeza + kw_interdicao):
            layers_encontradas.append(l)
    
    print("\n--- 1. LAYERS ENCONTRADAS ---")
    if layers_encontradas:
        for l in layers_encontradas:
            print(f"  • {l}")
    else:
        print("  ❌ Nenhuma layer nomeada com termos de limpeza ou interdição.")

    # ---------------------------------------------------------
    # 2. Busca em Textos e Anotações
    # ---------------------------------------------------------
    print("\n--- 2. TEXTOS ENCONTRADOS ---")
    textos_encontrados = False
    
    for t in textos:
        c_raw = t.get('conteudo', '')
        # Normaliza o texto para a busca
        c_upper = c_raw.upper().replace('Ç', 'C').replace('Ã', 'A').replace('ÇÕES', 'COES')
        
        tem_limpeza = any(k in c_upper for k in kw_limpeza)
        tem_interdicao = any(k in c_upper for k in kw_interdicao)
        
        if tem_limpeza or tem_interdicao:
            textos_encontrados = True
            
            # Limpa as tags de formatação do AutoCAD
            c_limpo = re.sub(r'\{[^{}]*\}', '', c_raw).strip()
            c_limpo = re.sub(r'\\[a-zA-Z0-9]+\d*\.?.?x?;', ' ', c_limpo).strip()
            c_limpo = re.sub(r'\s+', ' ', c_limpo).strip()
            
            categoria = "LIMPEZA" if tem_limpeza else "INTERDIÇÃO"
            if tem_limpeza and tem_interdicao: 
                categoria = "LIMPEZA E INTERDIÇÃO"
            
            print(f"🔹 [{categoria}] Texto: '{c_limpo}'")
            print(f"   Layer: {t.get('layer', '')} | Posição: {t.get('posicao', [0,0])}")
            print("-" * 50)
            
    if not textos_encontrados:
        print("  ❌ Nenhum texto ou anotação relacionado encontrado na planta.")

    # ---------------------------------------------------------
    # 3. Busca em Blocos / Atributos Ocultos
    # ---------------------------------------------------------
    print("\n--- 3. BLOCOS E ATRIBUTOS (Metadados do CAD) ---")
    blocos_encontrados = False
    
    for b in blocos:
        nome_bloco = b.get('nome', '').upper()
        atributos = b.get('atributos', {})
        dados_b = b.get('dados', {})
        
        dic_para_busca = {**atributos, **dados_b}
        
        tem_alvo = False
        categoria = ""
        
        # Verifica no nome do bloco
        if any(k in nome_bloco for k in kw_limpeza): 
            tem_alvo = True; categoria += "LIMPEZA "
        if any(k in nome_bloco for k in kw_interdicao): 
            tem_alvo = True; categoria += "INTERDIÇÃO "
            
        # Verifica dentro dos atributos do bloco
        for k, v in dic_para_busca.items():
            v_str = str(v).upper().replace('Ç', 'C').replace('Ã', 'A')
            if any(kw in v_str for kw in kw_limpeza):
                tem_alvo = True; categoria += "LIMPEZA "
            if any(kw in v_str for kw in kw_interdicao):
                tem_alvo = True; categoria += "INTERDIÇÃO "
                
        if tem_alvo:
            blocos_encontrados = True
            # Evita categorias duplicadas na string
            cat_final = " E ".join(list(set(categoria.split()))) 
            
            print(f"🔸 [{cat_final}] Bloco: '{b.get('nome', '')}'")
            print(f"   Posição: {b.get('posicao', b.get('insercao', 'N/A'))}")
            print(f"   Atributos Ocultos: {dic_para_busca}")
            print("-" * 50)

    if not blocos_encontrados:
        print("  ❌ Nenhum bloco com esses atributos encontrado.")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    # Caminho do seu JSON
    JSON_ENTRADA = r"C:\Users\vinic\Downloads\teste.JSON" 
    
    auditar_limpeza_interdicoes(JSON_ENTRADA)
