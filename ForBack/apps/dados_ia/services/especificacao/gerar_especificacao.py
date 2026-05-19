from __future__ import annotations

import io
import json
import logging
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Inches
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from langchain_ollama import OllamaLLM
import pandas as pd

from apps.dados_ia.services.ollama_installer import ensure_ollama_ready

from apps.dados_ia.services.memorial.pandas.levantamento_campo import levantamento_campo
from apps.dados_ia.services.memorial.pandas.serviços_preliminares import servicos_preliminares
from apps.dados_ia.services.memorial.pandas.estruturas_manual import estruturas
from apps.dados_ia.services.memorial.pandas.alvenarias import alvenarias
from apps.dados_ia.services.memorial.pandas.acabamentos import acabamentos
from apps.dados_ia.services.memorial.pandas.inst_eletricas import eletricas
from apps.dados_ia.services.memorial.pandas.inst_mecanica import mecanica
from apps.dados_ia.services.memorial.pandas.inst_pressurizadas import pressurizada
from apps.dados_ia.services.memorial.pandas.inst_segurança import seguranca
from apps.dados_ia.services.memorial.pandas.comunicações_ambientais import ambientais
from apps.dados_ia.services.memorial.pandas.paisagismos import paisagismo
from apps.dados_ia.services.memorial.pandas.movimentosolo_manual import movimento_solo
from apps.dados_ia.services.memorial.pandas.inst_telefonia import telefonia

logger = logging.getLogger(__name__)

TEMPLATE_PATH = Path(__file__).parent / "especificacao_tecnica.docx"

MODELO_LLM = "llama3.1:8b"

_MAX_TEMPLATE_CHARS = 600
_MAX_DADOS_CHARS = 4000
_NUM_PREDICT = 1024

CAMPOS_POR_GRUPO: dict[str, list[str]] = {
    "SERVICOS PRELIMINARES": ["conteineres", "banheirosQuimicos", "andaimes",
                               "residuoComum", "residuoContaminado", "destinacaoResiduo"],
    "MOVIMENTOS DE SOLO":    ["volumes", "profundidadeEscavacao", "inclinacaoTerreno"],
    "SISTEMAS ESTRUTURAIS":  ["fundacoes", "superestrutura", "metalicas", "madeira"],
    "HIDRAULICA":            ["registros", "valvulas", "ramais", "reservatorio"],
    "ELETRICA":              ["tomadas", "iluminacao", "cabos", "disjuntores"],
    "REDE":                  ["quadrosRede", "cameras", "cabeamentos"],
    "CAMERAS":               ["quadrosRede", "cameras", "cabeamentos"],
    "SEGURANCA":             ["extintores", "hidrantes", "hastesAterramento"],
    "COBERTURA":             ["tipoEstrutura", "tipoTelhamento", "espessura", "inclinacao"],
    "DESCRICAO DOS LOCAIS":  ["nome", "area", "comprimento", "largura", "altura"],
    "AMBIENTES":             ["nome", "area", "comprimento", "largura", "altura"],
}

ABA_POR_GRUPO: dict[str, str] = {
    "SERVICOS PRELIMINARES": "Serviços Preliminares",
    "MOVIMENTOS DE SOLO": "Movimento de Solo",
    "SISTEMAS ESTRUTURAIS": "Estruturas",
    "ALVENARIAS": "Alvenarias",
    "ACABAMENTOS": "Acabamentos",
    "HIDRAULICA": "Inst. Hidraulica",
    "ELETRICA": "Inst. Elétricas",
    "REDE": "Inst. de Telefonia e Rede",
    "CAMERAS": "Inst. de Telefonia e Rede",
    "MECANICA": "Inst. Mecânicas",
    "PRESSURIZADA": "Inst. Pressurizadas",
    "SEGURANCA": "Inst. de Segurança",
    "COBERTURA": "Estruturas", 
    "DESCRICAO DOS LOCAIS": "Levantamento de Campo",
    "AMBIENTES": "Levantamento de Campo",
}


def _normalizar(s: str) -> str:
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().upper()


def _truncar_dict(dados: dict, max_chars: int) -> str:
    serializado = json.dumps(dados, ensure_ascii=False, indent=2)
    if len(serializado) > max_chars:
        return serializado[:max_chars - 3] + "..."
    return serializado


