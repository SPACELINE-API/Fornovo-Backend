import pandas as pd
import json
import os
from collections import Counter

colunas_estruturas_viga = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Peça"),
        ("Seção", "L [m]"),
        ("Seção", "h [m]"),
        ("", "C [m]"),
        ("", "Lastro [m³]"),
        ("", "Concreto [m³]"),
        ("", "Ferragem [KgF]"),
        ("", "Estribo [KgF]"),
        ("Forma em Madeira", "L [m]"),
        ("Forma em Madeira", "C [m]"),
        ("Forma em Madeira", "A [m²]"),
    ]
)

colunas_estruturas_fundacoes = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Peça"),
        ("Valores por Peça", "L [m]"),
        ("Valores por Peça", "h [m]"),
        ("Valores por Peça", "C [m]"),
        ("Valores Totais", "Lastro [m³]"),
        ("Valores Totais", "Concreto [m³]"),
        ("Valores Totais", "Ferragem [KgF]"),
        ("Valores Totais", "Estribo [KgF]"),
        ("Forma em Madeira", "L [m]"),
        ("Forma em Madeira", "C [m]"),
        ("Forma em Madeira", "A Tot [m²]"),
    ]
)

colunas_estruturas_concreto = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Peça"),
        ("", "L [m]"),
        ("", "h [m]"),
        ("", "C [m]"),
        ("", "Concreto [m³]"),
        ("", "Ferragem [KgF]"),
        ("", "Estribo [KgF]"),
        ("Forma em Madeira", "C [m]"),
        ("Forma em Madeira", "L [m]"),
        ("Forma em Madeira", "A [m²]"),
        ("Forma em Madeira", "Janela lança/o [m]"),
    ]
)

colunas_estruturas_metalica = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Peça"),
        ("", "h [m]"),
        ("", "Perfil"),
        ("Seção", "L [m]"),
        ("Seção", "C [m]"),
        ("", "Peso [KgF]"),
        ("", "Elastômero [m²]"),
        ("Equipamento de apoio", "h [m]"),
        ("Equipamento de apoio", "C [m]"),
        ("Equipamento de apoio", "e [m]"),
        ("Equipamento de apoio", "A [m²]"),
        ("Equipamento de apoio", "Peso [KgF]"),
    ]
)

colunas_estruturas_madeira = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Estrutura", "Peça"),
        ("Estrutura", "Tipo"),
        ("Estrutura", "Qtd"),
        ("Estrutura", "C tot [m]"),
        ("Estrutura", "Base [cm]"),
        ("Estrutura", "h/L [cm]"),
        ("Estrutura", "e [cm]"),
        ("Estrutura", "Peso [KgF]"),
        ("Telhamento", "T.Peça"),
        ("Telhamento", "T.Tipo"),
        ("Telhamento", "L [cm]"),
        ("Telhamento", "h [cm]"),
        ("Telhamento", "e [cm]"),
        ("Telhamento", "proj [m²]"),
        ("Telhamento", "real [m²]"),
        ("Telhamento", "i [%]"),
    ]
)

colunas_estruturas_escada = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
        ("", "Peça"),
        ("", "C [m]"),
        ("", "L [m]"),
        ("", "h [m]"),
        ("", "e [m]"),
        ("Pisada", "C [m]"),
        ("Pisada", "A [m²]"),
        ("Pisada", "Concreto [m³]"),
        ("Pisada", "Bocel [m]"),
        ("Espelho", "h [m]"),
        ("Espelho", "A [m²]"),
        ("Espelho", "Concreto [m³]"),
        ("Espelho", "i [%]"),
        ("Parede de Contenção", "L [m]"),
        ("Parede de Contenção", "h [m]"),
        ("Parede de Contenção", "C [m]"),
        ("Parede de Contenção", "A [m²]"),
        ("Parede de Contenção", "Concreto [m³]"),
        ("Guia Balizamento", "L [m]"),
        ("Guia Balizamento", "h [m]"),
        ("Armação", "Ferragem [KgF]"),
        ("Armação", "Estribo [KgF]"),
        ("Forma em Madeira", "h [m]"),
        ("Forma em Madeira", "C [m]"),
        ("Forma em Madeira", "A [m²]"),
    ]
)


HEADER_SPLIT = {
    "Ambiente": ("Ambiente", ""),
    "Peça": ("Peça", ""),
    "Tipo": ("Tipo", ""),
    "Qtd": ("Qtd", ""),
    "Perfil": ("Perfil", ""),
    "L [m]": ("L", "[m]"),
    "h [m]": ("h", "[m]"),
    "C [m]": ("C", "[m]"),
    "e [m]": ("e", "[m]"),
    "C tot [m]": ("C tot", "[m]"),
    "Base [cm]": ("Base", "[cm]"),
    "h/L [cm]": ("h/L", "[cm]"),
    "e [cm]": ("e", "[cm]"),
    "Lastro [m³]": ("Lastro", "[m³]"),
    "Concreto [m³]": ("Concreto", "[m³]"),
    "Ferragem [KgF]": ("Ferragem", "[KgF]"),
    "Estribo [KgF]": ("Estribo", "[KgF]"),
    "Peso [KgF]": ("Peso", "[KgF]"),
    "Elastômero [m²]": ("Elastômero", "[m²]"),
    "A [m²]": ("A", "[m²]"),
    "A Tot [m²]": ("A Tot", "[m²]"),
    "proj [m²]": ("proj", "[m²]"),
    "real [m²]": ("real", "[m²]"),
    "i [%]": ("i", "[%]"),
    "T.Peça": ("Peça", ""),
    "T.Tipo": ("Tipo", ""),
    "Janela lança/o [m]": ("Janela", "lança/o [m]"),
    "Bocel [m]": ("Bocel", "[m]"),
    "Ferragem [KgF]": ("Ferragem", "[KgF]"),
    "Estribo [KgF]": ("Estribo", "[KgF]"),
    "Concreto [m³]": ("Concreto", "[m³]"),
    "A [m²]": ("A", "[m²]"),
    "i [%]": ("i", "[%]"),
    "Local": ("Local", ""),
}


