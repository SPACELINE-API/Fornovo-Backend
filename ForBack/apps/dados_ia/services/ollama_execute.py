import os
import re
import json
import unicodedata
import multiprocessing
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, OllamaLLM

from apps.dados_ia.services.ollama_installer import ensure_ollama_cuda

CHROMA_DIR = Path.home() / ".chroma_normas_db"
MODELO_LLM = "llama3.1:8b"
MODELO_EMBEDDING = "nomic-embed-text"

_NUM_CPU = multiprocessing.cpu_count()
_NUM_THREADS = min(6, max(1, _NUM_CPU // 2))

_GPU = ensure_ollama_cuda()
_USE_GPU = _GPU.get("cuda_active", False)

os.environ.setdefault("OLLAMA_NUM_PARALLEL", "1")
os.environ.setdefault("OLLAMA_MAX_LOADED_MODELS", "2")

VERIFICACOES = [
    {
        "id": "ATR-01",
        "categoria": "Aterramento",
        "descricao": "Sistema de aterramento presente (malha, haste cobreada, eletrodo)",
        "query_norma": "sistema aterramento eletrodo haste cobreada malha NBR 5410",
        "busca_textos": ["MALHA TERRA", "HASTE COBREADA", "ATERRAMENTO", "TERRA", "MALHA DE ATERRAMENTO", "ELETRODO"],
        "busca_layers": ["ELE-MALHA TERRA", "ELE-HASTE COBREADA", "MALHA TERRA", "HASTE COBREADA", "ATERRAMENTO", "Elétrica"],
    },
    {
        "id": "ATR-02",
        "categoria": "Aterramento",
        "descricao": "Seção mínima do condutor de aterramento (≥ 16mm² cobre nu para malha enterrada)",
        "query_norma": "seção mínima condutor aterramento cobre nu milímetros NBR 5410",
        "busca_textos": ["#35MM²", "#50MM²", "NÚ #35", "NÚ #50", "CABO DE COBRE", "MM²", "COBRE NU"],
        "busca_layers": ["ELE-TEXTOS", "TEXTOS", "Elétrica"],
    },
    {
        "id": "ATR-03",
        "categoria": "Aterramento",
        "descricao": "Conexões de aterramento por solda exotérmica ou conector apropriado",
        "query_norma": "conexão aterramento solda exotérmica conector aprovado NBR",
        "busca_textos": ["SOLDA EXOTÉRMICA", "CONECTORES APROPRIADOS", "CONECTOR SPLIT BOLT", "CONECTOR DE EMENDA", "CONECTOR BIMETÁLICO"],
        "busca_layers": ["ELE-SOLDA EXOTÉRMICA", "ELE-CONECTOR SPLIT BOLT", "ELE-CONECTOR DE EMENDA", "ELE-CONCETOR BIMETÁLICO", "SOLDA", "CONECTOR", "Elétrica"],
    },
    {
        "id": "ATR-04",
        "categoria": "Aterramento",
        "descricao": "Equipotencialização de massas metálicas (eletrocalhas, eletrodutos, tubulações)",
        "query_norma": "equipotencialização massas metálicas eletrocalhas eletrodutos NBR 5410",
        "busca_textos": ["EQUIPOTENCIALIZAÇÃO", "MASSAS METÁLICAS", "ELETROCALHAS", "ELETRODUTOS", "COMBATE A INCÊNDIO"],
        "busca_layers": ["ELE-TEXTOS", "TEXTOS", "ELETROCALHA", "ELETRODUTO", "Elétrica"],
    },
    {
        "id": "ATR-05",
        "categoria": "Aterramento",
        "descricao": "Caixa de inspeção presente para acesso ao sistema de aterramento",
        "query_norma": "caixa inspeção aterramento acesso medição resistência NBR",
        "busca_textos": ["CX. INSPEÇÃO", "CAIXA DE INSPEÇÃO", "CX INSPECAO"],
        "busca_layers": ["ELE-CX. INSPEÇÃO", "CX. INSPEÇÃO", "CAIXA INSPEÇÃO", "Elétrica"],
    },
    {
        "id": "SPDA-01",
        "categoria": "SPDA (Para-raios)",
        "descricao": "Sistema SPDA presente com malha e descidas identificadas",
        "query_norma": "SPDA para-raios malha descida captores NBR 5419",
        "busca_textos": ["SPDA", "MALHA SPDA", "DESCIDA BARRA CHATA", "TERMINAL AÉREO", "PARA-RAIOS", "CAPTOR"],
        "busca_layers": ["ELE-MALHA SPDA", "ELE-TERMINAL AÉREO", "ELE-TUBO DESCIDA", "MALHA SPDA", "SPDA", "TERMINAL", "Elétrica"],
    },
    {
        "id": "SPDA-02",
        "categoria": "SPDA (Para-raios)",
        "descricao": "Descidas em barra chata de alumínio com dimensões adequadas (mín. 7/8\"x1/8\")",
        "query_norma": "descida SPDA barra chata alumínio dimensão mínima NBR 5419",
        "busca_textos": ["BARRA CHATA", "ALUMÍNIO", "7/8", "1/8", "DESCIDA"],
        "busca_layers": ["ELE-BARRA CHATA ALUMÍNIO", "ELE-TEXTOS", "BARRA CHATA", "SPDA", "TEXTOS", "Elétrica"],
    },
    {
        "id": "SPDA-03",
        "categoria": "SPDA (Para-raios)",
        "descricao": "Fixadores e rebites utilizados nas descidas do SPDA",
        "query_norma": "fixação descidas SPDA parafusos fixadores NBR 5419",
        "busca_textos": ["FIXADOR", "REBITE", "PARAFUSO", "BUCHA DE NYLON"],
        "busca_layers": ["ELE-FIXADOR GELCAM", "ELE-REBITE", "FIXADOR", "REBITE", "SPDA", "Elétrica"],
    },
    {
        "id": "PROT-01",
        "categoria": "Proteção e Quadros",
        "descricao": "Quadro geral de distribuição (QDG) presente e identificado",
        "query_norma": "quadro geral distribuição QDG identificação NBR 5410",
        "busca_textos": ["QDG", "QUADRO", "PAINEL", "AUTOPORTANTE", "QD.", "QDC", "QGBT"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "QUADRO", "Elétrica"],
    },
    {
        "id": "PROT-02",
        "categoria": "Proteção e Quadros",
        "descricao": "Disjuntores com capacidade de interrupção declarada (Icc ≥ 10kA para BT)",
        "query_norma": "capacidade interrupção disjuntor corrente curto circuito Icc NBR 5410",
        "busca_textos": ["Icc=20kA", "Icc=18kA", "DISJUNTOR", "DISJ. GER.", "CX. MOLDADA", "ICC", "KA"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "DISJUNTOR", "Elétrica"],
    },
    {
        "id": "PROT-03",
        "categoria": "Proteção e Quadros",
        "descricao": "Barramento com seção mínima declarada (≥ 400A conforme projeto)",
        "query_norma": "barramento seção mínima amperagem quadro distribuição NBR 5410",
        "busca_textos": ["BARRAMENTO CENTRAL", "SECÇÃO MÍNIMA 400A", "400A", "BARRAMENTO"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "BARRAMENTO", "Elétrica"],
    },
    {
        "id": "PROT-04",
        "categoria": "Proteção e Quadros",
        "descricao": "Padrão de entrada de baixa tensão identificado (concessionária)",
        "query_norma": "padrão entrada baixa tensão concessionária ramal NBR 5410",
        "busca_textos": ["PADRÃO DE ENTRADA BAIXA TENSÃO", "CENTRO MEDIÇÃO", "DUPLO T 300", "PADRÃO DE ENTRADA"],
        "busca_layers": ["Elétrica", "ENTRADA", "PADRAO"],
    },
    {
        "id": "COND-01",
        "categoria": "Condutores",
        "descricao": "Isolação dos cabos compatível com temperatura e tensão (EPR 90°C, 1,0kV)",
        "query_norma": "isolação condutor temperatura máxima tensão nominal EPR NBR 5410",
        "busca_textos": ["EPR 90", "ISOL.1,0kV", "1,0KV", "EPR", "ISOLAÇÃO"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "CABO", "FIAÇÃO", "Elétrica"],
    },
    {
        "id": "COND-02",
        "categoria": "Condutores",
        "descricao": "Condutor de proteção (terra) presente em todos os circuitos",
        "query_norma": "condutor proteção terra PE circuito obrigatório NBR 5410",
        "busca_textos": ["TERRA", "CONDUTOR DE PROTEÇÃO", "PE"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "CABO", "Elétrica"],
    },
    {
        "id": "COND-03",
        "categoria": "Condutores",
        "descricao": "Condutor neutro identificado nos circuitos",
        "query_norma": "condutor neutro identificação cor azul claro NBR 5410",
        "busca_textos": ["NEUTRO", "CONDUTOR NEUTRO"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "CABO", "Elétrica"],
    },
    {
        "id": "CIRC-01",
        "categoria": "Circuitos e Cargas",
        "descricao": "Circuitos numerados e identificados individualmente (CS-2 a CS-45)",
        "query_norma": "identificação numeração circuitos quadro distribuição NBR 5410",
        "busca_textos": ["CS-", "CIRCUITO", "CK-"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "Elétrica"],
    },
    {
        "id": "CIRC-02",
        "categoria": "Circuitos e Cargas",
        "descricao": "Circuitos de ar condicionado com circuito exclusivo (uso específico)",
        "query_norma": "circuito exclusivo uso específico ar condicionado chuveiro NBR 5410",
        "busca_textos": ["AP. AR COND.", "BTU", "CORTINA AR", "AR CONDICIONADO", "AR COND"],
        "busca_layers": ["Elétrica", "CIRCUITO", "AR CONDICIONADO"],
    },
    {
        "id": "CIRC-03",
        "categoria": "Circuitos e Cargas",
        "descricao": "Indicação de carga (KW), corrente (A) e proteção (A) por circuito",
        "query_norma": "dimensionamento circuito carga corrente proteção projeto elétrico NBR 5410",
        "busca_textos": ["(KW)", "CARGA", "CORRENTE", "PROTECAO", "CABO"],
        "busca_layers": ["ELE-CIRCUITO", "CIRCUITO", "Elétrica"],
    },
    {
        "id": "DOC-01",
        "categoria": "Documentação",
        "descricao": "Notas técnicas e memória de cálculo referenciadas no projeto",
        "query_norma": "memória de cálculo ART documentação projeto elétrico NR-10 NBR",
        "busca_textos": ["ART", "MEMÓRIA DE CÁLCULO", "PROFISSIONAL CAPACITADO", "VALIDAÇÃO", "MEMORIA DE CALCULO"],
        "busca_layers": ["ELE-TEXTOS", "TEXTOS", "NOTAS", "Elétrica"],
    },
    {
        "id": "DOC-02",
        "categoria": "Documentação",
        "descricao": "Projeto classificado como básico com exigência de validação profissional",
        "query_norma": "projeto básico aterramento validação profissional habilitado NR-10",
        "busca_textos": ["PROJETO BÁSICO", "VALIDAÇÃO", "EMPRESA VENCEDORA", "PROJETO BASICO"],
        "busca_layers": ["ELE-TEXTOS", "TEXTOS", "NOTAS", "Elétrica"],
    },
]

REGRAS_VALORES = {
    "ATR-01": {"tipo": "existe", "campos": ["MALHA TERRA", "MALHA DE ATERRAMENTO", "HASTE COBREADA", "HASTE DE TERRA", "ELETRODO"]},
    "ATR-02": {"tipo": "secao_mm2", "minimo": 16, "padrao": r"#([0-9]+)\s*mm", "padrao_alt": r"COBRE\s+N[ÚU].*?#([0-9]+)"},
    "ATR-03": {"tipo": "existe", "campos": ["SOLDA EXOTERMICA", "CONECTOR SPLIT BOLT", "CONECTOR DE EMENDA", "CONECTOR BIMETALICO", "CONECTORES APROPRIADOS"]},
    "ATR-04": {"tipo": "existe", "campos": ["EQUIPOTENCIALIZACAO", "MASSAS METALICAS", "ELETROCALHAS", "ATERRADAS"]},
    "ATR-05": {"tipo": "existe", "campos": ["CAIXA DE INSPECAO", "CX. INSPECAO"]},
    "SPDA-01": {"tipo": "existe", "campos": ["MALHA SPDA", "MALHA DO SPDA", "MALHA DE BARRA CHATA DO SPDA", "TERMINAL"]},
    "SPDA-02": {"tipo": "existe", "campos": ["BARRA CHATA", "ALUMINIO", "DESCIDA"]},
    "SPDA-03": {"tipo": "existe", "campos": ["FIXADOR", "REBITE", "PARAFUSO"]},
    "PROT-01": {"tipo": "existe", "campos": ["QDG", "QUADRO DE DISTRIBUICAO", "PAINEL"]},
    "PROT-02": {"tipo": "icc_ka", "minimo": 10, "padrao": r"ICC\s*=\s*([0-9]+)\s*KA"},
    "PROT-03": {"tipo": "amperagem", "minimo": 400, "padrao": r"([0-9]+)\s*A\b"},
    "PROT-04": {"tipo": "existe", "campos": ["PADRAO DE ENTRADA", "BAIXA TENSAO", "CENTRO MEDICAO"]},
    "COND-01": {"tipo": "existe_todos", "campos": ["EPR", "90", "1,0KV", "ISOL"]},
    "COND-02": {"tipo": "existe", "campos": ["TERRA", "ATERRAMENTO", "PROTECAO"]},
    "COND-03": {"tipo": "existe", "campos": ["NEUTRO"]},
    "CIRC-01": {"tipo": "regex", "padrao": r"CS-[0-9]+"},
    "CIRC-02": {"tipo": "existe", "campos": ["AR COND", "BTU"]},
    "CIRC-03": {"tipo": "existe_todos", "campos": ["CARGA", "CORRENTE"]},
    "DOC-01": {"tipo": "existe", "campos": ["ART", "MEMORIA DE CALCULO", "PROFISSIONAL"]},
    "DOC-02": {"tipo": "existe", "campos": ["PROJETO BASICO", "VALIDACAO"]},
}


def executar_agente(dados_extracao: dict) -> str:
    print("=" * 60)
    print("AGENTE DE CONFORMIDADE NBR")
    print("=" * 60)

    print("\n[1/3] Carregando dados da planta...")
    indice = _preparar_indice(dados_extracao)
    resumo = _resumo_planta(dados_extracao)
    print(f"  Arquivo: {Path(dados_extracao.get('arquivo', 'desconhecido')).name}")
    print(f"  Layers encontrados: {len(indice['layers_presentes'])}")
    print(f"  Layers reais: {sorted(indice['layers_presentes'])}")
    print(f"  Textos indexados: {len(indice['todos_textos'])}")
    amostra_textos = [f"    [{t[1]}] {t[2][:80]}" for t in indice['todos_textos'][:15]]
    if amostra_textos:
        print(f"  Amostra de textos (até 15):")
        for linha in amostra_textos:
            print(linha)

    print("\n[2/3] Inicializando modelos Ollama...")
    gpu_layers = -1 if _USE_GPU else 0
    embeddings = OllamaEmbeddings(model=MODELO_EMBEDDING, num_thread=_NUM_THREADS, num_gpu=gpu_layers)
    llm = OllamaLLM(
        model=MODELO_LLM,
        num_ctx=4096,
        num_predict=512,
        num_thread=_NUM_THREADS,
        num_gpu=gpu_layers,
        temperature=0,
        top_k=20,
        top_p=0.8,
        repeat_penalty=1.0,
        keep_alive="30m",
    )
    db_normas = Chroma(persist_directory=str(CHROMA_DIR), embedding_function=embeddings)
    if _USE_GPU:
        print(f"  GPU: {_GPU['gpu_name']} ({_GPU['vram_mb']} MB VRAM) — CUDA ativo")
    else:
        print("  GPU: não detectada ou CUDA indisponível — processando em CPU")
    print(f"  LLM: {MODELO_LLM} (threads={_NUM_THREADS}, ctx=4096)")
    print(f"  Embeddings: {MODELO_EMBEDDING}")
    print(f"  ChromaDB: {CHROMA_DIR}")

    print("  Aquecendo modelo (warmup)...")
    try:
        llm.invoke("Responda apenas: OK")
    except Exception:
        pass

    total = len(VERIFICACOES)
    print(f"\n[3/3] Executando {total} verificações...\n")
    print("-" * 60)

    resultados = []
    conformes = 0
    nao_conformes = 0
    inconclusivos = 0

    for i, verif in enumerate(VERIFICACOES, 1):
        print(f"  [{i:02d}/{total}] {verif['id']} — {verif['descricao'][:50]}...")

        evidencias = _coletar_evidencias(verif, indice)

        textos_found = len(evidencias["ocorrencias_texto"])
        layers_found = len(evidencias["layers_encontrados"])
        layers_miss = len(evidencias["layers_ausentes"])
        print(f"          Evidências: {textos_found} texto(s) | {layers_found} layer(s) encontrado(s): {evidencias['layers_encontrados']} | {layers_miss} layer(s) ausente(s): {evidencias['layers_ausentes']}")

        contexto_norma = _consultar_norma(verif["query_norma"], db_normas)
        avaliacao = _avaliar_com_llm(llm, verif, contexto_norma, resumo, evidencias)

        status = avaliacao["status"]
        icone = {"CONFORME": "✅", "NÃO CONFORME": "❌", "INCONCLUSIVO": "⚠️"}.get(status, "❓")

        if status == "CONFORME":
            conformes += 1
        elif status == "NÃO CONFORME":
            nao_conformes += 1
        else:
            inconclusivos += 1

        pct = round(i / total * 100)
        barra = ("█" * (pct // 5)).ljust(20)
        print(f"          {icone} {status}")
        print(f"          Progresso: [{barra}] {pct}% ({i}/{total})")
        print()

        norma_match = re.search(r'(NBR\s+\d+|NR-\d+)', verif["query_norma"], re.IGNORECASE)
        norma_codigo = norma_match.group(1).upper() if norma_match else "NBR GERAL"

        resultados.append({
            "id": verif["id"],
            "norma_codigo": norma_codigo,
            "categoria": verif["categoria"],
            "descricao": verif["descricao"],
            "avaliacao": avaliacao,
            "evidencias": evidencias,
        })

    print("-" * 60)
    print("\nRESULTADO FINAL")
    print("-" * 60)
    print(f"  ✅ Conformes:      {conformes}/{total} ({round(conformes/total*100)}%)")
    print(f"  ❌ Não Conformes:  {nao_conformes}/{total} ({round(nao_conformes/total*100)}%)")
    print(f"  ⚠️  Inconclusivos:  {inconclusivos}/{total} ({round(inconclusivos/total*100)}%)")
    print("\nGerando relatório...")

    relatorio = _gerar_relatorio(resultados, dados_extracao)

    print("Relatório gerado com sucesso.")
    print("=" * 60)

    return {
        "status": "sucesso",
        "mensagem": "Elementos validados pela IA Real (Ollama + LangChain).",
        "relatorio_md": relatorio,
        "insights": resultados
    }


def _preparar_indice(extracao: dict) -> dict:
    todos_textos = []
    for t in extracao.get("textos", []):
        conteudo = t["conteudo"].strip()
        if conteudo:
            conteudo_limpo = _limpar_texto_dxf(conteudo)
            if conteudo_limpo:
                todos_textos.append((conteudo_limpo, t["layer"], conteudo))
    return {
        "todos_textos": todos_textos,
        "layers_presentes": set(extracao.get("layers", [])),
    }


def _resumo_planta(extracao: dict) -> str:
    r = extracao.get("resumo", {})
    layers_ele = [l for l in extracao.get("layers", []) if "ELE" in l.upper() or "ELÉTR" in l.upper()]
    return (
        f"Arquivo: {Path(extracao.get('arquivo', '')).name}\n"
        f"Layers elétricos: {', '.join(layers_ele)}\n"
        f"Total entidades: {r.get('total_entidades', 0)}\n"
        f"Total textos: {r.get('total_textos', 0)}"
    )


def _limpar_texto_dxf(texto: str) -> str:
    t = _remover_acentos(texto.upper())
    t = re.sub(r'%%[A-Z]', '', t)
    t = re.sub(r'\\P', ' ', t)
    t = re.sub(r'\\[a-zA-Z]\d*[;,]?', ' ', t)
    t = re.sub(r'[{}\\()]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


def _match_texto_flexivel(texto_limpo: str, termo: str) -> bool:
    t = _remover_acentos(termo.upper().strip())
    if t in texto_limpo:
        return True
    t_sem_espacos = t.replace(' ', '')
    texto_sem_espacos = texto_limpo.replace(' ', '')
    if t_sem_espacos in texto_sem_espacos:
        return True
    palavras_termo = t.split()
    if len(palavras_termo) > 1:
        if all(p in texto_limpo for p in palavras_termo):
            return True
    return False


def _coletar_evidencias(verificacao: dict, indice: dict) -> dict:
    ocorrencias_texto = []
    for termo in verificacao.get("busca_textos", []):
        for conteudo_up, layer, conteudo_orig in indice["todos_textos"]:
            if _match_texto_flexivel(conteudo_up, termo):
                entrada = f"[{layer}] \"{conteudo_orig[:80]}\""
                if entrada not in ocorrencias_texto:
                    ocorrencias_texto.append(entrada)
        if len(ocorrencias_texto) >= 5:
            break
    layers_esperados = verificacao.get("busca_layers", [])
    layers_presentes_real = indice["layers_presentes"]
    layers_encontrados = []
    layers_ausentes = []
    for termo in layers_esperados:
        match = any(_match_layer_flexivel(layer_real, termo) for layer_real in layers_presentes_real)
        if match:
            matched = [lr for lr in layers_presentes_real if _match_layer_flexivel(lr, termo)]
            layers_encontrados.extend(matched)
        else:
            layers_ausentes.append(termo)
    seen = set()
    layers_encontrados_unicos = []
    for l in layers_encontrados:
        if l not in seen:
            seen.add(l)
            layers_encontrados_unicos.append(l)
    return {
        "ocorrencias_texto": ocorrencias_texto[:5],
        "layers_encontrados": layers_encontrados_unicos,
        "layers_ausentes": layers_ausentes,
    }


def _consultar_norma(query: str, db: Chroma, k: int = 5) -> str:
    docs = db.similarity_search(query, k=k)
    return "\n\n---\n\n".join(d.page_content[:600] for d in docs)


def _remover_acentos(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _normalizar_para_comparacao(nome: str) -> str:
    s = _remover_acentos(nome.upper().strip())
    s = re.sub(r'[-_./\s]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _match_layer_flexivel(layer_real: str, termo_busca: str) -> bool:
    l = _normalizar_para_comparacao(layer_real)
    t = _normalizar_para_comparacao(termo_busca)
    if l == t:
        return True
    if t in l or l in t:
        return True
    prefixos_remover = ["ELE ", "ELETRICA ", "ELETRICO ", "ELECTRICAL "]
    l_sem_prefixo = l
    t_sem_prefixo = t
    for p in prefixos_remover:
        l_sem_prefixo = l_sem_prefixo.replace(p, "").strip()
        t_sem_prefixo = t_sem_prefixo.replace(p, "").strip()
    if l_sem_prefixo == t_sem_prefixo:
        return True
    if t_sem_prefixo in l_sem_prefixo or l_sem_prefixo in t_sem_prefixo:
        return True
    palavras_layer = set(l_sem_prefixo.split())
    palavras_termo = set(t_sem_prefixo.split())
    if palavras_termo and palavras_termo.issubset(palavras_layer):
        return True
    intersecao = palavras_layer & palavras_termo
    if palavras_termo and len(intersecao) >= max(1, len(palavras_termo) * 0.5):
        return True
    return False


def _validar_valores(verificacao_id: str, evidencias: dict) -> dict:
    regra = REGRAS_VALORES.get(verificacao_id)
    if not regra:
        return {"ok": False, "detalhe": "Sem regra de validação definida.", "valores": []}

    textos_limpos = [_limpar_texto_dxf(e) for e in evidencias.get("ocorrencias_texto", [])]
    textos_concat = " ".join(textos_limpos)
    tipo = regra["tipo"]

    if tipo == "existe":
        encontrados = [c for c in regra["campos"] if c in textos_concat]
        return {
            "ok": len(encontrados) > 0,
            "detalhe": f"Termos encontrados: {encontrados}" if encontrados else f"Nenhum dos termos {regra['campos']} encontrado.",
            "valores": encontrados,
        }

    if tipo == "existe_todos":
        encontrados = [c for c in regra["campos"] if c in textos_concat]
        return {
            "ok": len(encontrados) == len(regra["campos"]),
            "detalhe": f"Encontrados {len(encontrados)}/{len(regra['campos'])}: {encontrados}",
            "valores": encontrados,
        }

    if tipo == "regex":
        matches = re.findall(regra["padrao"], textos_concat)
        return {
            "ok": len(matches) > 0,
            "detalhe": f"Padrões encontrados: {matches}" if matches else "Nenhum padrão identificado nos textos.",
            "valores": matches,
        }

    if tipo in ("secao_mm2", "icc_ka", "amperagem"):
        padrao_principal = regra["padrao"]
        matches = re.findall(padrao_principal, textos_concat)

        if not matches:
            padrao_alt = regra.get("padrao_alt")
            if padrao_alt:
                matches = re.findall(padrao_alt, textos_concat)

        valores_num = []
        for m in matches:
            try:
                valores_num.append(int(m))
            except (ValueError, TypeError):
                pass
        if not valores_num:
            return {"ok": False, "detalhe": "Nenhum valor numérico identificado nos textos.", "valores": []}
        max_val = max(valores_num)
        atende = max_val >= regra["minimo"]
        return {
            "ok": atende,
            "detalhe": f"Máximo encontrado: {max_val} (mínimo exigido: {regra['minimo']})",
            "valores": valores_num,
        }

    return {"ok": False, "detalhe": "Tipo de regra desconhecido.", "valores": []}


def _avaliar_evidencia_forte(verificacao_id: str, evidencias: dict, valor_check: dict) -> dict | None:
    tem_textos = len(evidencias["ocorrencias_texto"]) > 0
    tem_layers = len(evidencias["layers_encontrados"]) > 0
    layers_aus = len(evidencias["layers_ausentes"])
    valores_ok = valor_check["ok"]

    if not tem_textos and not tem_layers:
        return {
            "status": "NÃO CONFORME",
            "justificativa": "Nenhuma evidência encontrada na planta para este critério.",
            "recomendacao": "Incluir os elementos exigidos pela norma no projeto.",
        }

    if tem_layers and not tem_textos:
        return {
            "status": "INCONCLUSIVO",
            "justificativa": f"Layer(s) elétrico(s) identificado(s) ({', '.join(evidencias['layers_encontrados'])}), porém nenhum texto comprobatório encontrado para este critério. Análise manual necessária.",
            "recomendacao": "Revisar manualmente o conteúdo do layer para verificar se o requisito foi atendido.",
        }

    if tem_layers and layers_aus == 0 and tem_textos and valores_ok:
        return {
            "status": "CONFORME",
            "justificativa": f"Elementos identificados e valores validados. Layers: {', '.join(evidencias['layers_encontrados'])}. {valor_check['detalhe']}.",
            "recomendacao": "Manter conforme documentado.",
        }

    if tem_layers and layers_aus == 0 and tem_textos and not valores_ok:
        return {
            "status": "NÃO CONFORME",
            "justificativa": f"Layers presentes ({', '.join(evidencias['layers_encontrados'])}), porém {valor_check['detalhe']}.",
            "recomendacao": "Verificar se os valores atendem os mínimos da norma.",
        }

    return None


def _avaliar_com_llm(llm, verificacao: dict, contexto_norma: str, resumo: str, evidencias: dict) -> dict:
    tem_textos = len(evidencias["ocorrencias_texto"]) > 0
    tem_layers = len(evidencias["layers_encontrados"]) > 0
    layers_aus = ", ".join(evidencias["layers_ausentes"]) or "nenhum"

    if not tem_textos and not tem_layers:
        return {
            "status": "NÃO CONFORME",
            "justificativa": f"Nenhuma evidência encontrada. Layers esperados ausentes: {layers_aus}.",
            "recomendacao": f"Incluir no projeto os elementos exigidos: {layers_aus}.",
        }

    if tem_layers and not tem_textos:
        return {
            "status": "INCONCLUSIVO",
            "justificativa": f"Layer(s) elétrico(s) identificado(s) ({', '.join(evidencias['layers_encontrados'])}), porém nenhum texto comprobatório encontrado para este critério. Layers ausentes: {layers_aus}.",
            "recomendacao": "Revisar manualmente o conteúdo do layer para verificar se o requisito foi atendido.",
        }

    valor_check = _validar_valores(verificacao["id"], evidencias)

    avaliacao_forte = _avaliar_evidencia_forte(verificacao["id"], evidencias, valor_check)
    if avaliacao_forte is not None:
        return avaliacao_forte

    ocorrencias_str = "\n".join(evidencias["ocorrencias_texto"]) or "Nenhum texto encontrado."
    layers_enc = ", ".join(evidencias["layers_encontrados"]) or "nenhum"
    valores_info = f"Validação automática: {valor_check['detalhe']}" if valor_check else "Sem validação automática."

    prompt = f"""Você é um auditor técnico de normas elétricas brasileiras.

Avalie o critério abaixo na planta elétrica e retorne APENAS JSON.

CRITÉRIO: {verificacao['descricao']}

TRECHO DA NORMA:
{contexto_norma}

EVIDÊNCIAS ENCONTRADAS NA PLANTA:
Textos: {ocorrencias_str}
Layers presentes: {layers_enc}
Layers ausentes: {layers_aus}
{valores_info}

REGRAS DE AVALIAÇÃO:
- CONFORME: quando há evidência clara de que o requisito foi atendido (layers presentes E textos confirmam valores adequados)
- NÃO CONFORME: quando não há evidência suficiente, ou os valores encontrados são inferiores ao mínimo da norma
- INCONCLUSIVO: apenas quando há evidência parcial que não permite conclusão definitiva

Responda SOMENTE este JSON, sem texto antes ou depois:
{{"status":"CONFORME"|"NÃO CONFORME"|"INCONCLUSIVO","justificativa":"...","recomendacao":"..."}}"""

    resposta_raw = llm.invoke(prompt)

    resposta_limpa = re.sub(r'<think>.*?</think>', '', resposta_raw, flags=re.DOTALL).strip()

    try:
        match = re.search(r'\{[^{}]*"status"[^{}]*\}', resposta_limpa, re.DOTALL)
        if match:
            resultado = json.loads(match.group())
            if resultado.get("status") in ("CONFORME", "NÃO CONFORME", "INCONCLUSIVO"):
                if resultado.get("status") == "INCONCLUSIVO" and not tem_textos and not tem_layers:
                    resultado["status"] = "NÃO CONFORME"
                    resultado["justificativa"] = "Nenhum texto comprobatório encontrado. " + resultado.get("justificativa", "")
                return resultado
    except Exception:
        pass

    try:
        status_match = re.search(r'"status"\s*:\s*"(CONFORME|NÃO CONFORME|INCONCLUSIVO)"', resposta_limpa)
        just_match = re.search(r'"justificativa"\s*:\s*"([^"]{10,})', resposta_limpa)
        if status_match:
            return {
                "status": status_match.group(1),
                "justificativa": just_match.group(1)[:300] if just_match else "Extraído parcialmente.",
                "recomendacao": "",
            }
    except Exception:
        pass

    if tem_layers and tem_textos and valor_check["ok"]:
        return {
            "status": "CONFORME",
            "justificativa": f"Evidências presentes e valores validados. {valor_check['detalhe']}.",
            "recomendacao": "Confirmar conformidade em revisão manual.",
        }
    elif tem_layers or tem_textos:
        return {
            "status": "INCONCLUSIVO",
            "justificativa": f"Evidência parcial encontrada. {valor_check['detalhe']}. Análise manual recomendada.",
            "recomendacao": "Revisar manualmente o item com base nas evidências parciais.",
        }
    else:
        return {
            "status": "NÃO CONFORME",
            "justificativa": f"Não foi possível comprovar conformidade. Layers ausentes: {layers_aus}.",
            "recomendacao": "Revisar o projeto e incluir os elementos exigidos pela norma.",
        }


def _gerar_relatorio(resultados: list, extracao: dict) -> str:
    nome_arquivo = Path(extracao.get('arquivo', 'desconhecido')).name
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")

    conformes = sum(1 for r in resultados if r["avaliacao"]["status"] == "CONFORME")
    nao_conformes = sum(1 for r in resultados if r["avaliacao"]["status"] == "NÃO CONFORME")
    inconclusivos = sum(1 for r in resultados if r["avaliacao"]["status"] == "INCONCLUSIVO")
    total = len(resultados)

    icone = {"CONFORME": "✅", "NÃO CONFORME": "❌", "INCONCLUSIVO": "⚠️"}

    linhas = [
        "# Relatório de Conformidade NBR — Planta Elétrica",
        "",
        f"**Arquivo analisado:** `{nome_arquivo}`  ",
        f"**Data/Hora:** {data_hora}  ",
        f"**Normas de referência:** NBR 5410, NBR 5419, NR-10, NBR 6123, NBR 9050  ",
        f"**Total de verificações:** {total}  ",
        "",
        "## Sumário Executivo",
        "",
        "| Status | Qtd | % |",
        "|--------|-----|---|",
        f"| ✅ Conforme      | {conformes} | {100*conformes//total}% |",
        f"| ❌ Não Conforme  | {nao_conformes} | {100*nao_conformes//total}% |",
        f"| ⚠️  Inconclusivo  | {inconclusivos} | {100*inconclusivos//total}% |",
        "",
        "---",
        "",
    ]

    categorias = {}
    for r in resultados:
        categorias.setdefault(r["categoria"], []).append(r)

    for categoria, itens in categorias.items():
        conf_cat = sum(1 for i in itens if i["avaliacao"]["status"] == "CONFORME")
        linhas.append(f"## {categoria}  *({conf_cat}/{len(itens)} conformes)*")
        linhas.append("")

        for item in itens:
            av = item["avaliacao"]
            status = av["status"]
            ic = icone.get(status, "❓")

            linhas.append(f"### {ic} [{item['id']}] {item['descricao']}")
            linhas.append("")
            linhas.append(f"**Status:** `{status}`  ")
            linhas.append(f"**Justificativa:** {av['justificativa']}  ")

            if av.get("recomendacao"):
                linhas.append(f"**Recomendação:** {av['recomendacao']}  ")

            ev = item.get("evidencias", {})

            if ev.get("layers_encontrados"):
                linhas.append(f"**Layers confirmados:** {', '.join(f'`{l}`' for l in ev['layers_encontrados'])}")

            if ev.get("layers_ausentes"):
                linhas.append(f"**Layers não encontrados:** {', '.join(f'`{l}`' for l in ev['layers_ausentes'])}")

            if ev.get("ocorrencias_texto"):
                linhas.append("")
                linhas.append("**Evidências no texto da planta:**")
                for oc in ev["ocorrencias_texto"][:5]:
                    linhas.append(f"- {oc}")

            linhas.append("")

    linhas += [
        "---",
        "",
        "## Observações Gerais",
        "",
        "- Relatório gerado automaticamente por agente RAG local (Ollama + ChromaDB).",
        "- Itens **INCONCLUSIVOS** indicam evidências insuficientes — recomenda-se revisão manual.",
        "- Este relatório **não substitui** laudo técnico assinado por engenheiro responsável.",
        "",
        "*Gerado automaticamente — Pipeline RAG Local (Ollama + LangChain + ChromaDB)*",
    ]

    return "\n".join(linhas)