def _extrair_arvore(template_path: Path) -> list[dict]:
    print(f"[TEMPLATE] Lendo template: {template_path}")
    doc = Document(str(template_path))
    arvore: list[dict] = []
    h1_atual = ""

    for para in doc.paragraphs:
        estilo = para.style.name
        texto = para.text.strip()
        if not texto:
            continue

        if estilo == "Heading 1":
            h1_atual = texto.upper()
            continue

        if estilo in ("Heading 2", "Heading 3"):
            nivel = 2 if estilo == "Heading 2" else 3
            m = re.match(r"^([\d\.]+)\s+(.*)", texto)
            sec_id = m.group(1) if m else texto.split()[0]
            titulo = m.group(2) if m else texto
            arvore.append({
                "id": sec_id,
                "nivel": nivel,
                "titulo": titulo,
                "grupo": h1_atual,
                "texto_template": "",
            })
        elif arvore:
            sep = "\n" if arvore[-1]["texto_template"] else ""
            arvore[-1]["texto_template"] += sep + texto

    print(f"[TEMPLATE] {len(arvore)} seções encontradas no template.")
    return arvore


def _gerar_dados_estruturados(path_man: dict, path_cad: dict) -> dict:
    pm = path_man.copy()
    if isinstance(pm, list):
        pm = {"ambientes": pm}
    elif isinstance(pm, dict) and "ambientes" not in pm:
        pm = {"ambientes": [pm]}
    
    dfs_levantamento = list(levantamento_campo(pm, path_cad))
    df_servicos = list(servicos_preliminares(pm, path_cad))
    tabela_map_solo = movimento_solo(pm, path_cad)
    tabela_map_estruturas = estruturas(pm, path_cad)
    tabela_map_alvenarias = alvenarias(pm, path_cad)
    df_acabamentos = list(acabamentos(pm, path_cad))
    tabela_map_eletrica = eletricas(pm, path_cad)
    df_mecanica = list(mecanica())
    df_pressurizada = pressurizada()
    df_seguranca = list(seguranca(path_cad))
    df_ambientais = ambientais()
    df_tel = telefonia(pm, path_cad)
    df_paisagismo = paisagismo()

    mapa_abas = {
        "Levantamento de Campo": dfs_levantamento,
        "Serviços Preliminares": df_servicos,
        "Movimento de Solo": tabela_map_solo,
        "Estruturas": tabela_map_estruturas,
        "Alvenarias": tabela_map_alvenarias,
        "Acabamentos": df_acabamentos,
        "Inst. Hidraulica": [],
        "Inst. Elétricas": tabela_map_eletrica,
        "Inst. de Telefonia e Rede": df_tel,
        "Inst. Mecânicas": df_mecanica,
        "Inst. Pressurizadas": df_pressurizada,
        "Inst. de Segurança": df_seguranca,
        "Comunicações Ambientais": df_ambientais,
        "Paisagismos": df_paisagismo,
    }
    return mapa_abas

def _resumir_conteudo(conteudo: Any) -> list[dict]:
    resumo = []
    itens = []
    if isinstance(conteudo, dict):
        for titulo, valor in conteudo.items():
            if isinstance(valor, (list, tuple)):
                itens.append((titulo, valor[0]))
            else:
                itens.append((titulo, valor))
    elif isinstance(conteudo, list):
        for i, item in enumerate(conteudo):
            if isinstance(item, tuple):
                if len(item) >= 2:
                    itens.append((item[0], item[1]))
                else:
                    itens.append((None, item[0]))
            else:
                itens.append((None, item))
    else:
        itens = [(None, conteudo)]

    for titulo, df in itens:
        if not isinstance(df, pd.DataFrame):
            continue
        if df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df_flat = df.copy()
            df_flat.columns = [' '.join([str(c) for c in col if c]).strip() for col in df.columns.values]
        else:
            df_flat = df.copy()

        records = df_flat.to_dict('records')
        clean_records = []
        for rec in records:
            clean_rec = {}
            for k, v in rec.items():
                if pd.notnull(v) and str(v).strip() != "":
                    clean_rec[k] = v
            if clean_rec:
                clean_records.append(clean_rec)
        
        if clean_records:
            resumo.append({"tabela": titulo or "Dados", "itens": clean_records})
    
    return resumo


