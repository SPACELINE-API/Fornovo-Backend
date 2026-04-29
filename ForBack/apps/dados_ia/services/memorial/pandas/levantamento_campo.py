import pandas as pd
import json
import os
import re
import math
from collections import Counter

colunas_levantamento_campo = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Dimensões", "C [m]"),
        ("Dimensões", "L [m]"),
        ("Dimensões", "h [m]"),
        ("Dimensões", "e [m]"),
        ("Dimensões", "A [m²]"),
        ("Vãos", "Tipo"),
        ("Vãos", "C [m]"),
        ("Vãos", "h [m]"),
        ("Vãos", "e [m]"),
        ("Vãos", "A [m²]"),
        ("Alvenarias Adicionais", "Tipo"),
        ("Alvenarias Adicionais", "C [m]"),
        ("Alvenarias Adicionais", "h [m]"),
        ("Alvenarias Adicionais", "e [m]"),
        ("Alvenarias Adicionais", "V [m³]"),
    ]
)

colunas_levantamento_campo2 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Pilar", "C [m]"),
        ("Pilar", "L [m]"),
        ("Pilar", "h [m]"),
        ("Pilar", "A [m²]"),
        ("Viga", "C [m]"),
        ("Viga", "h [m]"),
        ("Viga", "e [m]"),
        ("Viga", "A [m²]"),
        ("Laje", "Tipo"),
        ("Laje", "C [m]"),
        ("Laje", "L [m]"),
        ("Laje", "e [m]"),
        ("Laje", "A [m²]"),
    ]
)

colunas_levantamento_campo3 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Quadros [Un]"),
        ("", "Conduletes [Un]"),
        ("", "Tomadas [Un]"),
        ("", "Interruptor [Un]"),
        ("", "Luminárias [Un]"),
        ("", "Dutos [m]"),
        ("", "Cabos [m]"),
        ("Acessórios", "Tipo"),
        ("Acessórios", "[Un]"),
        ("Equipamentos", "Tipo"),
        ("Equipamentos", "[Un]"),
    ]
)

colunas_levantamento_campo4 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Água Fria/Quente/Reúso", "Cavalete [Un]"),
        ("Água Fria/Quente/Reúso", "Reservatório Tipo"),
        ("Água Fria/Quente/Reúso", "Reservatório [Un]"),
        ("Água Fria/Quente/Reúso", "Reservatório [L]"),
        ("Água Fria/Quente/Reúso", "Registros [Un]"),
        ("Água Fria/Quente/Reúso", "Válvulas [Un]"),
        ("Água Fria/Quente/Reúso", "Torneiras [Un]"),
        ("Água Fria/Quente/Reúso", "Dutos [m]"),
        ("Água Pluvial", "Calhas Tipo"),
        ("Água Pluvial", "Calhas [m]"),
        ("Água Pluvial", "Dutos [m]"),
        ("Água Pluvial", "Caixas [Un]"),
        ("Esgoto", "Drenos [Un]"),
        ("Esgoto", "Dutos [m]"),
        ("Esgoto", "Caixas [Un]"),
    ]
)

colunas_levantamento_campo5 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Rede", "Quadros [Un]"),
        ("Rede", "Condulete [Un]"),
        ("Rede", "Tomadas [Un]"),
        ("Rede", "Dutos Tipo"),
        ("Rede", "Dutos [m]"),
        ("Rede", "Cabos [m]"),
        ("SPDA", "Captação [Un]"),
        ("SPDA", "Condulete [m]"),
        ("SPDA", "Aterra/o [Un]"),
        ("SPDA", "Dutos Tipo"),
        ("SPDA", "Dutos [m]"),
        ("SPDA", "Cabos [m]"),
    ]
)

colunas_levantamento_campo6 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Contra incêndio", "Reservatório Tipo"),
        ("Contra incêndio", "Reservatório [Un]"),
        ("Contra incêndio", "Registros [Un]"),
        ("Contra incêndio", "Válvulas [Un]"),
        ("Contra incêndio", "Dutos Tipo"),
        ("Contra incêndio", "Dutos [m]"),
        ("Contra incêndio", "Hidrantes [Un]"),
        ("Instalações Pressurizadas", "Reservatório Tipo"),
        ("Instalações Pressurizadas", "Reservatório [Un]"),
        ("Instalações Pressurizadas", "Registros [Un]"),
        ("Instalações Pressurizadas", "Válvulas [Un]"),
        ("Instalações Pressurizadas", "Dutos Tipo"),
        ("Instalações Pressurizadas", "Dutos [m]"),
        ("Instalações Pressurizadas", "Regulador [Un]"),
    ]
)

colunas_levantamento_campo7 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Telhados", "C [m]"),
        ("Telhados", "L [m]"),
        ("Telhados", "H [m]"),
        ("Estrutura", "Tipo"),
        ("Estrutura", "C [m]"),
        ("Estrutura", "L [m]"),
        ("Estrutura", "e [m]"),
        ("Estrutura", "a [m²]"),
        ("Telhamento", "Tipo"),
        ("Telhamento", "L [m]"),
        ("Telhamento", "C [m]"),
        ("Telhamento", "e [m]"),
    ]
)