def estruturas(
    dados_manuais, dados_automaticos
):
    df_viga_baldrame = pd.DataFrame(columns=colunas_estruturas_viga)
    df_estacas_blocos = pd.DataFrame(columns=colunas_estruturas_fundacoes)
    df_estacas = pd.DataFrame(columns=colunas_estruturas_fundacoes)
    df_sapatas = pd.DataFrame(columns=colunas_estruturas_fundacoes)
    df_radier = pd.DataFrame(columns=colunas_estruturas_fundacoes)
    df_sapata_corrida = pd.DataFrame(columns=colunas_estruturas_fundacoes)
    df_pilares = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_vigas = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_lajes = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_contencao = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_bloco = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_placa = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_passarelas = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_porticos = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_bermas = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_recuperacao = pd.DataFrame(columns=colunas_estruturas_concreto)
    df_pilares_met = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_vigas_met = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_lajes_met = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_passarelas_met = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_escadas_met = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_escadas = pd.DataFrame(columns=colunas_estruturas_escada)
    df_porticos_met = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_para_balas = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_recuperacao_met = pd.DataFrame(columns=colunas_estruturas_metalica)
    df_madeira = pd.DataFrame(columns=colunas_estruturas_madeira)

    ambientes = dados_manuais.get("ambientes", [])

    for item in ambientes:
        nome = item.get("nome", "")

        for fnd in item.get("fundacoes", []):
            tipo_fnd = fnd.get("tipo", "").lower()

            if "baldrame" in tipo_fnd or "viga" in tipo_fnd:
                df_ref = df_viga_baldrame
                cols = colunas_estruturas_viga
                is_viga = True
            elif "estaca" in tipo_fnd and "bloco" in tipo_fnd:
                df_ref = df_estacas_blocos
                cols = colunas_estruturas_fundacoes
                is_viga = False
            elif "estaca" in tipo_fnd:
                df_ref = df_estacas
                cols = colunas_estruturas_fundacoes
                is_viga = False
            elif "radier" in tipo_fnd:
                df_ref = df_radier
                cols = colunas_estruturas_fundacoes
                is_viga = False
            elif "corrida" in tipo_fnd:
                df_ref = df_sapata_corrida
                cols = colunas_estruturas_fundacoes
                is_viga = False
            else:
                df_ref = df_sapatas
                cols = colunas_estruturas_fundacoes
                is_viga = False

            idx = len(df_ref)
            df_ref.loc[idx, ("", "Ambiente")] = nome
            df_ref.loc[idx, ("", "Peça")] = fnd.get("tipo", "")

            if is_viga:
                df_ref.loc[idx, ("Seção", "L [m]")] = ""
                df_ref.loc[idx, ("Seção", "h [m]")] = fnd.get("profundidade", "")
                df_ref.loc[idx, ("", "C [m]")] = ""
                df_ref.loc[idx, ("", "Lastro [m³]")] = fnd.get("volumeLastro", "")
                df_ref.loc[idx, ("", "Concreto [m³]")] = fnd.get("volumeConcreto", "")
                df_ref.loc[idx, ("", "Ferragem [KgF]")] = fnd.get("pesoFerragem", "")
                df_ref.loc[idx, ("", "Estribo [KgF]")] = fnd.get("pesoEstribo", "")
                df_ref.loc[idx, ("Forma em Madeira", "L [m]")] = ""
                df_ref.loc[idx, ("Forma em Madeira", "C [m]")] = ""
                df_ref.loc[idx, ("Forma em Madeira", "A [m²]")] = fnd.get(
                    "areaForma", ""
                )

            else:
                df_ref.loc[idx, ("Valores por Peça", "L [m]")] = ""
                df_ref.loc[idx, ("Valores por Peça", "h [m]")] = fnd.get(
                    "profundidade", ""
                )
                df_ref.loc[idx, ("Valores por Peça", "C [m]")] = ""
                df_ref.loc[idx, ("Valores Totais", "Lastro [m³]")] = fnd.get(
                    "volumeLastro", ""
                )
                df_ref.loc[idx, ("Valores Totais", "Concreto [m³]")] = fnd.get(
                    "volumeConcreto", ""
                )
                df_ref.loc[idx, ("Valores Totais", "Ferragem [KgF]")] = fnd.get(
                    "pesoFerragem", ""
                )
                df_ref.loc[idx, ("Valores Totais", "Estribo [KgF]")] = fnd.get(
                    "pesoEstribo", ""
                )
                df_ref.loc[idx, ("Forma em Madeira", "L [m]")] = ""
                df_ref.loc[idx, ("Forma em Madeira", "C [m]")] = ""
                df_ref.loc[idx, ("Forma em Madeira", "A Tot [m²]")] = fnd.get(
                    "areaForma", ""
                )

        for sup in item.get("superestrutura", []):
            tipo_sup = sup.get("tipo", "").lower()

            if "pilar" in tipo_sup:
                df_ref = df_pilares
            elif "laje" in tipo_sup:
                df_ref = df_lajes
            elif "contencao" in tipo_sup or "contenção" in tipo_sup:
                df_ref = df_contencao
            elif "bloco" in tipo_sup:
                df_ref = df_bloco
            elif "placa" in tipo_sup:
                df_ref = df_placa
            elif "passarela" in tipo_sup:
                df_ref = df_passarelas
            elif "portico" in tipo_sup or "pórtico" in tipo_sup:
                df_ref = df_porticos
            elif "berma" in tipo_sup:
                df_ref = df_bermas
            elif "recuperacao" in tipo_sup:
                df_ref = df_recuperacao
            else:
                df_ref = df_vigas

            idx = len(df_ref)
            df_ref.loc[idx, ("", "Ambiente")] = nome
            df_ref.loc[idx, ("", "Peça")] = sup.get("tipo", "")
            df_ref.loc[idx, ("", "L [m]")] = sup.get("largura", "")
            df_ref.loc[idx, ("", "h [m]")] = sup.get("altura", "")
            df_ref.loc[idx, ("", "C [m]")] = ""
            df_ref.loc[idx, ("", "Concreto [m³]")] = sup.get("volumeConcreto", "")
            df_ref.loc[idx, ("", "Ferragem [KgF]")] = sup.get("pesoFerragem", "")
            df_ref.loc[idx, ("", "Estribo [KgF]")] = sup.get("pesoEstribo", "")
            df_ref.loc[idx, ("Forma em Madeira", "C [m]")] = ""
            df_ref.loc[idx, ("Forma em Madeira", "L [m]")] = ""
            df_ref.loc[idx, ("Forma em Madeira", "A [m²]")] = sup.get("areaForma", "")
            df_ref.loc[idx, ("Forma em Madeira", "Janela lança/o [m]")] = sup.get(
                "janelaLancamento", ""
            )

        for met in item.get("metalicas", []):
            tipo_met = met.get("tipo", "").lower()

            if "pilar" in tipo_met:
                df_ref = df_pilares_met
            elif "laje" in tipo_met:
                df_ref = df_lajes_met
            elif "passarela" in tipo_met:
                df_ref = df_passarelas_met
            elif "escada" in tipo_met:
                df_ref = df_escadas_met
            elif "portico" in tipo_met or "pórtico" in tipo_met:
                df_ref = df_porticos_met
            elif "para-bala" in tipo_met or "para bala" in tipo_met:
                df_ref = df_para_balas
            elif "recuperacao" in tipo_met:
                df_ref = df_recuperacao_met
            else:
                df_ref = df_vigas_met

            secao_raw = met.get("secao", "")
            partes = str(secao_raw).split("x") if "x" in str(secao_raw) else ["", ""]
            secao_l = partes[0] if len(partes) > 0 else ""
            secao_c = partes[1] if len(partes) > 1 else ""
            idx = len(df_ref)
            df_ref.loc[idx, ("", "Ambiente")] = nome
            df_ref.loc[idx, ("", "Peça")] = met.get("tipo", "")
            df_ref.loc[idx, ("", "h [m]")] = ""
            df_ref.loc[idx, ("", "Perfil")] = met.get("tipoPerfil", "")
            df_ref.loc[idx, ("Seção", "L [m]")] = secao_l
            df_ref.loc[idx, ("Seção", "C [m]")] = secao_c
            df_ref.loc[idx, ("", "Peso [KgF]")] = met.get("peso", "")
            df_ref.loc[idx, ("", "Elastômero [m²]")] = met.get("elastomero", "")
            df_ref.loc[idx, ("Equipamento de apoio", "h [m]")] = ""
            df_ref.loc[idx, ("Equipamento de apoio", "C [m]")] = ""
            df_ref.loc[idx, ("Equipamento de apoio", "e [m]")] = ""
            df_ref.loc[idx, ("Equipamento de apoio", "A [m²]")] = ""
            df_ref.loc[idx, ("Equipamento de apoio", "Peso [KgF]")] = ""

        for mad in item.get("madeira", []):
            idx = len(df_madeira)
            secao_raw = mad.get("secao", "")
            partes = str(secao_raw).split("x") if "x" in str(secao_raw) else ["", ""]
            base = partes[0] if len(partes) > 0 else ""
            alt = partes[1] if len(partes) > 1 else ""
            df_madeira.loc[idx, ("", "Ambiente")] = nome
            df_madeira.loc[idx, ("Estrutura", "Peça")] = mad.get("tipoPeca", "")
            df_madeira.loc[idx, ("Estrutura", "Tipo")] = ""
            df_madeira.loc[idx, ("Estrutura", "Qtd")] = ""
            df_madeira.loc[idx, ("Estrutura", "C tot [m]")] = ""
            df_madeira.loc[idx, ("Estrutura", "Base [cm]")] = base
            df_madeira.loc[idx, ("Estrutura", "h/L [cm]")] = alt
            df_madeira.loc[idx, ("Estrutura", "e [cm]")] = ""
            df_madeira.loc[idx, ("Estrutura", "Peso [KgF]")] = mad.get("pesoTotal", "")
            df_madeira.loc[idx, ("Telhamento", "T.Peça")] = ""
            df_madeira.loc[idx, ("Telhamento", "T.Tipo")] = mad.get(
                "tipoTelhamento", ""
            )
            df_madeira.loc[idx, ("Telhamento", "L [cm]")] = ""
            df_madeira.loc[idx, ("Telhamento", "h [cm]")] = ""
            df_madeira.loc[idx, ("Telhamento", "e [cm]")] = ""
            df_madeira.loc[idx, ("Telhamento", "proj [m²]")] = ""
            df_madeira.loc[idx, ("Telhamento", "real [m²]")] = ""
            df_madeira.loc[idx, ("Telhamento", "i [%]")] = ""

    import re, math

    # ── extrair ambientes do CAD para associação por proximidade ─────────────
    ambientes_cad = []
    for _txt in dados_automaticos.get("textos", []):
        _c = _txt.get("conteudo", "")
        if "m²" in _c.lower():
            _ma = re.search(r"(\d+[.,]\d+)\s*m²", _c, re.IGNORECASE)
            if _ma and _txt.get("posicao"):
                _parts = _c.split("\\P")
                _aidx = next(
                    (
                        i
                        for i, p in enumerate(_parts)
                        if re.search(r"\d+[.,]\d+\s*m²", p, re.IGNORECASE)
                    ),
                    -1,
                )
                _raw = " ".join(_parts[:_aidx]) if _aidx > 0 else _parts[0]
                _nome = (
                    re.sub(r"\\[^;\\]+;", "", _raw).replace("{", "").replace("}", "")
                )
                _nome = re.sub(r"\\[Pp]", " ", _nome)
                _nome = re.sub(r"\d+[.,]\d+\s*m²", "", _nome, flags=re.IGNORECASE)
                _nome = re.sub(r"\s+", " ", _nome).strip()
                if _nome:
                    ambientes_cad.append({"nome": _nome, "pos": _txt["posicao"]})

    def _get_amb(cx, cy):
        if not ambientes_cad:
            return "Não identificado"

        best = min(
            ambientes_cad, key=lambda a: math.hypot(cx - a["pos"][0], cy - a["pos"][1])
        )

        if math.hypot(cx - best["pos"][0], cy - best["pos"][1]) < 250:
            return best["nome"] or "Não identificado"

        return "Não identificado"

    entidades = dados_automaticos.get("entidades", [])

    # ── 3.2.1 Pilares — agrupamento por componentes conectados ───────────────
    _pilar_lines = [
        e
        for e in entidades
        if e.get("layer") == "Estrutural - Pilares"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
    ]
    _pilar_circs = [
        e
        for e in entidades
        if e.get("layer") == "Estrutural - Pilares"
        and e.get("tipo") == "CIRCLE"
        and "dados" in e
    ]

    def _rpt(pt):
        return (round(pt[0], 2), round(pt[1], 2))

    _adj = {}
    _edges = []
    for _i, _ln in enumerate(_pilar_lines):
        _p1 = _rpt(_ln["dados"]["inicio"])
        _p2 = _rpt(_ln["dados"]["fim"])
        _edges.append((_i, _p1, _p2))
        _adj.setdefault(_p1, []).append(_i)
        _adj.setdefault(_p2, []).append(_i)

    _visited = set()
    _comps = []
    for _i in range(len(_pilar_lines)):
        if _i in _visited:
            continue
        _comp, _q = [], [_i]
        _visited.add(_i)
        while _q:
            _cur = _q.pop(0)
            _comp.append(_cur)
            if _cur < len(_edges):
                for _nb in _adj.get(_edges[_cur][1], []) + _adj.get(
                    _edges[_cur][2], []
                ):
                    if _nb not in _visited:
                        _visited.add(_nb)
                        _q.append(_nb)
        _comps.append(_comp)

    for _comp in _comps:
        if len(_comp) < 2:
            continue
        _comprimentos = sorted(
            [round(_pilar_lines[i]["dados"].get("comprimento", 0), 3) for i in _comp],
        )
        _pts_x = [
            c
            for i in _comp
            for c in [
                _pilar_lines[i]["dados"]["inicio"][0],
                _pilar_lines[i]["dados"]["fim"][0],
            ]
        ]
        _pts_y = [
            c
            for i in _comp
            for c in [
                _pilar_lines[i]["dados"]["inicio"][1],
                _pilar_lines[i]["dados"]["fim"][1],
            ]
        ]
        _cx = sum(_pts_x) / len(_pts_x)
        _cy = sum(_pts_y) / len(_pts_y)
        _amb = _get_amb(_cx, _cy)
        _L = _comprimentos[0] if _comprimentos else ""
        _C = _comprimentos[-1] if _comprimentos else ""
        _idx = len(df_pilares)
        df_pilares.loc[_idx, ("", "Ambiente")] = _amb
        df_pilares.loc[_idx, ("", "Peça")] = "Pilar"
        df_pilares.loc[_idx, ("", "L [m]")] = _L
        df_pilares.loc[_idx, ("", "h [m]")] = ""
        df_pilares.loc[_idx, ("", "C [m]")] = _C
        df_pilares.loc[_idx, ("", "Concreto [m³]")] = ""
        df_pilares.loc[_idx, ("", "Ferragem [KgF]")] = ""
        df_pilares.loc[_idx, ("", "Estribo [KgF]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "C [m]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "L [m]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "A [m²]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "Janela lança/o [m]")] = ""

    for _circ in _pilar_circs:
        _raio = _circ["dados"].get("raio", 0)
        _cx, _cy = _circ["dados"]["centro"][:2]
        _amb = _get_amb(_cx, _cy)
        _d = round(2 * _raio, 3)
        _idx = len(df_pilares)
        df_pilares.loc[_idx, ("", "Ambiente")] = _amb if _amb else "Não identificado"
        df_pilares.loc[_idx, ("", "Peça")] = "Pilar circular"
        df_pilares.loc[_idx, ("", "L [m]")] = _d
        df_pilares.loc[_idx, ("", "h [m]")] = ""
        df_pilares.loc[_idx, ("", "C [m]")] = _d
        df_pilares.loc[_idx, ("", "Concreto [m³]")] = ""
        df_pilares.loc[_idx, ("", "Ferragem [KgF]")] = ""
        df_pilares.loc[_idx, ("", "Estribo [KgF]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "C [m]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "L [m]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "A [m²]")] = ""
        df_pilares.loc[_idx, ("Forma em Madeira", "Janela lança/o [m]")] = ""

    # ── 3.2.2 Vigas — agrupamento por alinhamento ────────────────────────────
    _viga_lines = [
        e
        for e in entidades
        if e.get("layer") == "Estrutural - Vigas"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
    ]

    TOL_ANG = 2.0
    TOL_DIST = 0.5
    TOL_OVL = 0.05

    def _ang(v):
        dx = v["dados"]["fim"][0] - v["dados"]["inicio"][0]
        dy = v["dados"]["fim"][1] - v["dados"]["inicio"][1]
        return math.degrees(math.atan2(dy, dx)) % 180

    def _med(v):
        return (
            (v["dados"]["inicio"][0] + v["dados"]["fim"][0]) / 2,
            (v["dados"]["inicio"][1] + v["dados"]["fim"][1]) / 2,
        )

    def _dist_pt_reta(px, py, v):
        sx, sy = v["dados"]["inicio"][:2]
        fx, fy = v["dados"]["fim"][:2]
        dx, dy = fx - sx, fy - sy
        den = dx * dx + dy * dy
        if den < 1e-12:
            return math.dist([px, py], [sx, sy])
        t = ((px - sx) * dx + (py - sy) * dy) / den
        return math.dist([px, py], [sx + t * dx, sy + t * dy])

    def _proj(v, ux, uy):
        t0 = v["dados"]["inicio"][0] * ux + v["dados"]["inicio"][1] * uy
        t1 = v["dados"]["fim"][0] * ux + v["dados"]["fim"][1] * uy
        return (min(t0, t1), max(t0, t1))

    def _sobrepoem(a, b, tol):
        return a[1] >= b[0] + tol and b[1] >= a[0] + tol

    _meta_v = [
        {
            "idx": i,
            "linha": v,
            "ang": _ang(v),
            "med": _med(v),
            "comp": v["dados"].get("comprimento", 0),
        }
        for i, v in enumerate(_viga_lines)
        if "inicio" in v["dados"] and "fim" in v["dados"]
    ]
    _meta_v.sort(key=lambda m: -m["comp"])

    _used_v = set()
    _grupos_v = []
    for _semente in _meta_v:
        if _semente["idx"] in _used_v:
            continue
        _grp = [_semente]
        _used_v.add(_semente["idx"])
        _ang_s = _semente["ang"]
        _rad_s = math.radians(_ang_s)
        _ux, _uy = math.cos(_rad_s), math.sin(_rad_s)
        _proj_s = _proj(_semente["linha"], _ux, _uy)
        for _cand in _meta_v:
            if _cand["idx"] in _used_v:
                continue
            _da = abs(_cand["ang"] - _ang_s)
            _da = min(_da, 180 - _da)
            if _da > TOL_ANG:
                continue
            _px, _py = _cand["med"]
            if _dist_pt_reta(_px, _py, _semente["linha"]) > TOL_DIST:
                continue
            if not _sobrepoem(_proj_s, _proj(_cand["linha"], _ux, _uy), TOL_OVL):
                continue
            _grp.append(_cand)
            _used_v.add(_cand["idx"])
        _grupos_v.append(_grp)

    for _grp in _grupos_v:
        _pts_x = [
            c
            for m in _grp
            for c in [m["linha"]["dados"]["inicio"][0], m["linha"]["dados"]["fim"][0]]
        ]
        _pts_y = [
            c
            for m in _grp
            for c in [m["linha"]["dados"]["inicio"][1], m["linha"]["dados"]["fim"][1]]
        ]
        _cx = sum(_pts_x) / len(_pts_x)
        _cy = sum(_pts_y) / len(_pts_y)
        _amb = _get_amb(_cx, _cy)
        _ref = max(_grp, key=lambda m: m["comp"])
        _C = round(_ref["comp"], 3)
        _longas = sorted(_grp, key=lambda m: -m["comp"])
        if len(_longas) >= 2:
            _px2, _py2 = _longas[1]["med"]
            _e = round(_dist_pt_reta(_px2, _py2, _longas[0]["linha"]), 3)
        else:
            _e = ""
        if _C < 0.05:
            continue
        _idx = len(df_vigas)
        df_vigas.loc[_idx, ("", "Ambiente")] = _amb
        df_vigas.loc[_idx, ("", "Peça")] = "Viga"
        df_vigas.loc[_idx, ("", "L [m]")] = _e
        df_vigas.loc[_idx, ("", "h [m]")] = ""
        df_vigas.loc[_idx, ("", "C [m]")] = _C
        df_vigas.loc[_idx, ("", "Concreto [m³]")] = ""
        df_vigas.loc[_idx, ("", "Ferragem [KgF]")] = ""
        df_vigas.loc[_idx, ("", "Estribo [KgF]")] = ""
        df_vigas.loc[_idx, ("Forma em Madeira", "C [m]")] = ""
        df_vigas.loc[_idx, ("Forma em Madeira", "L [m]")] = ""
        df_vigas.loc[_idx, ("Forma em Madeira", "A [m²]")] = ""
        df_vigas.loc[_idx, ("Forma em Madeira", "Janela lança/o [m]")] = ""

    # ── 3.2.3 Lajes — agrupamento por componentes conectados ────────────────
    _laje_lines = [
        e
        for e in entidades
        if e.get("layer") == "Estrutural - Lajes"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
    ]

    _adj_lj = {}
    _edges_lj = []
    for _i, _ln in enumerate(_laje_lines):
        _p1 = _rpt(_ln["dados"]["inicio"])
        _p2 = _rpt(_ln["dados"]["fim"])
        _edges_lj.append((_i, _p1, _p2))
        _adj_lj.setdefault(_p1, []).append(_i)
        _adj_lj.setdefault(_p2, []).append(_i)

    _visited_lj = set()
    _comps_lj = []
    for _i in range(len(_laje_lines)):
        if _i in _visited_lj:
            continue
        _comp, _q = [], [_i]
        _visited_lj.add(_i)
        while _q:
            _cur = _q.pop(0)
            _comp.append(_cur)
            if _cur < len(_edges_lj):
                for _nb in _adj_lj.get(_edges_lj[_cur][1], []) + _adj_lj.get(
                    _edges_lj[_cur][2], []
                ):
                    if _nb not in _visited_lj:
                        _visited_lj.add(_nb)
                        _q.append(_nb)
        _comps_lj.append(_comp)

    for _comp in _comps_lj:
        if len(_comp) < 2:
            continue
        _comps_sorted = sorted(
            [round(_laje_lines[i]["dados"].get("comprimento", 0), 3) for i in _comp]
        )
        _pts_x = [
            c
            for i in _comp
            for c in [
                _laje_lines[i]["dados"]["inicio"][0],
                _laje_lines[i]["dados"]["fim"][0],
            ]
        ]
        _pts_y = [
            c
            for i in _comp
            for c in [
                _laje_lines[i]["dados"]["inicio"][1],
                _laje_lines[i]["dados"]["fim"][1],
            ]
        ]
        _cx = sum(_pts_x) / len(_pts_x)
        _cy = sum(_pts_y) / len(_pts_y)
        _amb = _get_amb(_cx, _cy)
        _L = _comps_sorted[0] if _comps_sorted else ""
        _C = _comps_sorted[-1] if _comps_sorted else ""
        _A = round(_L * _C, 4) if _L and _C else ""
        _idx = len(df_lajes)
        df_lajes.loc[_idx, ("", "Ambiente")] = _amb
        df_lajes.loc[_idx, ("", "Peça")] = "Laje"
        df_lajes.loc[_idx, ("", "L [m]")] = _L
        df_lajes.loc[_idx, ("", "h [m]")] = ""
        df_lajes.loc[_idx, ("", "C [m]")] = _C
        df_lajes.loc[_idx, ("", "Concreto [m³]")] = ""
        df_lajes.loc[_idx, ("", "Ferragem [KgF]")] = ""
        df_lajes.loc[_idx, ("", "Estribo [KgF]")] = ""
        df_lajes.loc[_idx, ("Forma em Madeira", "C [m]")] = _C
        df_lajes.loc[_idx, ("Forma em Madeira", "L [m]")] = _L
        df_lajes.loc[_idx, ("Forma em Madeira", "A [m²]")] = _A
        df_lajes.loc[_idx, ("Forma em Madeira", "Janela lança/o [m]")] = ""

    # ── 3.2.4 Paredes de Contenção — alinhamento sobre ARQ - Alvenaria (-) ──
    _cont_lines = [
        e
        for e in entidades
        if e.get("layer") == "ARQ - Alvenaria (-)"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
        and e["dados"].get("comprimento", 0) >= 0.5
    ]

    _meta_ct = [
        {
            "idx": i,
            "linha": v,
            "ang": _ang(v),
            "med": _med(v),
            "comp": v["dados"].get("comprimento", 0),
        }
        for i, v in enumerate(_cont_lines)
        if "inicio" in v["dados"] and "fim" in v["dados"]
    ]
    _meta_ct.sort(key=lambda m: -m["comp"])

    _used_ct = set()
    _grupos_ct = []
    for _semente in _meta_ct:
        if _semente["idx"] in _used_ct:
            continue
        _grp = [_semente]
        _used_ct.add(_semente["idx"])
        _ang_s = _semente["ang"]
        _rad_s = math.radians(_ang_s)
        _ux, _uy = math.cos(_rad_s), math.sin(_rad_s)
        _proj_s = _proj(_semente["linha"], _ux, _uy)
        for _cand in _meta_ct:
            if _cand["idx"] in _used_ct:
                continue
            _da = abs(_cand["ang"] - _ang_s)
            _da = min(_da, 180 - _da)
            if _da > TOL_ANG:
                continue
            _px, _py = _cand["med"]
            if _dist_pt_reta(_px, _py, _semente["linha"]) > TOL_DIST:
                continue
            if not _sobrepoem(_proj_s, _proj(_cand["linha"], _ux, _uy), TOL_OVL):
                continue
            _grp.append(_cand)
            _used_ct.add(_cand["idx"])
        _grupos_ct.append(_grp)

    for _grp in _grupos_ct:
        _pts_x = [
            c
            for m in _grp
            for c in [m["linha"]["dados"]["inicio"][0], m["linha"]["dados"]["fim"][0]]
        ]
        _pts_y = [
            c
            for m in _grp
            for c in [m["linha"]["dados"]["inicio"][1], m["linha"]["dados"]["fim"][1]]
        ]
        _cx = sum(_pts_x) / len(_pts_x)
        _cy = sum(_pts_y) / len(_pts_y)
        _amb = _get_amb(_cx, _cy)
        _ref = max(_grp, key=lambda m: m["comp"])
        _C = round(_ref["comp"], 3)
        _longas = sorted(_grp, key=lambda m: -m["comp"])
        if len(_longas) >= 2:
            _px2, _py2 = _longas[1]["med"]
            _e = round(_dist_pt_reta(_px2, _py2, _longas[0]["linha"]), 3)
        else:
            _e = ""
        if _C < 0.05:
            continue
        _idx = len(df_contencao)
        df_contencao.loc[_idx, ("", "Ambiente")] = _amb
        df_contencao.loc[_idx, ("", "Peça")] = "Parede de Contenção"
        df_contencao.loc[_idx, ("", "L [m]")] = _e
        df_contencao.loc[_idx, ("", "h [m]")] = ""
        df_contencao.loc[_idx, ("", "C [m]")] = _C
        df_contencao.loc[_idx, ("", "Concreto [m³]")] = ""
        df_contencao.loc[_idx, ("", "Ferragem [KgF]")] = ""
        df_contencao.loc[_idx, ("", "Estribo [KgF]")] = ""
        df_contencao.loc[_idx, ("Forma em Madeira", "C [m]")] = ""
        df_contencao.loc[_idx, ("Forma em Madeira", "L [m]")] = ""
        df_contencao.loc[_idx, ("Forma em Madeira", "A [m²]")] = ""
        df_contencao.loc[_idx, ("Forma em Madeira", "Janela lança/o [m]")] = ""

    # ── 3.2.5 Bloco Estrutural ───────────────────────────────────────────────
    _bloco_lines = [
        e
        for e in entidades
        if e.get("layer")
        and "alvenaria" in str(e.get("layer")).lower()
        and "(-)" not in str(e.get("layer"))  # Evita pegar a layer da contenção (3.2.4)
        and e.get("tipo") == "LINE"
        and "dados" in e
    ]

    _meta_bl = [
        {
            "idx": i,
            "linha": v,
            "ang": _ang(v),
            "med": _med(v),
            "comp": v["dados"].get("comprimento", 0),
        }
        for i, v in enumerate(_bloco_lines)
    ]
    _meta_bl.sort(key=lambda m: -m["comp"])

    _used_bl = set()
    _grupos_bl = []

    for _sem in _meta_bl:
        if _sem["idx"] in _used_bl:
            continue
        _grp = [_sem]
        _used_bl.add(_sem["idx"])
        _rad = math.radians(_sem["ang"])
        _ux, _uy = math.cos(_rad), math.sin(_rad)
        _prj_s = _proj(_sem["linha"], _ux, _uy)

        for _cand in _meta_bl:
            if _cand["idx"] in _used_bl:
                continue
            _da = abs(_cand["ang"] - _sem["ang"])
            if min(_da, 180 - _da) > TOL_ANG:
                continue
            if _dist_pt_reta(_cand["med"][0], _cand["med"][1], _sem["linha"]) > 1.0:
                continue
            if not _sobrepoem(_prj_s, _proj(_cand["linha"], _ux, _uy), TOL_OVL):
                continue
            _grp.append(_cand)
            _used_bl.add(_cand["idx"])
        _grupos_bl.append(_grp)

    for _g in _grupos_bl:
        _px = [
            c
            for m in _g
            for c in [m["linha"]["dados"]["inicio"][0], m["linha"]["dados"]["fim"][0]]
        ]
        _py = [
            c
            for m in _g
            for c in [m["linha"]["dados"]["inicio"][1], m["linha"]["dados"]["fim"][1]]
        ]
        _cx, _cy = sum(_px) / len(_px), sum(_py) / len(_py)

        _amb = _get_amb(_cx, _cy)
        _ref = max(_g, key=lambda m: m["comp"])
        _lng = sorted(_g, key=lambda m: -m["comp"])

        _L = (
            round(
                _dist_pt_reta(_lng[1]["med"][0], _lng[1]["med"][1], _lng[0]["linha"]), 2
            )
            if len(_lng) >= 2
            else 0.15
        )
        _C = round(_ref["comp"], 2)

        if _amb == "Não identificado":
            continue

        _idx = len(df_bloco)
        df_bloco.loc[_idx, ("", "Ambiente")] = _amb
        df_bloco.loc[_idx, ("", "Peça")] = "Bloco Estrutural"
        df_bloco.loc[_idx, ("", "L [m]")] = _L
        df_bloco.loc[_idx, ("", "C [m]")] = _C

        for col in [
            ("", "h [m]"),
            ("", "Concreto [m³]"),
            ("", "Ferragem [KgF]"),
            ("", "Estribo [KgF]"),
            ("Forma em Madeira", "A [m²]"),
        ]:
            df_bloco.loc[_idx, col] = ""

    # ── 3.2.9 Pórticos ───────────────────────────────────────────────
    porticos_data = []
    for t in dados_automaticos.get("textos", []):
        conteudo = t.get("conteudo", "").lower()
        if "pórtico" in conteudo or "portico" in conteudo:
            pos = t.get("posicao", [0, 0])
            amb_raw = _get_amb(pos[0], pos[1])
            amb_clean = re.sub(r"\\[Pp]", " ", amb_raw)
            amb_clean = re.sub(r"\\{.*?\\}|\\.*?;", "", amb_clean)
            amb_clean = re.sub(r"\s+", " ", amb_clean).strip()

            porticos_data.append({"amb": amb_clean, "nome": "Pórtico"})

    contagem_porticos_total = Counter([p["amb"] for p in porticos_data])
    agrupamento_porticos = {}
    for p in porticos_data:
        chave = (p["amb"], p["nome"])
        agrupamento_porticos[chave] = agrupamento_porticos.get(chave, 0) + 1

    for (amb, nome), qtd in sorted(agrupamento_porticos.items()):
        idx = len(df_porticos)
        total_amb = contagem_porticos_total[amb]
        df_porticos.loc[idx, ("", "Ambiente")] = f"{amb} ({total_amb})"
        df_porticos.loc[idx, ("", "Peça")] = f"{nome} ({qtd} un)"

    # ── 3.2.9 Bermas ───────────────────────────────────────────────
    layers_bermas = [
        "ARQ - Desnível Terreno",
        "ARQ - Desnível",
        "ARQ - Guias Calçadas Sarjetas",
    ]
    bermas_raw = []

    for e in dados_automaticos.get("entidades", []):
        if e.get("layer") in layers_bermas and "dados" in e:
            if e["tipo"] == "LINE":
                inicio = e["dados"]["inicio"]
                fim = e["dados"]["fim"]
                cx = (inicio[0] + fim[0]) / 2
                cy = (inicio[1] + fim[1]) / 2
                comp = e["dados"].get("comprimento", 0.0)
            elif e["tipo"] in ["LWPOLYLINE", "POLYLINE"]:
                vertices = e["dados"].get("vertices", [])
                if not vertices:
                    continue
                xs = [p[0] for p in vertices]
                ys = [p[1] for p in vertices]
                cx = sum(xs) / len(vertices)
                cy = sum(ys) / len(vertices)
                comp = e["dados"].get("comprimento", 0.0)
            else:
                continue

            amb = _get_amb(cx, cy)
            bermas_raw.append({"amb": amb, "comp": comp})

    bermas_por_amb = {}
    for item in bermas_raw:
        amb = item["amb"]
        bermas_por_amb[amb] = bermas_por_amb.get(amb, 0.0) + item["comp"]

    for amb, comp_total in sorted(bermas_por_amb.items()):
        idx = len(df_bermas)
        df_bermas.loc[idx, ("", "Ambiente")] = amb
        df_bermas.loc[idx, ("", "Peça")] = "Berma / Guia"
        df_bermas.loc[idx, ("", "C [m]")] = round(comp_total, 2)

    # ── 3.2.9 Recuperação de Viga Existente ───────────────────────────────────────────────

    layer_recuperacao = "EST-VIGAS COBERTURA EXISTENTE"
    recuperacao_raw = []

    for e in dados_automaticos.get("entidades", []):
        if e.get("layer") == layer_recuperacao and "dados" in e:
            if e["tipo"] == "LINE":
                inicio = e["dados"]["inicio"]
                fim = e["dados"]["fim"]
                cx = (inicio[0] + fim[0]) / 2
                cy = (inicio[1] + fim[1]) / 2
                comp = e["dados"].get("comprimento", 0.0)
            elif e["tipo"] in ["LWPOLYLINE", "POLYLINE"]:
                vertices = e["dados"].get("vertices", [])
                if not vertices:
                    continue
                xs = [p[0] for p in vertices]
                ys = [p[1] for p in vertices]
                cx = sum(xs) / len(vertices)
                cy = sum(ys) / len(vertices)
                comp = e["dados"].get("comprimento", 0.0)
            else:
                continue

            amb = _get_amb(cx, cy)
            recuperacao_raw.append({"amb": amb, "comp": comp})

    rec_por_amb = {}
    for item in recuperacao_raw:
        amb = item["amb"]
        rec_por_amb[amb] = rec_por_amb.get(amb, 0.0) + item["comp"]

    for amb, comp_total in sorted(rec_por_amb.items()):
        idx = len(df_recuperacao)
        df_recuperacao.loc[idx, ("", "Ambiente")] = amb
        df_recuperacao.loc[idx, ("", "Peça")] = "Recuperação de Viga Existente"
        df_recuperacao.loc[idx, ("", "C [m]")] = round(comp_total, 2)

    # ── 3.3.1 Pilares metálicos ───────────────────────────────────────────────

    layers_pilares_alvo = ["Estrutural - Pilares", "BAR-PECAS"]
    pilares_met_data = []

    for e in dados_automaticos.get("entidades", []):
        if e.get("layer") in layers_pilares_alvo:
            tipo = e.get("tipo")
            d = e.get("dados", {})
            dim_l, dim_b = 0.0, 0.0

            if tipo == "CIRCLE":
                dim_l = dim_b = d.get("raio", 0) * 2
                pos = d.get("centro", [0, 0])
            elif tipo in ["LWPOLYLINE", "POLYLINE"]:
                v = d.get("vertices", [])
                if len(v) >= 2:
                    xs, ys = [p[0] for p in v], [p[1] for p in v]
                    dim_l, dim_b = max(xs) - min(xs), max(ys) - min(ys)
                    pos = [sum(xs) / len(v), sum(ys) / len(v)]
                else:
                    continue
            else:
                continue

            if dim_l < 0.05:
                continue

            amb_bruto = _get_amb(pos[0], pos[1])
            amb = amb_bruto.replace("{", "").replace("}", "").strip()

            perfil = "A definir"
            for t in dados_automaticos.get("textos", []):
                t_pos = t.get("posicao", [0, 0])
                if math.hypot(pos[0] - t_pos[0], pos[1] - t_pos[1]) < 130:
                    cont = t.get("conteudo", "").upper()
                    if not any(tp in cont for tp in ["m²", "M2", "AREA"]):
                        p_limpo = re.sub(
                            r"\\[^;\\]+;", "", t.get("conteudo", "")
                        ).strip()
                        perfil = p_limpo.replace("{", "").replace("}", "")
                        break

            pilares_met_data.append(
                {"amb": amb, "l": dim_l, "b": dim_b, "perfil": perfil}
            )

    for item in pilares_met_data:
        idx = len(df_pilares_met)
        df_pilares_met.loc[idx, ("", "Ambiente")] = item["amb"]
        df_pilares_met.loc[idx, ("", "Peça")] = "Pilar Metálico"
        df_pilares_met.loc[idx, ("Seção", "L [m]")] = round(item["l"], 3)
        df_pilares_met.loc[idx, ("Seção", "C [m]")] = round(item["b"], 3)
        df_pilares_met.loc[idx, ("", "Perfil")] = item["perfil"]

    def agrupar_elementos(df, col_amb, col_l, col_c):
        df[col_amb] = df[col_amb].replace("", "Não identificado")
        grupos = df.groupby([col_amb, col_l, col_c], dropna=False)

        novas_linhas = []

        for (amb, l, c), grupo in grupos:
            qtd = len(grupo)
            linha = grupo.iloc[0].copy()

            if qtd > 1:
                linha[col_amb] = f"{amb} ({qtd})"
            else:
                linha[col_amb] = amb

            novas_linhas.append(linha)

        return pd.DataFrame(novas_linhas).reset_index(drop=True)

        ocorrencias = {}
        for idx in df.index:
            amb = df.at[idx, col_amb]
            l = df.at[idx, col_l]
            c = df.at[idx, col_c]
            chave = (amb, l, c)
            if contadores[chave] > 1:
                ocorrencias[chave] = ocorrencias.get(chave, 0) + 1
                df.at[idx, col_amb] = f"{amb} ({ocorrencias[chave]})"

    df_pilares = agrupar_elementos(
        df_pilares, ("", "Ambiente"), ("", "L [m]"), ("", "C [m]")
    )
    df_vigas = agrupar_elementos(
        df_vigas, ("", "Ambiente"), ("", "L [m]"), ("", "C [m]")
    )
    df_lajes = agrupar_elementos(
        df_lajes, ("", "Ambiente"), ("", "L [m]"), ("", "C [m]")
    )
    df_contencao = agrupar_elementos(
        df_contencao, ("", "Ambiente"), ("", "L [m]"), ("", "C [m]")
    )
    df_bloco = agrupar_elementos(
        df_bloco, ("", "Ambiente"), ("", "L [m]"), ("", "C [m]")
    )

    def garantir_minimo_linhas(df, n=10):
        if df is None or df.empty:
            return pd.DataFrame(
                [{col: None for col in df.columns} for _ in range(n)],
                columns=df.columns,
            )

        faltantes = n - len(df)
        if faltantes > 0:
            extras = pd.DataFrame(
                [{col: None for col in df.columns} for _ in range(faltantes)],
                columns=df.columns,
            )
            df = pd.concat([df, extras], ignore_index=True)

        return df

    df_viga_baldrame = garantir_minimo_linhas(df_viga_baldrame)
    df_estacas_blocos = garantir_minimo_linhas(df_estacas_blocos)
    df_estacas = garantir_minimo_linhas(df_estacas)
    df_sapatas = garantir_minimo_linhas(df_sapatas)
    df_radier = garantir_minimo_linhas(df_radier)
    df_sapata_corrida = garantir_minimo_linhas(df_sapata_corrida)
    df_pilares = garantir_minimo_linhas(df_pilares)
    df_vigas = garantir_minimo_linhas(df_vigas)
    df_lajes = garantir_minimo_linhas(df_lajes)
    df_contencao = garantir_minimo_linhas(df_contencao)
    df_bloco = garantir_minimo_linhas(df_bloco)
    df_placa = garantir_minimo_linhas(df_placa)
    df_passarelas = garantir_minimo_linhas(df_passarelas)
    df_porticos = garantir_minimo_linhas(df_porticos)
    df_bermas = garantir_minimo_linhas(df_bermas)
    df_recuperacao = garantir_minimo_linhas(df_recuperacao)

    df_pilares_met = garantir_minimo_linhas(df_pilares_met)
    df_vigas_met = garantir_minimo_linhas(df_vigas_met)
    df_lajes_met = garantir_minimo_linhas(df_lajes_met)
    df_passarelas_met = garantir_minimo_linhas(df_passarelas_met)
    df_escadas_met = garantir_minimo_linhas(df_escadas_met)
    df_escadas = garantir_minimo_linhas(df_escadas)
    df_porticos_met = garantir_minimo_linhas(df_porticos_met)
    df_para_balas = garantir_minimo_linhas(df_para_balas)
    df_recuperacao_met = garantir_minimo_linhas(df_recuperacao_met)
    df_madeira = garantir_minimo_linhas(df_madeira)

    ordem_secoes = [
        "3.1 Fundações",
        "3.1.1 Sistema Viga Baldrame",
        "3.1.2 Estacas e Blocos de Coroamento",
        "3.1.3 Estacas",
        "3.1.4 Sapatas Isoladas",
        "3.1.5 Radier",
        "3.1.6 Sistema Sapata Corrida",
        "3.2 Superestrutura em Concreto",
        "3.2.1 Pilares",
        "3.2.2 Vigas",
        "3.2.3 Lajes",
        "3.2.4 Paredes de Contenção",
        "3.2.5 Bloco Estrutural",
        "3.2.6 Placa",
        "3.2.7 Passarelas",
        "3.2.8 Escadas",
        "3.2.9 Pórticos",
        "3.2.10 Bermas",
        "3.2.11 Recuperação de Estruturas em Concreto",
        "3.3 Estruturas Metálicas",
        "3.3.1 Pilares",
        "3.3.2 Vigas",
        "3.3.3 Lajes",
        "3.3.4 Passarelas",
        "3.3.5 Escadas",
        "3.3.6 Pórticos",
        "3.3.7 Para-Balas",
        "3.3.8 Recuperação de Estruturas Metálicas",
        "3.4 Estruturas em Madeira",
    ]

    tabela_map = {
        "3.1.1 Sistema Viga Baldrame": df_viga_baldrame,
        "3.1.2 Estacas e Blocos de Coroamento": df_estacas_blocos,
        "3.1.3 Estacas": df_estacas,
        "3.1.4 Sapatas Isoladas": df_sapatas,
        "3.1.5 Radier": df_radier,
        "3.1.6 Sistema Sapata Corrida": df_sapata_corrida,

        "3.2.1 Pilares": df_pilares,
        "3.2.2 Vigas": df_vigas,
        "3.2.3 Lajes": df_lajes,
        "3.2.4 Paredes de Contenção": df_contencao,
        "3.2.5 Bloco Estrutural": df_bloco,
        "3.2.6 Placa": df_placa,
        "3.2.7 Passarelas": df_passarelas,
        "3.2.8 Escadas": df_escadas,
        "3.2.9 Pórticos": df_porticos,
        "3.2.10 Bermas": df_bermas,
        "3.2.11 Recuperação de Estruturas em Concreto": df_recuperacao,

        "3.3.1 Pilares": df_pilares_met,
        "3.3.2 Vigas": df_vigas_met,
        "3.3.3 Lajes": df_lajes_met,
        "3.3.4 Passarelas": df_passarelas_met,
        "3.3.5 Escadas": df_escadas_met,
        "3.3.6 Pórticos": df_porticos_met,
        "3.3.7 Para-Balas": df_para_balas,
        "3.3.8 Recuperação de Estruturas Metálicas": df_recuperacao_met,

        "3.4 Estruturas em Madeira": df_madeira,
    }

    titulos_grupo = {
        "3.1 Fundações",
        "3.2 Superestrutura em Concreto",
        "3.3 Estruturas Metálicas",
    }

    return tabela_map