def _dados_para_grupo(grupo: str, path_man: dict, path_cad: dict, dados_estruturados: dict) -> dict:
    ambientes = path_man.get("ambientes") or []

    grupo_norm = _normalizar(grupo)
    campos_interesse: list[str] = []
    aba_interesse = ""
    for chave, campos in CAMPOS_POR_GRUPO.items():
        if chave in grupo_norm:
            campos_interesse = campos
            aba_interesse = ABA_POR_GRUPO.get(chave, "")
            break

    dados: dict[str, Any] = {}
    for campo in campos_interesse:
        valores: list = []
        for amb in ambientes:
            if not isinstance(amb, dict):
                continue
            v = amb.get(campo)
            if v is not None:
                valores.append(v)
        if valores:
            if len(valores) == 1 or all(v == valores[0] for v in valores):
                dados[campo] = valores[0]
            else:
                dados[campo] = valores

    dados["_projeto"] = {
        "nome":        path_man.get("nome") or "Não informado",
        "cliente":     path_man.get("cliente") or "Não informado",
        "localizacao": path_man.get("localizacao") or "Não informado",
        "cep":         path_man.get("cep") or "Não informado",
        "descricao":   path_man.get("descricao") or "Não informada",
        "data_inicio": path_man.get("data_inicio") or "Não informada",
        "data_fim":    path_man.get("data_fim") or "Não informada",
    }

    if aba_interesse and aba_interesse in dados_estruturados:
        dados["_tabelas_calculadas"] = _resumir_conteudo(dados_estruturados[aba_interesse])

    if path_cad:
        dados["_cad_resumo"] = path_cad.get("resumo", {})

    return dados


def _criar_llm() -> OllamaLLM:
    print(f"[LLM] Inicializando modelo: {MODELO_LLM}")
    return OllamaLLM(
        model=MODELO_LLM,
        base_url="http://127.0.0.1:11434",
        num_ctx=4096,
        num_predict=_NUM_PREDICT,
        temperature=0.2,
        top_k=20,
        top_p=0.85,
        repeat_penalty=1.1,
        keep_alive="30m",
    )


def _construir_prompt_secao(sec: dict, dados: dict) -> str:
    dados_str = _truncar_dict(dados, _MAX_DADOS_CHARS)
    texto_ref  = sec["texto_template"][:_MAX_TEMPLATE_CHARS]
    sec_id     = sec["id"]

    return f"""Você é engenheiro civil redator de especificações técnicas ABNT.

Dados reais do projeto:
{dados_str}

Reescreva o texto de referência abaixo adaptando-o aos dados do projeto.
Retorne EXCLUSIVAMENTE um objeto JSON válido, sem nenhum texto antes ou depois:
{{"{sec_id}": "texto adaptado aqui"}}

Regras:
- A chave do JSON deve ser exatamente "{sec_id}" (apenas os números).
- TODOS os campos devem ser preenchidos. Se não houver dados no JSON para alterar o texto, retorne o próprio "Texto de referência" com pequenas melhorias de linguagem, MAS NUNCA retorne "SEM_DADOS" e nunca omita a seção.
- Máximo 2 parágrafos separados por \\n
- Linguagem técnica ABNT, sem markdown
- NÃO invente normas NBR
- NÃO inclua metadados ou estatísticas brutas de arquivos CAD (ex: quantidade de layers, entidades, linhas, blocos).
- Utilize os dados do projeto estritamente para qualificar e quantificar os elementos reais da obra (ex: volumes, áreas, quantidades de materiais).
- NÃO repita o nome do cliente, endereço, localização, CEP ou datas do projeto no corpo do texto. Estas informações já constam na capa do documento. Concentre-se estritamente na adaptação técnica da seção atual.

Texto de referência da seção {sec_id} — {sec["titulo"]}:
{texto_ref}"""


def _parsear_json_llm(resposta_raw: str, sec_id: str) -> dict[str, str]:
    resposta = re.sub(r"<think>.*?</think>", "", resposta_raw, flags=re.DOTALL).strip()

    try:
        return json.loads(resposta)
    except Exception:
        pass

    m = re.search(r"\{[\s\S]*?\}", resposta)
    if m:
        try:
            return json.loads(m.group())
        except Exception:
            pass

    m = re.search(
        r'"' + re.escape(sec_id) + r'"\s*:\s*"([\s\S]*?)"(?:\s*[,}])',
        resposta,
    )
    if m:
        logger.warning("JSON malformado para seção %s; valor extraído via regex.", sec_id)
        return {sec_id: m.group(1)}

    logger.error(
        "LLM não retornou JSON válido para a seção %s. Resposta: %s",
        sec_id, resposta[:300],
    )
    return {}


