import pandas as pd
import json
import os
import re
import math

colunas_movimento_solo_escavacoes = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Tipo"),
        ("", "i [%]"),
        ("", "L [m]"),
        ("", "C [m]"),
        ("", "h [m]"),
        ("", "Lastro"),
        ("", "A [m²]"),
        ("", "V [m³]"),
    ]
)

colunas_movimento_solo = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "i [%]"),
        ("", "L [m]"),
        ("", "C [m]"),
        ("", "h [m]"),
        ("", "A [m²]"),
        ("", "V [m³]"),
    ]
)

HEADER_SPLIT = {
    "Ambiente": ("Ambiente", ""),
    "Tipo": ("Tipo", ""),
    "i [%]": ("i", "[%]"),
    "L [m]": ("L", "[m]"),
    "C [m]": ("C", "[m]"),
    "h [m]": ("h", "[m]"),
    "Lastro": ("Lastro", "[m³]"),
    "A [m²]": ("A", "[m²]"),
    "V [m³]": ("V", "[m³]"),
}


def movimento_solo(dados_manuais, dados_automaticos):
    
    df_escavacao = pd.DataFrame(columns=colunas_movimento_solo_escavacoes)
    df_aterro = pd.DataFrame(columns=colunas_movimento_solo)
    df_enrocamento = pd.DataFrame(columns=colunas_movimento_solo)
    df_contencao = pd.DataFrame(columns=colunas_movimento_solo)
    df_taludamento = pd.DataFrame(columns=colunas_movimento_solo)
    df_nivelamento = pd.DataFrame(columns=colunas_movimento_solo)

    amb_manuais = dados_manuais.get("ambientes", [])
    for item in amb_manuais:
        nome = item.get("nome", "")
        ms = item.get("volumes", {})
        if ms.get("escavacao"):
            idx = len(df_escavacao)
            df_escavacao.loc[idx, ("", "Ambiente")] = nome
            df_escavacao.loc[idx, ("", "Tipo")] = "Outros"
            df_escavacao.loc[idx, ("", "h [m]")] = item.get("profundidadeEscavacao", "")
            df_escavacao.loc[idx, ("", "V [m³]")] = ms.get("escavacao")
        if ms.get("aterro"):
            idx = len(df_aterro)
            df_aterro.loc[idx, ("", "Ambiente")] = nome
            df_aterro.loc[idx, ("", "V [m³]")] = ms.get("aterro")
        outros = [
            ("enrocamento", df_enrocamento),
            ("contencao", df_contencao),
            ("taludamento", df_taludamento),
            ("nivelamento", df_nivelamento),
        ]
        for chave, df_ref in outros:
            if ms.get(chave):
                idx = len(df_ref)
                df_ref.loc[idx, ("", "Ambiente")] = nome
                df_ref.loc[idx, ("", "V [m³]")] = ms.get(chave)

    dict_ambientes_cad = {}
    for txt in dados_automaticos.get("textos", []):
        c = txt.get("conteudo", "")
        if "m²" in c.lower():
            ma = re.search(r"(\d+[.,]\d+)\s*m²", c, re.IGNORECASE)
            if ma:
                area_val = float(ma.group(1).replace(",", "."))
                partes = c.split("\\P")
                aidx = -1
                for i, p in enumerate(partes):
                    if re.search(r"\d+[.,]\d+\s*m²", p, re.IGNORECASE):
                        aidx = i
                        break
                raw = " ".join(partes[:aidx]) if aidx > 0 else partes[0]
                n = re.sub(r"\\[^;\\]+;", "", raw).replace("{", "").replace("}", "")
                n = re.sub(r"\\[Pp]", " ", n)
                n = re.sub(r"\d+[.,]\d+\s*m²", "", n, flags=re.IGNORECASE)
                n = re.sub(r"\s+", " ", n).strip()
                if n and txt.get("posicao"):
                    if n not in dict_ambientes_cad:
                        dict_ambientes_cad[n] = {
                            "pos": txt["posicao"],
                            "area": area_val,
                        }

    def get_amb(cx, cy, threshold=400):
        if not dict_ambientes_cad:
            return "Área Externa"
        best_n = min(
            dict_ambientes_cad.keys(),
            key=lambda k: math.hypot(
                cx - dict_ambientes_cad[k]["pos"][0],
                cy - dict_ambientes_cad[k]["pos"][1],
            ),
        )
        dist = math.hypot(
            cx - dict_ambientes_cad[best_n]["pos"][0],
            cy - dict_ambientes_cad[best_n]["pos"][1],
        )
        return best_n if dist <= threshold else "Área Externa"

    fund_lines = [
        e
        for e in dados_automaticos.get("entidades", [])
        if e.get("layer") == "Estrutural - Fundações" and e.get("tipo") == "LINE"
    ]
    fund_por_amb = {}
    for e in fund_lines:
        cx = (e["dados"]["inicio"][0] + e["dados"]["fim"][0]) / 2
        cy = (e["dados"]["inicio"][1] + e["dados"]["fim"][1]) / 2
        amb = get_amb(cx, cy)
        fund_por_amb[amb] = fund_por_amb.get(amb, 0.0) + e["dados"].get(
            "comprimento", 0.0
        )
    for amb, comp in sorted(fund_por_amb.items()):
        idx = len(df_escavacao)
        df_escavacao.loc[idx, ("", "Ambiente")] = amb
        df_escavacao.loc[idx, ("", "Tipo")] = "Vala de Fundação"
        df_escavacao.loc[idx, ("", "C [m]")] = round(comp / 2, 2)
        df_escavacao.loc[idx, ("", "L [m]")] = ""
        df_escavacao.loc[idx, ("", "h [m]")] = ""

    valas_agrupadas = {}
    for txt in dados_automaticos.get("textos", []):
        c = txt.get("conteudo", "").lower()
        if any(term in c for term in ["nível do solo", "escavar", "escavação"]):
            cx, cy = txt.get("posicao", [0, 0])[:2]
            amb = get_amb(cx, cy)
            h_v = ""
            ma_h = re.search(r"(\d+[.,]\d+)m do nível", c)
            if ma_h:
                h_s = ma_h.group(1).replace(",", ".")
                try:
                    h_v = float(h_s)
                except ValueError:
                    h_v = ma_h.group(1).replace(".", ",")
            l_t = re.sub(r"\\[^;\\]+;", "", txt.get("conteudo", ""))
            l_t = re.sub(r"\\[Pp]", " ", l_t).strip()
            if amb not in valas_agrupadas:
                valas_agrupadas[amb] = {}
            ch = (l_t, h_v)
            valas_agrupadas[amb][ch] = valas_agrupadas[amb].get(ch, 0) + 1
    for amb, dict_v in sorted(valas_agrupadas.items()):
        for (t, h), q in dict_v.items():
            idx = len(df_escavacao)
            df_escavacao.loc[idx, ("", "Ambiente")] = amb
            df_escavacao.loc[idx, ("", "Tipo")] = (
                "Vala para tubulação" if "eletroduto" in t.lower() else t[:25]
            )
            df_escavacao.loc[idx, ("", "C [m]")] = f"{q}x" if q > 1 else ""
            df_escavacao.loc[idx, ("", "h [m]")] = h

    layers_geom = {
        "aterro": ["ARQ - Desnível Terreno", "ARQ - Desnível", "ARQ - Arruamentos"],
        "enrocamento": ["ARQ - Desnível Terreno", "ARQ - Cercamentos"],
        "contencao": ["ARQ - Cercamentos", "ARQ - Desnível"],
        "taludamento": ["ARQ - Desnível Terreno", "ARQ - Desnível"],
    }
    dfs_geom = {
        "aterro": df_aterro,
        "enrocamento": df_enrocamento,
        "contencao": df_contencao,
        "taludamento": df_taludamento,
    }

    for chave, layers in layers_geom.items():
        lines = [
            e
            for e in dados_automaticos.get("entidades", [])
            if e.get("layer") in layers and e.get("tipo") == "LINE"
        ]
        por_amb = {}
        for e in lines:
            cx = (e["dados"]["inicio"][0] + e["dados"]["fim"][0]) / 2
            cy = (e["dados"]["inicio"][1] + e["dados"]["fim"][1]) / 2
            amb = get_amb(cx, cy)
            por_amb[amb] = por_amb.get(amb, 0.0) + e["dados"].get("comprimento", 0.0)

        target_df = dfs_geom[chave]
        for amb, comp in sorted(por_amb.items()):
            idx = len(target_df)
            target_df.loc[idx, ("", "Ambiente")] = amb
            target_df.loc[idx, ("", "C [m]")] = round(comp, 2)
            target_df.loc[idx, ("", "L [m]")] = ""
            target_df.loc[idx, ("", "h [m]")] = ""

    def normalizar_nome(nome):
        nome = re.sub(r"\(.*?\)", "", nome)
        nome = re.sub(r"\s+", " ", nome).strip().lower()
        return nome

    ambientes_unicos = set()
    for nome, dados in sorted(dict_ambientes_cad.items()):
        nome_norm = normalizar_nome(nome)

        if nome_norm in ambientes_unicos:
            continue

        ambientes_unicos.add(nome_norm)

        idx = len(df_nivelamento)
        df_nivelamento.loc[idx, ("", "Ambiente")] = nome
        df_nivelamento.loc[idx, ("", "A [m²]")] = str(dados["area"]).replace(".", ",")
        df_nivelamento.loc[idx, ("", "C [m]")] = ""
        df_nivelamento.loc[idx, ("", "h [m]")] = ""

    ordem_secoes = [
        "2.1 Terraplanagem",
        "2.2 Escavações",
        "2.3 Aterros e Reaterros",
        "2.4 Enrocamentos",
        "2.5 Contenções",
        "2.6 Taludamentos",
        "2.7 Nivelamentos e Compactações",
    ]

    tabela_map = {
        "2.2 Escavações": df_escavacao,
        "2.3 Aterros e Reaterros": df_aterro,
        "2.4 Enrocamentos": df_enrocamento,
        "2.5 Contenções": df_contencao,
        "2.6 Taludamentos": df_taludamento,
        "2.7 Nivelamentos e Compactações": df_nivelamento,
    }

    return tabela_map