def levantamento_campo(json_path, dxf_path):
    df = pd.DataFrame(columns=colunas_levantamento_campo)
    df2 = pd.DataFrame(columns=colunas_levantamento_campo2)
    df3 = pd.DataFrame(columns=colunas_levantamento_campo3)
    df4 = pd.DataFrame(columns=colunas_levantamento_campo4)
    df5 = pd.DataFrame(columns=colunas_levantamento_campo5)
    df6 = pd.DataFrame(columns=colunas_levantamento_campo6)
    df7 = pd.DataFrame(columns=colunas_levantamento_campo7)

    with open(json_path, "r", encoding="utf-8") as m:
        dados_manuais = json.load(m)

    with open(dxf_path, "r", encoding="utf-8") as a:
        dados_automaticos = json.load(a)

    idx_linha = 0

    for item in dados_manuais.get("ambientes", []):
        c = item.get("comprimento")
        l = item.get("largura")
        df.loc[idx_linha, ("", "Ambiente")] = item.get("nome", "")
        df.loc[idx_linha, ("Dimensões", "C [m]")] = c if c is not None else ""
        df.loc[idx_linha, ("Dimensões", "L [m]")] = l if l is not None else ""
        df.loc[idx_linha, ("Dimensões", "h [m]")] = item.get("altura", "")
        df.loc[idx_linha, ("Dimensões", "e [m]")] = item.get("espessura", "")
        df.loc[idx_linha, ("Dimensões", "A [m²]")] = (
            item.get("area")
            if "area" in item
            else (c * l if c is not None and l is not None else "")
        )
        idx_linha += 1

    idx_linha2 = 0
    for item2 in dados_manuais.get("ambientes", []):
        df2.loc[idx_linha2, ("", "Ambiente")] = item2.get("nome", "")

        super_list = item2.get("superestrutura", [])
        pilar = next((s for s in super_list if s.get("tipo") == "pilar"), super_list[0] if super_list else {})
        viga  = next((s for s in super_list if s.get("tipo") == "viga"), {})

        df2.loc[idx_linha2, ("Pilar", "C [m]")] = pilar.get("largura", "")
        df2.loc[idx_linha2, ("Pilar", "L [m]")] = pilar.get("largura", "")
        df2.loc[idx_linha2, ("Pilar", "h [m]")] = pilar.get("altura", "")
        df2.loc[idx_linha2, ("Pilar", "A [m²]")] = (
            round(pilar["largura"] ** 2, 4) if pilar.get("largura") else ""
        )

        df2.loc[idx_linha2, ("Viga", "C [m]")] = viga.get("largura", "")
        df2.loc[idx_linha2, ("Viga", "h [m]")] = viga.get("altura", "")
        df2.loc[idx_linha2, ("Viga", "e [m]")] = viga.get("largura", "")
        df2.loc[idx_linha2, ("Viga", "A [m²]")] = (
            round(viga["largura"] * viga["altura"], 4)
            if viga.get("largura") and viga.get("altura") else ""
        )

        df2.loc[idx_linha2, ("Laje", "Tipo")] = ""
        df2.loc[idx_linha2, ("Laje", "C [m]")] = item2.get("comprimento", "")
        df2.loc[idx_linha2, ("Laje", "L [m]")] = item2.get("largura", "")
        df2.loc[idx_linha2, ("Laje", "e [m]")] = item2.get("espessura", "")
        df2.loc[idx_linha2, ("Laje", "A [m²]")] = item2.get("area", "")

        idx_linha2 += 1

    idx_linha3 = 0
    for item3 in dados_manuais.get("ambientes", []):

        df3.loc[idx_linha3, ("", "Ambiente")] = item3.get("nome", "")
        df3.loc[idx_linha3, ("", "Quadros [Un]")] = item3.get("quadrosRede", "")
        df3.loc[idx_linha3, ("", "Conduletes [Un]")] = item3.get("caixasInspecao", "")
        df3.loc[idx_linha3, ("", "Tomadas [Un]")] = item3.get("tomadas", "")
        df3.loc[idx_linha3, ("", "Interruptor [Un]")] = item3.get("interruptores", "")
        df3.loc[idx_linha3, ("", "Luminárias [Un]")] = item3.get("iluminacao", "")

        df3.loc[idx_linha3, ("", "Dutos [m]")] = (
            sum(r.get("comprimento", 0) for r in item3.get("ramais", []))
            if item3.get("ramais")
            else ""
        )

        df3.loc[idx_linha3, ("", "Cabos [m]")] = (
            sum(c.get("comprimento", 0) for c in item3.get("cabeamentos", []))
            if item3.get("cabeamentos")
            else ""
        )

        df3.loc[idx_linha3, ("Acessórios", "Tipo")] = item3.get("tipoTomada", "")
        df3.loc[idx_linha3, ("Acessórios", "[Un]")] = item3.get("tomadas", "")

        df3.loc[idx_linha3, ("Equipamentos", "Tipo")] = item3.get("tipoLuminaria", "")
        df3.loc[idx_linha3, ("Equipamentos", "[Un]")] = item3.get("iluminacao", "")

        idx_linha3 += 1

        idx_linha4 = 0

    for item4 in dados_manuais.get("ambientes", []):

        df4.loc[idx_linha4, ("", "Ambiente")] = item4.get("nome", "")

        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Cavalete [Un]")] = ""

        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Reservatório [Un]")] = (
            1 if item4.get("reservatorio") else 0
        )

        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Reservatório Tipo")] = (
            item4.get("reservatorio", {}).get("tipo", "")
            if item4.get("reservatorio")
            else ""
        )

        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Reservatório [L]")] = (
            item4.get("reservatorio", {}).get("capacidade", "")
            if item4.get("reservatorio")
            else ""
        )

        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Registros [Un]")] = item4.get(
            "registros", 0
        )
        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Válvulas [Un]")] = item4.get(
            "valvulas", 0
        )

        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Torneiras [Un]")] = item4.get(
            "tomadas", 0
        )

        df4.loc[idx_linha4, ("Água Fria/Quente/Reúso", "Dutos [m]")] = (
            sum(d.get("comprimento", 0) for d in item4.get("dutos", []))
            if item4.get("dutos")
            else 0
        )

        df4.loc[idx_linha4, ("Água Pluvial", "Calhas Tipo")] = ""

        df4.loc[idx_linha4, ("Água Pluvial", "Calhas [m]")] = 0

        df4.loc[idx_linha4, ("Água Pluvial", "Dutos [m]")] = (
            sum(d.get("comprimento", 0) for d in item4.get("dutos", []))
            if item4.get("dutos")
            else 0
        )

        df4.loc[idx_linha4, ("Água Pluvial", "Caixas [Un]")] = item4.get(
            "caixasInspecao", 0
        )

        df4.loc[idx_linha4, ("Esgoto", "Drenos [Un]")] = len(item4.get("ramais", []))

        df4.loc[idx_linha4, ("Esgoto", "Dutos [m]")] = (
            sum(r.get("comprimento", 0) for r in item4.get("ramais", []))
            if item4.get("ramais")
            else 0
        )

        df4.loc[idx_linha4, ("Esgoto", "Caixas [Un]")] = item4.get("caixasInspecao", 0)

        idx_linha4 += 1

    idx_linha5 = 0

    for item5 in dados_manuais.get("ambientes", []):
        df5.loc[idx_linha5, ("", "Ambiente")] = item5.get("nome", "")

        df5.loc[idx_linha5, ("Rede", "Quadros [Un]")] = item5.get("quadrosRede", "")
        df5.loc[idx_linha5, ("Rede", "Condulete [Un]")] = item5.get(
            "caixasInspecao", ""
        )
        df5.loc[idx_linha5, ("Rede", "Tomadas [Un]")] = item5.get("tomadas", "")
        df5.loc[idx_linha5, ("Rede", "Dutos Tipo")] = (
            item5.get("dutos", [{}])[0].get("diametro", "")
            if item5.get("dutos")
            else ""
        )
        df5.loc[idx_linha5, ("Rede", "Dutos [m]")] = (
            sum(d.get("comprimento", 0) for d in item5.get("dutos", []))
            if item5.get("dutos")
            else ""
        )
        df5.loc[idx_linha5, ("Rede", "Cabos [m]")] = (
            sum(c.get("comprimento", 0) for c in item5.get("cabeamentos", []))
            if item5.get("cabeamentos")
            else ""
        )

        df5.loc[idx_linha5, ("SPDA", "Captação [Un]")] = item5.get(
            "terminaisAereos", ""
        )
        df5.loc[idx_linha5, ("SPDA", "Condulete [m]")] = item5.get("caixasInspecao", "")
        df5.loc[idx_linha5, ("SPDA", "Aterra/o [Un]")] = item5.get(
            "hastesAterramento", ""
        )
        df5.loc[idx_linha5, ("SPDA", "Dutos Tipo")] = (
            item5.get("dutos", [{}])[0].get("diametro", "")
            if item5.get("dutos")
            else ""
        )
        df5.loc[idx_linha5, ("SPDA", "Dutos [m]")] = (
            sum(d.get("comprimento", 0) for d in item5.get("dutos", []))
            if item5.get("dutos")
            else ""
        )
        df5.loc[idx_linha5, ("SPDA", "Cabos [m]")] = (
            sum(c.get("comprimento", 0) for c in item5.get("cabeamentos", []))
            if item5.get("cabeamentos")
            else ""
        )

        idx_linha5 += 1

    idx_linha6 = 0

    for item6 in dados_manuais.get("ambientes", []):
        df6.loc[idx_linha6, ("", "Ambiente")] = item6.get("nome", "")

        hidrantes = item6.get("hidrantes", [])
        df6.loc[idx_linha6, ("Contra incêndio", "Reservatório Tipo")] = (
            item6.get("reservatorio", {}).get("tipo", "")
            if item6.get("reservatorio")
            else ""
        )
        df6.loc[idx_linha6, ("Contra incêndio", "Reservatório [Un]")] = (
            1 if item6.get("reservatorio") else 0
        )
        df6.loc[idx_linha6, ("Contra incêndio", "Registros [Un]")] = item6.get(
            "registros", ""
        )
        df6.loc[idx_linha6, ("Contra incêndio", "Válvulas [Un]")] = item6.get(
            "valvulas", ""
        )
        df6.loc[idx_linha6, ("Contra incêndio", "Dutos Tipo")] = (
            item6.get("dutos", [{}])[0].get("diametro", "")
            if item6.get("dutos")
            else ""
        )
        df6.loc[idx_linha6, ("Contra incêndio", "Dutos [m]")] = (
            sum(d.get("comprimento", 0) for d in item6.get("dutos", []))
            if item6.get("dutos")
            else ""
        )
        df6.loc[idx_linha6, ("Contra incêndio", "Hidrantes [Un]")] = len(hidrantes)

        df6.loc[idx_linha6, ("Instalações Pressurizadas", "Reservatório Tipo")] = (
            item6.get("reservatorio", {}).get("tipo", "")
            if item6.get("reservatorio")
            else ""
        )
        df6.loc[idx_linha6, ("Instalações Pressurizadas", "Reservatório [Un]")] = (
            1 if item6.get("reservatorio") else 0
        )
        df6.loc[idx_linha6, ("Instalações Pressurizadas", "Registros [Un]")] = (
            item6.get("registros", "")
        )
        df6.loc[idx_linha6, ("Instalações Pressurizadas", "Válvulas [Un]")] = item6.get(
            "valvulas", ""
        )
        df6.loc[idx_linha6, ("Instalações Pressurizadas", "Dutos Tipo")] = (
            item6.get("ramais", [{}])[0].get("diametro", "")
            if item6.get("ramais")
            else ""
        )
        df6.loc[idx_linha6, ("Instalações Pressurizadas", "Dutos [m]")] = (
            sum(r.get("comprimento", 0) for r in item6.get("ramais", []))
            if item6.get("ramais")
            else ""
        )
        df6.loc[idx_linha6, ("Instalações Pressurizadas", "Regulador [Un]")] = ""

        idx_linha6 += 1

    textos = dados_automaticos.get("textos", [])
    cotas = [d.get("valor_medido") for d in dados_automaticos.get("dimensions", [])]

    ambientes_processados = {}
    ambientes_cad = []

    for txt in textos:
        conteudo = txt.get("conteudo", "")
        if "m²" in conteudo.lower():
            match_area = re.search(r"(\d+[.,]\d+)\s*m²", conteudo, re.IGNORECASE)
            match_perim = re.search(r"P\s*=\s*(\d+[.,]\d+)m", conteudo, re.IGNORECASE)
            match_pd = re.search(r"PD\s*=\s*(\d+[.,]\d+)", conteudo, re.IGNORECASE)

            if match_area:
                area = float(match_area.group(1).replace(",", "."))
                perim = (
                    float(match_perim.group(1).replace(",", ".")) if match_perim else 0
                )
                pdi = float(match_pd.group(1).replace(",", ".")) if match_pd else ""

                parts = conteudo.split("\\P")

                area_idx = -1
                for i_p, p_str in enumerate(parts):
                    if re.search(r"\d+[.,]\d+\s*m²", p_str, re.IGNORECASE):
                        area_idx = i_p
                        break

                if area_idx > 0:
                    raw_name = " ".join(parts[:area_idx])
                else:
                    raw_name = parts[0]

                nome = re.sub(r"\\[^;\\]+;", "", raw_name)
                nome = nome.replace("{", "").replace("}", "")
                nome = re.sub(r"\\[Pp]", " ", nome)
                nome = re.sub(r"\d+[.,]\d+\s*m²", "", nome, flags=re.IGNORECASE)
                nome = re.sub(r"\s+", " ", nome).strip()

                if nome and txt.get("posicao"):
                    ambientes_cad.append({"nome": nome, "pos": txt.get("posicao")})

                if not nome:
                    continue

                chave_unica = f"{nome}_{area}"
                if chave_unica in ambientes_processados:
                    continue
                ambientes_processados[chave_unica] = True

                c_auto = ""
                l_auto = ""

                if perim > 0:
                    s = perim / 2
                    discriminante = s**2 - 4 * area
                    if discriminante >= 0:
                        c_calc = (s + math.sqrt(discriminante)) / 2
                        l_calc = (s - math.sqrt(discriminante)) / 2

                        for valor in cotas:
                            if math.isclose(valor, c_calc, rel_tol=0.05):
                                c_auto = valor
                            if math.isclose(valor, l_calc, rel_tol=0.05):
                                l_auto = valor

                        if c_auto == "":
                            c_auto = c_calc
                        if l_auto == "":
                            l_auto = l_calc

                df.loc[idx_linha, ("", "Ambiente")] = nome
                df.loc[idx_linha, ("Dimensões", "C [m]")] = (
                    c_auto if c_auto != "" else ""
                )
                df.loc[idx_linha, ("Dimensões", "L [m]")] = (
                    l_auto if l_auto != "" else ""
                )
                df.loc[idx_linha, ("Dimensões", "h [m]")] = pdi
                df.loc[idx_linha, ("Dimensões", "e [m]")] = ""
                df.loc[idx_linha, ("Dimensões", "A [m²]")] = area
                idx_linha += 1

    pilares_entities = [
        e
        for e in dados_automaticos.get("entidades", [])
        if e.get("layer") == "Estrutural - Pilares"
    ]

    def get_closest_ambiente(cx, cy):
        if not ambientes_cad:
            return ""
        min_dist = float("inf")
        closest = ""
        for amb in ambientes_cad:
            pos = amb["pos"]
            dist = math.hypot(cx - pos[0], cy - pos[1])
            if dist < min_dist:
                min_dist = dist
                closest = amb["nome"]
        return closest if min_dist < 15 else "Externa/Não Identificado"

    def round_pt(pt):
        return (round(pt[0], 2), round(pt[1], 2))

    linhas = [e for e in pilares_entities if e.get("tipo") == "LINE"]
    adj = {}
    edges = []
    for i, line in enumerate(linhas):
        if "dados" in line and "inicio" in line["dados"] and "fim" in line["dados"]:
            p1 = round_pt(line["dados"]["inicio"])
            p2 = round_pt(line["dados"]["fim"])
            edges.append((i, p1, p2))
            adj.setdefault(p1, []).append(i)
            adj.setdefault(p2, []).append(i)

    visited = set()
    components = []
    for i in range(len(linhas)):
        if i in visited:
            continue
        comp = []
        q = [i]
        visited.add(i)
        while q:
            curr = q.pop(0)
            comp.append(curr)
            if curr < len(edges):
                p1, p2 = edges[curr][1], edges[curr][2]
                for neighbor in adj.get(p1, []) + adj.get(p2, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
        components.append(comp)

    pilares_extraidos = []
    for comp in components:
        if len(comp) < 2:
            continue
        comprimentos = [
            linhas[idx]["dados"]["comprimento"]
            for idx in comp
            if "comprimento" in linhas[idx]["dados"]
        ]
        comprimentos = sorted([round(l, 3) for l in comprimentos])
        pts_x = []
        pts_y = []
        for idx in comp:
            pts_x.extend(
                [linhas[idx]["dados"]["inicio"][0], linhas[idx]["dados"]["fim"][0]]
            )
            pts_y.extend(
                [linhas[idx]["dados"]["inicio"][1], linhas[idx]["dados"]["fim"][1]]
            )
        if not pts_x:
            continue
        cx = sum(pts_x) / len(pts_x)
        cy = sum(pts_y) / len(pts_y)
        c = max(comprimentos) if comprimentos else 0
        l = min(comprimentos) if comprimentos else 0
        area = round(c * l, 4)
        amb = get_closest_ambiente(cx, cy)
        pilares_extraidos.append({"ambiente": amb, "c": c, "l": l, "area": area})

    circulos = [e for e in pilares_entities if e.get("tipo") == "CIRCLE"]
    for circ in circulos:
        raio = circ["dados"]["raio"]
        cx, cy = circ["dados"]["centro"][:2]
        c = l = round(2 * raio, 3)
        area = round(math.pi * raio**2, 4)
        amb = get_closest_ambiente(cx, cy)
        pilares_extraidos.append({"ambiente": amb, "c": c, "l": l, "area": area})

    pilares_extraidos.sort(key=lambda x: (x["ambiente"], x["c"], x["l"]))

    pilares_processados = {}
    pilares_unicos = []

    for pilar in pilares_extraidos:
        chave_unica = f"{pilar['ambiente']}_{pilar['c']}_{pilar['l']}"
        if chave_unica in pilares_processados:
            continue
        pilares_processados[chave_unica] = True
        pilares_unicos.append(pilar)

    pilares_por_ambiente = {}

    for p in pilares_unicos:
        amb = p["ambiente"]

        if amb not in pilares_por_ambiente:
            pilares_por_ambiente[amb] = {"c": [], "l": [], "area": []}

        pilares_por_ambiente[amb]["c"].append(p["c"])
        pilares_por_ambiente[amb]["l"].append(p["l"])
        pilares_por_ambiente[amb]["area"].append(p["area"])

    vigas_entities = [
        e
        for e in dados_automaticos.get("entidades", [])
        if e.get("layer") == "Estrutural - Vigas"
    ]

    linhas_vigas = [e for e in vigas_entities if e.get("tipo") == "LINE"]

    TOL_ANG = 2.0
    TOL_DIST = 0.5
    TOL_OVL = 0.05

    def _angulo_ln(v):
        dx = v["dados"]["fim"][0] - v["dados"]["inicio"][0]
        dy = v["dados"]["fim"][1] - v["dados"]["inicio"][1]
        return math.degrees(math.atan2(dy, dx)) % 180

    def _medio_ln(v):
        sx, sy = v["dados"]["inicio"][:2]
        fx, fy = v["dados"]["fim"][:2]
        return ((sx + fx) / 2, (sy + fy) / 2)

    def _dist_pt_reta(px, py, v):
        sx, sy = v["dados"]["inicio"][:2]
        fx, fy = v["dados"]["fim"][:2]
        dx, dy = fx - sx, fy - sy
        denom = dx * dx + dy * dy
        if denom < 1e-12:
            return math.dist([px, py], [sx, sy])
        t = ((px - sx) * dx + (py - sy) * dy) / denom
        return math.dist([px, py], [sx + t * dx, sy + t * dy])

    def _proj_intervalo(v, ux, uy):
        sx, sy = v["dados"]["inicio"][:2]
        fx, fy = v["dados"]["fim"][:2]
        t0, t1 = sx * ux + sy * uy, fx * ux + fy * uy
        return (min(t0, t1), max(t0, t1))

    def _sobrepoem(a, b, tol):
        return a[1] >= b[0] + tol and b[1] >= a[0] + tol

    meta_vigas = [
        {
            "idx": i,
            "linha": v,
            "angulo": _angulo_ln(v),
            "medio": _medio_ln(v),
            "comp": v["dados"].get("comprimento", 0.0),
        }
        for i, v in enumerate(linhas_vigas)
        if "dados" in v and "inicio" in v["dados"] and "fim" in v["dados"]
    ]
    meta_vigas.sort(key=lambda m: -m["comp"])

    used_v = set()
    grupos_viga = []

    for semente in meta_vigas:
        if semente["idx"] in used_v:
            continue
        grp = [semente]
        used_v.add(semente["idx"])
        ang_s = semente["angulo"]
        rad_s = math.radians(ang_s)
        ux, uy = math.cos(rad_s), math.sin(rad_s)
        proj_s = _proj_intervalo(semente["linha"], ux, uy)

        for cand in meta_vigas:
            if cand["idx"] in used_v:
                continue
            da = abs(cand["angulo"] - ang_s)
            da = min(da, 180 - da)
            if da > TOL_ANG:
                continue
            px, py = cand["medio"]
            if _dist_pt_reta(px, py, semente["linha"]) > TOL_DIST:
                continue
            proj_c = _proj_intervalo(cand["linha"], ux, uy)
            if not _sobrepoem(proj_s, proj_c, TOL_OVL):
                continue
            grp.append(cand)
            used_v.add(cand["idx"])

        grupos_viga.append(grp)

    def _get_ambiente_viga(cx, cy):
        """Retorna o ambiente mais próximo sem corte fixo de distância."""
        if not ambientes_cad:
            return "Externa/Não Identificado"
        return min(
            ambientes_cad, key=lambda a: math.hypot(cx - a["pos"][0], cy - a["pos"][1])
        )["nome"]

    vigas_extraidas = []

    for grp in grupos_viga:
        pts_x, pts_y = [], []
        for m in grp:
            sx, sy = m["linha"]["dados"]["inicio"][:2]
            fx, fy = m["linha"]["dados"]["fim"][:2]
            pts_x.extend([sx, fx])
            pts_y.extend([sy, fy])

        cx = sum(pts_x) / len(pts_x)
        cy = sum(pts_y) / len(pts_y)
        amb = _get_ambiente_viga(cx, cy)

        linha_ref = max(grp, key=lambda m: m["comp"])
        C = round(linha_ref["comp"], 3)

        longas = sorted(grp, key=lambda m: -m["comp"])
        if len(longas) >= 2:
            px2, py2 = longas[1]["medio"]
            e = round(_dist_pt_reta(px2, py2, longas[0]["linha"]), 3)
        else:
            e = ""

        if C < 0.05:
            continue

        vigas_extraidas.append({"ambiente": amb, "C": C, "e": e})

    vigas_por_ambiente = {}

    for v in vigas_extraidas:
        amb = v["ambiente"]
        if amb not in vigas_por_ambiente:
            vigas_por_ambiente[amb] = {"C": [], "e": []}
        if v["C"]:
            vigas_por_ambiente[amb]["C"].append(v["C"])
        if v["e"] != "":
            vigas_por_ambiente[amb]["e"].append(v["e"])

    lajes_entities = [
        e
        for e in dados_automaticos.get("entidades", [])
        if e.get("layer") == "Estrutural - Lajes"
    ]

    linhas_lajes = [
        e
        for e in lajes_entities
        if e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
    ]

    TOL_DIST_LAJE = 0.15
    TOL_ASSOC_LAJE = 8.0
    COMP_MIN_LAJE = 0.5

    meta_lajes = [
        {
            "idx": i,
            "linha": v,
            "angulo": _angulo_ln(v),
            "medio": _medio_ln(v),
            "comp": v["dados"].get("comprimento", 0.0),
        }
        for i, v in enumerate(linhas_lajes)
    ]
    meta_lajes.sort(key=lambda m: -m["comp"])

    used_l = set()
    pares_laje = []

    for semente in meta_lajes:
        if semente["idx"] in used_l:
            continue
        if semente["comp"] < COMP_MIN_LAJE:
            used_l.add(semente["idx"])
            continue

        grp = [semente]
        used_l.add(semente["idx"])
        ang_s = semente["angulo"]
        rad_s = math.radians(ang_s)
        ux, uy = math.cos(rad_s), math.sin(rad_s)
        proj_s = _proj_intervalo(semente["linha"], ux, uy)

        for cand in meta_lajes:
            if cand["idx"] in used_l:
                continue
            if cand["comp"] < COMP_MIN_LAJE:
                continue
            da = abs(cand["angulo"] - ang_s)
            da = min(da, 180 - da)
            if da > TOL_ANG:
                continue
            px, py = cand["medio"]
            if _dist_pt_reta(px, py, semente["linha"]) > TOL_DIST_LAJE:
                continue
            proj_c = _proj_intervalo(cand["linha"], ux, uy)
            if not _sobrepoem(proj_s, proj_c, TOL_OVL):
                continue
            grp.append(cand)
            used_l.add(cand["idx"])

        comp_par = round(max(m["comp"] for m in grp), 3)
        pts_x = []
        pts_y = []
        for m in grp:
            sx, sy = m["linha"]["dados"]["inicio"][:2]
            fx, fy = m["linha"]["dados"]["fim"][:2]
            pts_x.extend([sx, fx])
            pts_y.extend([sy, fy])
        cx_par = sum(pts_x) / len(pts_x)
        cy_par = sum(pts_y) / len(pts_y)
        pares_laje.append({"comp": comp_par, "cx": cx_par, "cy": cy_par})

    used_par = set()
    lajes_extraidas = []

    pares_laje.sort(key=lambda p: -p["comp"])

    comps_unicos = sorted(set(p["comp"] for p in pares_laje), reverse=True)

    if len(comps_unicos) >= 2:
        pares_C = [p for p in pares_laje if p["comp"] == comps_unicos[0]]
        pares_L = [p for p in pares_laje if p["comp"] == comps_unicos[1]]

        used_L = set()
        for i, par_a in enumerate(pares_C):
            melhor_j, melhor_dist = None, float("inf")
            for j, par_b in enumerate(pares_L):
                if j in used_L:
                    continue
                dist = math.hypot(par_a["cx"] - par_b["cx"], par_a["cy"] - par_b["cy"])
                if dist < melhor_dist and dist <= TOL_ASSOC_LAJE:
                    melhor_dist = dist
                    melhor_j = j
            if melhor_j is not None:
                used_L.add(melhor_j)
                par_b = pares_L[melhor_j]
                C = round(max(par_a["comp"], par_b["comp"]), 3)
                L = round(min(par_a["comp"], par_b["comp"]), 3)
                A = round(C * L, 4)
                cx = (par_a["cx"] + par_b["cx"]) / 2
                cy = (par_a["cy"] + par_b["cy"]) / 2
            else:
                C, L, A = par_a["comp"], "", ""
                cx, cy = par_a["cx"], par_a["cy"]
            amb = _get_ambiente_viga(cx, cy)
            lajes_extraidas.append({"ambiente": amb, "C": C, "L": L, "A": A})

        for j, par_b in enumerate(pares_L):
            if j not in used_L:
                amb = _get_ambiente_viga(par_b["cx"], par_b["cy"])
                lajes_extraidas.append(
                    {"ambiente": amb, "C": par_b["comp"], "L": "", "A": ""}
                )
    else:
        for par in pares_laje:
            amb = _get_ambiente_viga(par["cx"], par["cy"])
            lajes_extraidas.append(
                {"ambiente": amb, "C": par["comp"], "L": "", "A": ""}
            )

    lajes_por_ambiente = {}

    for lj in lajes_extraidas:
        amb = lj["ambiente"]
        if amb not in lajes_por_ambiente:
            lajes_por_ambiente[amb] = {"C": [], "L": [], "A": []}
        if lj["C"]:
            lajes_por_ambiente[amb]["C"].append(lj["C"])
        if lj["L"] != "":
            lajes_por_ambiente[amb]["L"].append(lj["L"])
        if lj["A"] != "":
            lajes_por_ambiente[amb]["A"].append(lj["A"])

    todos_ambientes = (
        set(pilares_por_ambiente.keys())
        | set(vigas_por_ambiente.keys())
        | set(lajes_por_ambiente.keys())
    )

    for amb in todos_ambientes:

        df2.loc[idx_linha2, ("", "Ambiente")] = amb

        # PILAR
        if amb in pilares_por_ambiente:
            valores = pilares_por_ambiente[amb]
            df2.loc[idx_linha2, ("Pilar", "C [m]")] = (
                max(valores["c"]) if valores["c"] else ""
            )
            df2.loc[idx_linha2, ("Pilar", "L [m]")] = (
                max(valores["l"]) if valores["l"] else ""
            )
            df2.loc[idx_linha2, ("Pilar", "A [m²]")] = (
                sum(valores["area"]) if valores["area"] else ""
            )

        # VIGA
        if amb in vigas_por_ambiente:
            vals = vigas_por_ambiente[amb]

            C = sum(vals["C"]) if vals["C"] else ""
            e = (sum(vals["e"]) / len(vals["e"])) if vals["e"] else ""

            A = (C * e) if C and e else ""

            df2.loc[idx_linha2, ("Viga", "C [m]")] = C
            df2.loc[idx_linha2, ("Viga", "e [m]")] = e
            df2.loc[idx_linha2, ("Viga", "A [m²]")] = A

        # LAJE
        if amb in lajes_por_ambiente:
            vals = lajes_por_ambiente[amb]

            C_lj = max(vals["C"]) if vals["C"] else ""
            L_lj = max(vals["L"]) if vals["L"] else ""
            A_lj = sum(vals["A"]) if vals["A"] else ""

            df2.loc[idx_linha2, ("Laje", "C [m]")] = C_lj
            df2.loc[idx_linha2, ("Laje", "L [m]")] = L_lj
            df2.loc[idx_linha2, ("Laje", "e [m]")] = ""
            df2.loc[idx_linha2, ("Laje", "A [m²]")] = A_lj

        idx_linha2 += 1

    entidades_auto = dados_automaticos.get("entidades", [])
    textos_auto = dados_automaticos.get("textos", [])

    _circ_lines = [
        e
        for e in entidades_auto
        if e.get("layer") == "ELE-CIRCUITO" and e.get("tipo") == "LINE" and "dados" in e
    ]
    _rede_dutos_m = round(sum(e["dados"].get("comprimento", 0) for e in _circ_lines), 2)
    _rede_cabos_m = _rede_dutos_m

    _cx_insp = [
        e
        for e in entidades_auto
        if e.get("layer") == "ELE-CX. INSPEÇÃO" and e.get("tipo") == "CIRCLE"
    ]
    _rede_conduletes = len(_cx_insp)

    _cp_txts = set(
        re.match(r"(CP\d+)", t.get("conteudo", "")).group(1)
        for t in textos_auto
        if t.get("layer") == "Elétrica" and re.match(r"CP\d+", t.get("conteudo", ""))
    )
    _rede_tomadas = len(_cp_txts)

    _duto_tipo_txts = [
        t.get("conteudo", "")
        for t in textos_auto
        if "Eletroduto" in t.get("conteudo", "") and t.get("layer") == "Elétrica"
    ]
    _rede_duto_tipo = _duto_tipo_txts[0] if _duto_tipo_txts else ""

    _term_aereo = [e for e in entidades_auto if e.get("layer") == "ELE-TERMINAL AÉREO"]
    _spda_captacao = len(_term_aereo)

    _spda_lines = [
        e
        for e in entidades_auto
        if e.get("layer") == "ELE-MALHA SPDA"
        and e.get("tipo") == "LINE"
        and "dados" in e
    ]
    _spda_condulete_m = round(
        sum(e["dados"].get("comprimento", 0) for e in _spda_lines), 2
    )

    _haste_lines = [
        e
        for e in entidades_auto
        if e.get("layer") == "ELE-HASTE COBREADA"
        and e.get("tipo") == "LINE"
        and "dados" in e
    ]
    _used_h = set()
    _clusters_haste = []
    for _i, _e in enumerate(_haste_lines):
        if _i in _used_h:
            continue
        _hcx = (_e["dados"]["inicio"][0] + _e["dados"]["fim"][0]) / 2
        _hcy = (_e["dados"]["inicio"][1] + _e["dados"]["fim"][1]) / 2
        _used_h.add(_i)
        for _j, _f in enumerate(_haste_lines):
            if _j in _used_h:
                continue
            _fcx = (_f["dados"]["inicio"][0] + _f["dados"]["fim"][0]) / 2
            _fcy = (_f["dados"]["inicio"][1] + _f["dados"]["fim"][1]) / 2
            if math.hypot(_hcx - _fcx, _hcy - _fcy) < 1.0:
                _used_h.add(_j)
        _clusters_haste.append((_hcx, _hcy))
    _spda_aterramento = len(_clusters_haste)

    _tubo_lines = [
        e
        for e in entidades_auto
        if e.get("layer") == "ELE-TUBO DESCIDA"
        and e.get("tipo") == "LINE"
        and "dados" in e
    ]
    _spda_dutos_m = round(sum(e["dados"].get("comprimento", 0) for e in _tubo_lines), 2)

    _terra_lines = [
        e
        for e in entidades_auto
        if e.get("layer") == "ELE-MALHA TERRA"
        and e.get("tipo") == "LINE"
        and "dados" in e
    ]
    _cord_lines = [
        e
        for e in entidades_auto
        if e.get("layer") == "ELE-CORDOALHA"
        and e.get("tipo") == "LWPOLYLINE"
        and "dados" in e
    ]
    _spda_cabos_m = round(
        sum(e["dados"].get("comprimento", 0) for e in _terra_lines)
        + sum(
            sum(math.dist(pts[_k], pts[_k + 1]) for _k in range(len(pts) - 1))
            for e in _cord_lines
            for pts in [e["dados"].get("pontos", [])]
        ),
        2,
    )

    df5.loc[idx_linha5, ("", "Ambiente")] = "TOTAL (automático)"
    df5.loc[idx_linha5, ("Rede", "Quadros [Un]")] = ""
    df5.loc[idx_linha5, ("Rede", "Condulete [Un]")] = _rede_conduletes
    df5.loc[idx_linha5, ("Rede", "Tomadas [Un]")] = _rede_tomadas
    df5.loc[idx_linha5, ("Rede", "Dutos Tipo")] = _rede_duto_tipo
    df5.loc[idx_linha5, ("Rede", "Dutos [m]")] = _rede_dutos_m
    df5.loc[idx_linha5, ("Rede", "Cabos [m]")] = _rede_cabos_m
    df5.loc[idx_linha5, ("SPDA", "Captação [Un]")] = _spda_captacao
    df5.loc[idx_linha5, ("SPDA", "Condulete [m]")] = _spda_condulete_m
    df5.loc[idx_linha5, ("SPDA", "Aterra/o [Un]")] = _spda_aterramento
    df5.loc[idx_linha5, ("SPDA", "Dutos Tipo")] = "Eletroduto corrugado DN 100"
    df5.loc[idx_linha5, ("SPDA", "Dutos [m]")] = _spda_dutos_m
    df5.loc[idx_linha5, ("SPDA", "Cabos [m]")] = _spda_cabos_m

    _ci_ents = dados_automaticos.get("entidades", [])

    _ci_lines = [
        e
        for e in _ci_ents
        if e.get("layer") == "Contra incêndio"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and e["dados"].get("comprimento", 0) >= 0.5
    ]
    _ci_dutos_m = round(sum(e["dados"].get("comprimento", 0) for e in _ci_lines), 2)

    _ci_circles = [
        e
        for e in _ci_ents
        if e.get("layer") == "Contra incêndio"
        and e.get("tipo") == "CIRCLE"
        and "dados" in e
    ]
    _ci_hidrantes = sum(1 for c in _ci_circles if c["dados"].get("raio", 0) < 0.1)
    _ci_reserv = sum(1 for c in _ci_circles if c["dados"].get("raio", 0) >= 0.1)

    df6.loc[idx_linha6, ("", "Ambiente")] = "TOTAL (automático)"
    df6.loc[idx_linha6, ("Contra incêndio", "Reservatório Tipo")] = ""
    df6.loc[idx_linha6, ("Contra incêndio", "Reservatório [Un]")] = _ci_reserv
    df6.loc[idx_linha6, ("Contra incêndio", "Registros [Un]")] = ""
    df6.loc[idx_linha6, ("Contra incêndio", "Válvulas [Un]")] = ""
    df6.loc[idx_linha6, ("Contra incêndio", "Dutos Tipo")] = ""
    df6.loc[idx_linha6, ("Contra incêndio", "Dutos [m]")] = _ci_dutos_m
    df6.loc[idx_linha6, ("Contra incêndio", "Hidrantes [Un]")] = _ci_hidrantes
    df6.loc[idx_linha6, ("Instalações Pressurizadas", "Reservatório Tipo")] = ""
    df6.loc[idx_linha6, ("Instalações Pressurizadas", "Reservatório [Un]")] = ""
    df6.loc[idx_linha6, ("Instalações Pressurizadas", "Registros [Un]")] = ""
    df6.loc[idx_linha6, ("Instalações Pressurizadas", "Válvulas [Un]")] = ""
    df6.loc[idx_linha6, ("Instalações Pressurizadas", "Dutos Tipo")] = ""
    df6.loc[idx_linha6, ("Instalações Pressurizadas", "Dutos [m]")] = ""
    df6.loc[idx_linha6, ("Instalações Pressurizadas", "Regulador [Un]")] = ""

    # =========================
    # DF7 — Telhamentos
    # =========================

    # ── Dados automáticos: agrupar linhas de cobertura e projeção por ambiente ──
    _tel_ents = dados_automaticos.get("entidades", [])

    _cob_lines = [
        e
        for e in _tel_ents
        if e.get("layer") == "ARQ - Cobertura"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
        and e["dados"].get("comprimento", 0) >= 0.5
    ]

    _proj_lines = [
        e
        for e in _tel_ents
        if e.get("layer") == "Projeção Telhado"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
        and e["dados"].get("comprimento", 0) >= 0.5
    ]

    def _centro_linha(e):
        sx, sy = e["dados"]["inicio"][:2]
        fx, fy = e["dados"]["fim"][:2]
        return ((sx + fx) / 2, (sy + fy) / 2)

    def _dims_por_amb(comp_list):
        if not comp_list:
            return "", ""
        s = sorted(comp_list, reverse=True)
        return s[0], (s[1] if len(s) >= 2 else "")

    _cob_por_amb = {}
    for e in _cob_lines:
        cx, cy = _centro_linha(e)
        amb = get_closest_ambiente(cx, cy)
        _cob_por_amb.setdefault(amb, []).append(round(e["dados"].get("comprimento", 0), 3))

    _proj_por_amb = {}
    for e in _proj_lines:
        cx, cy = _centro_linha(e)
        amb = get_closest_ambiente(cx, cy)
        _proj_por_amb.setdefault(amb, []).append(round(e["dados"].get("comprimento", 0), 3))

    idx_linha7 = 0

    for item7 in dados_manuais.get("ambientes", []):
        nome7 = item7.get("nome", "")
        df7.loc[idx_linha7, ("", "Ambiente")] = nome7

        cob_C, cob_L = _dims_por_amb(_cob_por_amb.get(nome7, []))
        df7.loc[idx_linha7, ("Telhados", "C [m]")] = cob_C
        df7.loc[idx_linha7, ("Telhados", "L [m]")] = cob_L
        df7.loc[idx_linha7, ("Telhados", "H [m]")] = item7.get("inclinacao", "")

        madeira = item7.get("madeira", [])
        mad = madeira[0] if madeira else {}
        df7.loc[idx_linha7, ("Estrutura", "Tipo")] = mad.get("tipoPeca", "")

        secao_str = mad.get("secao", "")
        if secao_str and "x" in secao_str.lower():
            partes = re.split(r"[xX]", secao_str)
            try:
                c_est = float(partes[0]) / 100
                l_est = float(partes[1]) / 100
                df7.loc[idx_linha7, ("Estrutura", "C [m]")] = c_est
                df7.loc[idx_linha7, ("Estrutura", "L [m]")] = l_est
                df7.loc[idx_linha7, ("Estrutura", "e [m]")] = item7.get("espessura", "")
                df7.loc[idx_linha7, ("Estrutura", "a [m²]")] = round(c_est * l_est, 4)
            except (ValueError, IndexError):
                df7.loc[idx_linha7, ("Estrutura", "C [m]")] = ""
                df7.loc[idx_linha7, ("Estrutura", "L [m]")] = ""
                df7.loc[idx_linha7, ("Estrutura", "e [m]")] = item7.get("espessura", "")
                df7.loc[idx_linha7, ("Estrutura", "a [m²]")] = ""
        else:
            df7.loc[idx_linha7, ("Estrutura", "C [m]")] = ""
            df7.loc[idx_linha7, ("Estrutura", "L [m]")] = ""
            df7.loc[idx_linha7, ("Estrutura", "e [m]")] = item7.get("espessura", "")
            df7.loc[idx_linha7, ("Estrutura", "a [m²]")] = ""

        proj_C, proj_L = _dims_por_amb(_proj_por_amb.get(nome7, []))
        df7.loc[idx_linha7, ("Telhamento", "Tipo")] = item7.get("tipoTelhamento", "")
        df7.loc[idx_linha7, ("Telhamento", "C [m]")] = proj_C
        df7.loc[idx_linha7, ("Telhamento", "L [m]")] = proj_L
        df7.loc[idx_linha7, ("Telhamento", "e [m]")] = item7.get("espessura", "")

        idx_linha7 += 1

    return df, df2, df3, df4, df5, df6, df7