def _gerar_textos_llm(arvore: list[dict], path_man: dict, path_cad: dict, dados_estruturados: dict) -> dict[str, str]:
    llm = _criar_llm()
    textos: dict[str, str] = {}

    grupos: dict[str, list[dict]] = {}
    for sec in arvore:
        grupos.setdefault(sec["grupo"], []).append(sec)

    total_secoes = len(arvore)
    contador = 0

    for grupo, secoes in grupos.items():
        print(f"\n[GRUPO] Processando grupo: '{grupo}' ({len(secoes)} seções)")
        dados = _dados_para_grupo(grupo, path_man, path_cad, dados_estruturados)

        for sec in secoes:
            contador += 1
            print(f"  [{contador}/{total_secoes}] Seção {sec['id']}: {sec['titulo']} ... ", end="", flush=True)
            prompt = _construir_prompt_secao(sec, dados)
            try:
                resposta_raw = llm.invoke(prompt)
                parcial = _parsear_json_llm(resposta_raw, sec["id"])
                textos.update(parcial)
                status = list(parcial.values())[0][:40] if parcial else "sem retorno"
                print(f"OK — '{status}...'")
            except Exception as exc:
                print(f"ERRO — {exc}")
                logger.error("Erro na LLM para seção %s: %s", sec["id"], exc)
                textos[sec["id"]] = "SEM_DADOS"

    print(f"\n[LLM] Geração concluída. {len(textos)} seções processadas.")
    return textos


def _aplicar_estilos(doc: Document) -> None:
    print("[DOC] Aplicando estilos corporativos e minimalistas...")
    
                    
    section = doc.sections[0]
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.18)
    section.right_margin = Inches(1.18)

                           
    for style_name in ['Normal', 'Heading 1', 'Heading 2', 'Heading 3', 'Header', 'Footer']:
        if style_name in doc.styles:
            doc.styles[style_name].font.name = 'Arial'

                                        
    normal = doc.styles['Normal']
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(64, 64, 64)                
    normal.paragraph_format.space_after = Pt(12)
    normal.paragraph_format.line_spacing = 1.15

                                                           
    h1 = doc.styles['Heading 1']
    h1.font.size = Pt(15)
    h1.font.bold = True
    h1.font.all_caps = True
    h1.font.color.rgb = RGBColor(0, 51, 102)               
    h1.paragraph_format.space_before = Pt(24)
    h1.paragraph_format.space_after = Pt(12)
    h1.paragraph_format.left_indent = Inches(0)

                                                   
    pPr = h1.element.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')        
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '0066CC')              
    pBdr.append(bottom)
    pPr.append(pBdr)

                                      
    h2 = doc.styles['Heading 2']
    h2.font.size = Pt(14)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0, 76, 153)                     
    h2.paragraph_format.space_before = Pt(18)
    h2.paragraph_format.space_after = Pt(6)
    h2.paragraph_format.left_indent = Inches(0.39)

    h3 = doc.styles['Heading 3']
    h3.font.size = Pt(11)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor(0, 102, 204)                   
    h3.paragraph_format.space_before = Pt(12)
    h3.paragraph_format.space_after = Pt(6)
    h3.paragraph_format.left_indent = Inches(0.79)

                                  
    header = section.header
    p_header = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    p_header.text = 'Caderno de Encargos e Especificações Técnicas'
    for r in p_header.runs:
        r.font.name = 'Arial'
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(102, 153, 204)              
    p_header.alignment = WD_ALIGN_PARAGRAPH.LEFT

                                                             
    footer = section.footer
    p_footer = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p_footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p_footer.add_run()
    run.font.name = 'Arial'
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(128, 128, 128)         
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


def _gerar_capa(doc: Document, path_man: dict) -> None:
    print("[DOC] Gerando capa...")
    nome         = path_man.get("nome") or "Não informado"
    cliente      = path_man.get("cliente") or "Não informado"
    localizacao  = path_man.get("localizacao") or "Não informado"
    cep          = path_man.get("cep") or "Não informado"
    descricao    = path_man.get("descricao") or "Não informada"
    data_inicio  = path_man.get("data_inicio") or "Não informada"
    data_fim     = path_man.get("data_fim") or "Não informada"
    data_geracao = datetime.now().strftime("%d/%m/%Y")

    titulo = doc.add_paragraph()
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = titulo.add_run("CADERNO DE ENCARGOS E ESPECIFICAÇÕES TÉCNICAS")
    run.bold = True
    run.font.size = Pt(15)
    run.font.color.rgb = RGBColor(0, 51, 102)

    doc.add_paragraph()

    for label, valor in [
        ("Projeto:", nome),
        ("Descrição:", descricao),
        ("Cliente:", cliente),
        ("Localização:", localizacao),
        ("CEP:", cep),
        ("Data de Início:", data_inicio),
        ("Data de Término:", data_fim),
        ("Data de Geração:", data_geracao),
    ]:
        p = doc.add_paragraph()
        r_label = p.add_run(label + "  ")
        r_label.bold = True
        r_label.font.size = Pt(13)
        r_label.font.color.rgb = RGBColor(0, 51, 102)
        r_valor = p.add_run(valor)
        r_valor.font.size = Pt(13)
        r_valor.font.color.rgb = RGBColor(64, 64, 64)

    doc.add_page_break()


def _gerar_corpo(doc: Document, arvore: list[dict], textos_adaptados: dict[str, str]) -> None:
    print("[DOC] Montando corpo do documento...")
    incluidas = 0
    puladas = 0
    grupo_atual = None
    for sec in arvore:
        if sec.get("grupo") and sec["grupo"] != grupo_atual:
            grupo_atual = sec["grupo"]
            doc.add_heading(grupo_atual, level=1)

        texto = textos_adaptados.get(sec["id"], "")

        if not texto or texto.strip() == "SEM_DADOS":
            texto = sec["texto_template"]
            puladas += 1

        doc.add_heading(f"{sec['id']} {sec['titulo']}", level=sec["nivel"])

        for paragrafo in [p.strip() for p in texto.split("\n") if p.strip()]:
            p_obj = doc.add_paragraph(paragrafo)
            if sec['nivel'] == 2:
                p_obj.paragraph_format.left_indent = Inches(0.39)
            elif sec['nivel'] == 3:
                p_obj.paragraph_format.left_indent = Inches(0.79)
        incluidas += 1

    print(f"[DOC] Corpo montado: {incluidas} seções incluídas, {puladas} puladas (SEM_DADOS).")


def gerar_especificacao(path_man: dict, path_cad: dict) -> io.BytesIO:
    print("\n========== INICIANDO GERAÇÃO DE ESPECIFICAÇÃO TÉCNICA ==========")

    nome_proj = path_man.get("nome")
    cliente_proj = path_man.get("cliente")
    localizacao_proj = path_man.get("localizacao")
    cep_proj = path_man.get("cep")
    descricao_proj = path_man.get("descricao")
    data_inicio_proj = path_man.get("data_inicio")
    data_fim_proj = path_man.get("data_fim")

        
    path_man["nome"] = nome_proj
    path_man["cliente"] = cliente_proj
    path_man["localizacao"] = localizacao_proj
    path_man["cep"] = cep_proj
    path_man["descricao"] = descricao_proj
    path_man["data_inicio"] = data_inicio_proj
    path_man["data_fim"] = data_fim_proj

    print(f"[DADOS] Ambientes recebidos: {len(path_man.get('ambientes', []))}")
    print(f"[DADOS] path_cad presente: {bool(path_cad)}")

    if not TEMPLATE_PATH.exists():
        print(f"[ERRO] Template não encontrado: {TEMPLATE_PATH}")
        raise FileNotFoundError(f"Template não encontrado: {TEMPLATE_PATH}")

    arvore = _extrair_arvore(TEMPLATE_PATH)

    print("\n[OLLAMA] Verificando se Ollama está pronto...")
    ensure_ollama_ready([MODELO_LLM])
    print("[OLLAMA] Ollama OK.")

    print("\n[DADOS] Gerando tabelas estruturadas via motor de memorial...")
    try:
        dados_estruturados = _gerar_dados_estruturados(path_man, path_cad)
        print("[DADOS] Estruturação geométrica/CAD concluída.")
    except Exception as e:
        logger.error(f"Erro ao gerar dados estruturados: {e}")
        print(f"[AVISO] Falha na estruturação do memorial. Usando fallback. Erro: {e}")
        dados_estruturados = {}

    textos_adaptados = _gerar_textos_llm(arvore, path_man, path_cad, dados_estruturados)

    print("\n[DOC] Criando documento Word...")
    doc = Document()
    _aplicar_estilos(doc)

    _gerar_capa(doc, path_man)
    _gerar_corpo(doc, arvore, textos_adaptados)

    print("[DOC] Serializando documento para BytesIO...")
    output = io.BytesIO()
    doc.save(output)
    output.seek(0)

    print("========== GERAÇÃO CONCLUÍDA COM SUCESSO ==========\n")
    return output