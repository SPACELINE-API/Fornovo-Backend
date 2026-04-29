import pandas as pd
import json
import os
import re
import math
from collections import defaultdict

colunas_alvenarias = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Painéis em Alvenaria", "Peça"),
        ("Painéis em Alvenaria", "C [m]"),
        ("Painéis em Alvenaria", "L [m]"),
        ("Painéis em Alvenaria", "h [m]"),
        ("Painéis em Alvenaria", "Vãos [m²]"),
        ("Painéis em Alvenaria", "A [m²]"),
        ("Painéis em Gesso Acartonado", "Peça"),
        ("Painéis em Gesso Acartonado", "C [m]"),
        ("Painéis em Gesso Acartonado", "L [m]"),
        ("Painéis em Gesso Acartonado", "h [m]"),
        ("Painéis em Gesso Acartonado", "Vãos [m²]"),
        ("Painéis em Gesso Acartonado", "A [m²]"),
        ("Painéis Cobogó ou em Blocos de Vidro", "Peça"),
        ("Painéis Cobogó ou em Blocos de Vidro", "C [m]"),
        ("Painéis Cobogó ou em Blocos de Vidro", "L [m]"),
        ("Painéis Cobogó ou em Blocos de Vidro", "h [m]"),
        ("Painéis Cobogó ou em Blocos de Vidro", "Vãos [m²]"),
        ("Painéis Cobogó ou em Blocos de Vidro", "A [m²]"),
    ]
)

colunas_alvenarias2 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Peça"),
        ("Quantidade", "Verga"),
        ("Quantidade", "C Verga"),
        ("", "L [m]"),
        ("", "Comprimento [m]"),
        ("", "h [m]"),
        ("", "Engasta/o [m]"),
        ("", "Concreto [m³]"),
        ("", "Ferrage [KgF]"),
    ]
)

colunas_alvenarias3 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Guias", "Local"),
        ("Guias", "L [m]"),
        ("Guias", "C [m]"),
        ("Guias", "h [m]"),
        ("Guias", "Concreto [m³]"),
        ("Calçadas e passeios", "Local"),
        ("Calçadas e passeios", "L [m]"),
        ("Calçadas e passeios", "C [m]"),
        ("Calçadas e passeios", "e [m]"),
        ("Calçadas e passeios", "h [m]"),
        ("Calçadas e passeios", "A [m²]"),
        ("Calçadas e passeios", "Concreto [m³]"),
    ]
)

colunas_alvenarias4 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
        ("Dimensões", "C Proj [m]"),
        ("Dimensões", "C Real [m]"),
        ("Dimensões", "L [m]"),
        ("Dimensões", "h [m]"),
        ("Dimensões", "i [%]"),
        ("Piso", "e [m]"),
        ("Piso", "A [m²]"),
        ("Piso", "Concreto [m³]"),
        ("Parede de contenção", "L [m]"),
        ("Parede de contenção", "h [m]"),
        ("Parede de contenção", "C [m]"),
        ("Parede de contenção", "A [m²]"),
        ("Parede de contenção", "Concreto [m³]"),
        ("Guia Balizamento", "L [m]"),
        ("Guia Balizamento", "h [m]"),
        ("Armação", "Ferragem [KgF]"),
        ("Armação", "Estribo [KgF]"),
        ("Forma em madeira", "h [m]"),
        ("Forma em madeira", "C [m]"),
        ("Forma em madeira", "A [m²]"),
    ]
)

colunas_alvenarias5 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
    ]
)

colunas_alvenarias6 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
        ("", "Peça"),
        ("Material de fechamento", "C [m]"),
        ("Material de fechamento", "h [m]"),
        ("Material de fechamento", "A [m²]"),
        ("Mourões", "Qnt"),
        ("Mourões", "C [m]"),
        ("Mourões", "h [m]"),
        ("Esticador", "Qnt"),
        ("Esticador", "C [m]"),
        ("Esticador", "h [m]"),
        ("Concertina", "C [m]"),
    ]
)

colunas_alvenarias7 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
        ("Apicoamento", "C [m]"),
        ("Apicoamento", "h [m]"),
        ("Apicoamento", "A [m²]"),
        ("Chapisco", "C [m]"),
        ("Chapisco", "h [m]"),
        ("Chapisco", "A [m²]"),
        ("Esboço para pintura", "C [m]"),
        ("Esboço para pintura", "h [m]"),
        ("Esboço para pintura", "A [m²]"),
        ("Esboço para Revestimento", "C [m]"),
        ("Esboço para Revestimento", "h [m]"),
        ("Esboço para Revestimento", "A [m²]"),
    ]
)

colunas_alvenarias8 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
        ("Lastros", "C [m]"),
        ("Lastros", "L [m]"),
        ("Lastros", "e [m]"),
        ("Lastros", "V [m³]"),
        ("Contrapisos", "C [m]"),
        ("Contrapisos", "L [m]"),
        ("Contrapisos", "e [m]"),
        ("Contrapisos", "V [m³]"),
        ("Contrapisos", "Ferragem [KgF]"),
        ("Juntas de Dilatação", "C [m]"),
        ("Juntas de Dilatação", "L [m]"),
        ("Juntas de Dilatação", "h [m]"),
    ]
)

colunas_alvenarias9 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
        ("Juntas de Dilatação", "C [m]"),
        ("Juntas de Dilatação", "L [m]"),
        ("Juntas de Dilatação", "h [m]"),
    ]
)

colunas_alvenarias10 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Local"),
        ("Estruturas", "Peça"),
        ("Estruturas", "Qtd"),
        ("Estruturas", "C"),
        ("Estruturas", "L"),
        ("Estruturas", "h"),
        ("Estruturas", "A_tot"),
        ("Pisos", "C"),
        ("Pisos", "L"),
        ("Pisos", "h"),
        ("Pisos", "Per"),
        ("Pisos", "A_tot"),
        ("Paredes", "C"),
        ("Paredes", "L"),
        ("Paredes", "h"),
        ("Paredes", "Per"),
        ("Paredes", "A_tot"),
    ]
)

TERMOS_IGNORAR = [
    "CABO",
    "COBRE",
    "SPDA",
    "CONDUTOR",
    "BARRA",
    "ALUMÍNIO",
    "S=",
    "NÚ",
    "TERRA",
    "MALHA",
    "SOLDA",
    "HASTE",
    "CONECTOR",
]


def limpar_texto(txt):
    txt = re.sub(r"XQC;|\\P|\\C|#|{|}|\d+.*", "", txt)
    txt = txt.replace(";", "").replace("-", "").strip()
    if any(termo in txt.upper() for termo in TERMOS_IGNORAR):
        return None
    return txt if txt else None


def alvenarias(dados_manuais, dados_automaticos):
    df = pd.DataFrame(columns=colunas_alvenarias)
    df2 = pd.DataFrame(columns=colunas_alvenarias2)
    df3 = pd.DataFrame(columns=colunas_alvenarias3)
    df4 = pd.DataFrame(columns=colunas_alvenarias4)
    df5 = pd.DataFrame(columns=colunas_alvenarias5)
    df6 = pd.DataFrame(columns=colunas_alvenarias6)
    df7 = pd.DataFrame(columns=colunas_alvenarias7)
    df8 = pd.DataFrame(columns=colunas_alvenarias8)
    df9 = pd.DataFrame(columns=colunas_alvenarias9)
    df10 = pd.DataFrame(columns=colunas_alvenarias10)

    ambientes_ref = []

    for t in dados_automaticos.get("textos", []):
        cont = t.get("conteudo", "").upper()

        if "M²" in cont or "M2" in cont:
            pd_match = re.search(r"PD\s*[:=]\s*(\d+[.,]\d+)", cont)
            h = float(pd_match.group(1).replace(",", ".")) if pd_match else 2.70
            nome = limpar_texto(cont)

            if nome and t.get("posicao"):
                ambientes_ref.append({"nome": nome, "pos": t["posicao"], "h": h})

    def _get_amb_sp(cx, cy, threshold=600):
        if not ambientes_ref:
            return None

        best = min(
            ambientes_ref,
            key=lambda a: math.hypot(cx - a["pos"][0], cy - a["pos"][1]),
        )

        dist = math.hypot(cx - best["pos"][0], cy - best["pos"][1])

        return best if dist <= threshold else None

    consolidado = defaultdict(
        lambda: defaultdict(lambda: {"c": 0.0, "l": 0.15, "h": 2.70})
    )

    consolidado_vaos = defaultdict(
        lambda: defaultdict(lambda: {"qtd": 0, "vao": 0.0, "l": 0.15})
    )

    consolidado_df3 = defaultdict(
        lambda: {
            "Guias": {"c": 0.0},
            "Calcadas": {"area": 0.0},
        }
    )

    # ── Painéis, gessos ───────────────

    for e in dados_automaticos.get("entidades", []):
        layer = e.get("layer", "").upper()
        categoria = None

        if any(k in layer for k in ["DRY-WALL", "DRYWALL", "GESSO", "DIVISORIA"]):
            categoria = "Painéis em Gesso Acartonado"

        elif any(k in layer for k in ["COBOGO", "VIDRO", "VAZADO"]):
            categoria = "Painéis Cobogó ou em Blocos de Vidro"

        elif any(k in layer for k in ["ALVENARIA", "PAREDE", "ALV"]):
            if not any(k in layer for k in ["ELE-", "SPDA", "CABO", "COBRE"]):
                categoria = "Painéis em Alvenaria"

        tipo = e.get("tipo")
        d = e.get("dados", {})

        if tipo not in ["LINE", "LWPOLYLINE", "POLYLINE"]:
            continue

        comp = d.get("comprimento", 0.0)

        if comp < 0.10:
            continue

        if tipo == "LINE":
            cx = (d["inicio"][0] + d["fim"][0]) / 2
            cy = (d["inicio"][1] + d["fim"][1]) / 2
        else:
            v = d.get("vertices", [])

            if not v:
                continue

            cx = sum(p[0] for p in v) / len(v)
            cy = sum(p[1] for p in v) / len(v)

        amb_info = _get_amb_sp(cx, cy)
        nome_amb = amb_info["nome"] if amb_info else "ÁREA EXTERNA"
        h_amb = amb_info["h"] if amb_info else 2.70

        if categoria:
            consolidado[nome_amb][categoria]["c"] += comp
            consolidado[nome_amb][categoria]["h"] = h_amb

            l_match = re.search(r"(\d+)\s*CM", layer)
            if l_match:
                consolidado[nome_amb][categoria]["l"] = float(l_match.group(1)) / 100

    # ── Guias, calçadas e passeios ───────────────
    def limpar_nome(txt):
        txt = re.sub(r"XQC;|\\P|\\C|#|{|}|\d+.*", "", txt)
        txt = txt.replace(";", "").replace("-", "").strip()
        if (
            any(k in txt.upper() for k in TERMOS_IGNORAR)
            or len(txt) < 3
            or "M²" in txt.upper()
            or "M2" in txt.upper()
        ):
            return "Não identificado"
        return txt if txt else "Não identificado"

    for e in dados_automaticos.get("entidades", []):
        layer = e.get("layer", "").upper()
        tipo = e.get("tipo")
        d = e.get("dados", {})
        if tipo not in ["LINE", "LWPOLYLINE", "POLYLINE", "HATCH"]:
            continue
        if tipo == "LINE":
            cx = (d["inicio"][0] + d["fim"][0]) / 2
            cy = (d["inicio"][1] + d["fim"][1]) / 2
        else:
            v = d.get("vertices", [])
            if not v:
                continue
            cx = sum(p[0] for p in v) / len(v)
            cy = sum(p[1] for p in v) / len(v)

        amb_info = _get_amb_sp(cx, cy)
        nome_limpo = amb_info["nome"] if amb_info else "Não identificado"
        nome_limpo = limpar_nome(nome_limpo)

        if any(
            k in layer
            for k in [
                "GUIA",
                "MEIO-FIO",
                "BORDO",
                "SARJETA",
                "CALCADA",
                "CALÇADA",
                "PASSEIO",
                "PAVIMENTO",
                "PISO",
            ]
        ):
            amb = f"EXT - {nome_limpo}"
            if "comprimento" in d:
                comp = d["comprimento"]
                if any(k in layer for k in ["GUIA", "MEIO-FIO", "BORDO", "SARJETA"]):
                    consolidado_df3[amb]["Guias"]["c"] += (
                        comp if comp < 500 else comp / 100
                    )
            if any(
                k in layer
                for k in ["CALCADA", "CALÇADA", "PASSEIO", "PAVIMENTO", "PISO"]
            ):
                area_raw = d.get("area", 0.0)
                consolidado_df3[amb]["Calcadas"]["area"] += (
                    area_raw if area_raw < 10000 else area_raw / 10000
                )

    for amb, categorias_data in consolidado.items():
        idx = len(df)
        df.loc[idx, ("", "Ambiente")] = amb

        for cat, info in categorias_data.items():
            c_final = info["c"]

            if c_final > 800:
                c_final /= 100

            df.loc[idx, (cat, "Peça")] = (
                "Gesso acartonado" if cat == "Painéis em Gesso Acartonado" else "Parede"
            )

            df.loc[idx, (cat, "C [m]")] = round(c_final, 2)
            df.loc[idx, (cat, "L [m]")] = info["l"]
            df.loc[idx, (cat, "h [m]")] = info["h"]
            df.loc[idx, (cat, "Vãos [m²]")] = 0.0
            df.loc[idx, (cat, "A [m²]")] = round(c_final * info["h"], 2)

    for amb, vaos in consolidado_vaos.items():
        for peca_nome, info in vaos.items():
            idx = len(df2)

            comp_verga = info["vao"]
            concreto = 0.0
            ferro = 0.0

            df2.loc[idx, ("", "Ambiente")] = amb
            df2.loc[idx, ("", "Peça")] = peca_nome
            df2.loc[idx, ("Quantidade", "Verga")] = info["qtd"]
            df2.loc[idx, ("Quantidade", "C Verga")] = (
                info["qtd"] if "Janela" in peca_nome else 0
            )
            df2.loc[idx, ("", "L [m]")] = info["l"]
            df2.loc[idx, ("", "Comprimento [m]")] = round(comp_verga, 2)
            df2.loc[idx, ("", "h [m]")] = None
            df2.loc[idx, ("", "Engasta/o [m]")] = None
            df2.loc[idx, ("", "Concreto [m³]")] = concreto
            df2.loc[idx, ("", "Ferrage [KgF]")] = ferro

    for amb, categorias in consolidado_df3.items():
        idx = len(df3)
        df3.loc[idx, ("", "Ambiente")] = amb
        if categorias["Guias"]["c"] > 0:
            c_guia = categorias["Guias"]["c"]
            df3.loc[idx, ("Guias", "Local")] = "Perímetro"
            df3.loc[idx, ("Guias", "L [m]")] = 0.15
            df3.loc[idx, ("Guias", "C [m]")] = round(c_guia, 2)
            df3.loc[idx, ("Guias", "h [m]")] = 0.30
        if categorias["Calcadas"]["area"] > 0:
            a_calc = categorias["Calcadas"]["area"]
            df3.loc[idx, ("Calçadas e passeios", "Local")] = "Externo"
            df3.loc[idx, ("Calçadas e passeios", "e [m]")] = 0.10
            df3.loc[idx, ("Calçadas e passeios", "A [m²]")] = round(a_calc, 2)
            df3.loc[idx, ("Calçadas e passeios", "Concreto [m³]")] = round(
                a_calc * 0.10, 4
            )

    # ── df4 — Pisos (Estrutural - Lajes) e Paredes de Contenção (ARQ - Alvenaria (-)) ──

    def _rpt4(pt):
        return (round(pt[0], 2), round(pt[1], 2))

    def _ang4(v):
        dx = v["dados"]["fim"][0] - v["dados"]["inicio"][0]
        dy = v["dados"]["fim"][1] - v["dados"]["inicio"][1]
        return math.degrees(math.atan2(dy, dx)) % 180

    def _med4(v):
        return (
            (v["dados"]["inicio"][0] + v["dados"]["fim"][0]) / 2,
            (v["dados"]["inicio"][1] + v["dados"]["fim"][1]) / 2,
        )

    def _dist_reta4(px, py, v):
        sx, sy = v["dados"]["inicio"][:2]
        fx, fy = v["dados"]["fim"][:2]
        dx, dy = fx - sx, fy - sy
        den = dx * dx + dy * dy
        if den < 1e-12:
            return math.dist([px, py], [sx, sy])
        t = ((px - sx) * dx + (py - sy) * dy) / den
        return math.dist([px, py], [sx + t * dx, sy + t * dy])

    def _proj4(v, ux, uy):
        t0 = v["dados"]["inicio"][0] * ux + v["dados"]["inicio"][1] * uy
        t1 = v["dados"]["fim"][0] * ux + v["dados"]["fim"][1] * uy
        return (min(t0, t1), max(t0, t1))

    def _sobrepoem4(a, b, tol=0.05):
        return a[1] >= b[0] + tol and b[1] >= a[0] + tol

    def _nome_amb4(cx, cy):
        info = _get_amb_sp(cx, cy)
        if info:
            return info["nome"]
        return "Não identificado"

    _TOL_ANG = 2.0
    _TOL_DIST = 0.5
    _TOL_OVL = 0.05

    # Pisos: agrupamento por componentes conectados (Estrutural - Lajes)
    _piso_lines = [
        e
        for e in dados_automaticos.get("entidades", [])
        if e.get("layer") == "Estrutural - Lajes"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e.get("dados", {})
        and "fim" in e.get("dados", {})
    ]

    _adj4 = {}
    _edges4 = []
    for _i, _ln in enumerate(_piso_lines):
        _p1 = _rpt4(_ln["dados"]["inicio"])
        _p2 = _rpt4(_ln["dados"]["fim"])
        _edges4.append((_i, _p1, _p2))
        _adj4.setdefault(_p1, []).append(_i)
        _adj4.setdefault(_p2, []).append(_i)

    _visited4 = set()
    _comps4 = []
    for _i in range(len(_piso_lines)):
        if _i in _visited4:
            continue
        _comp, _q = [], [_i]
        _visited4.add(_i)
        while _q:
            _cur = _q.pop(0)
            _comp.append(_cur)
            if _cur < len(_edges4):
                for _nb in _adj4.get(_edges4[_cur][1], []) + _adj4.get(
                    _edges4[_cur][2], []
                ):
                    if _nb not in _visited4:
                        _visited4.add(_nb)
                        _q.append(_nb)
        _comps4.append(_comp)

    for _comp in _comps4:
        if len(_comp) < 2:
            continue
        _pts_x = [
            c
            for i in _comp
            for c in [
                _piso_lines[i]["dados"]["inicio"][0],
                _piso_lines[i]["dados"]["fim"][0],
            ]
        ]
        _pts_y = [
            c
            for i in _comp
            for c in [
                _piso_lines[i]["dados"]["inicio"][1],
                _piso_lines[i]["dados"]["fim"][1],
            ]
        ]
        _cx4 = sum(_pts_x) / len(_pts_x)
        _cy4 = sum(_pts_y) / len(_pts_y)
        _comp_vals = sorted(
            [round(_piso_lines[i]["dados"].get("comprimento", 0), 3) for i in _comp]
        )
        _L4 = _comp_vals[0] if _comp_vals else None
        _C4 = _comp_vals[-1] if _comp_vals else None
        if not _L4 or not _C4 or _L4 <= 0 or _C4 <= 0:
            continue
        _A4 = round(_L4 * _C4, 4)
        _amb4 = _nome_amb4(_cx4, _cy4)
        _idx4 = len(df4)
        df4.loc[_idx4, ("", "Ambiente")] = _amb4
        df4.loc[_idx4, ("", "Local")] = "Piso"
        df4.loc[_idx4, ("Dimensões", "C Proj [m]")] = _C4
        df4.loc[_idx4, ("Dimensões", "C Real [m]")] = _C4
        df4.loc[_idx4, ("Dimensões", "L [m]")] = _L4
        df4.loc[_idx4, ("Piso", "A [m²]")] = _A4
        df4.loc[_idx4, ("Forma em madeira", "C [m]")] = _C4
        df4.loc[_idx4, ("Forma em madeira", "A [m²]")] = _A4

    # Paredes de contenção: agrupamento por alinhamento (ARQ - Alvenaria (-))
    _cont_lines = [
        e
        for e in dados_automaticos.get("entidades", [])
        if e.get("layer") == "ARQ - Alvenaria (-)"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e.get("dados", {})
        and "fim" in e.get("dados", {})
        and e["dados"].get("comprimento", 0) >= 0.5
    ]

    _meta_ct = [
        {
            "idx": i,
            "linha": v,
            "ang": _ang4(v),
            "med": _med4(v),
            "comp": v["dados"].get("comprimento", 0),
        }
        for i, v in enumerate(_cont_lines)
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
        _proj_s = _proj4(_semente["linha"], _ux, _uy)
        for _cand in _meta_ct:
            if _cand["idx"] in _used_ct:
                continue
            _da = min(abs(_cand["ang"] - _ang_s), 180 - abs(_cand["ang"] - _ang_s))
            if _da > _TOL_ANG:
                continue
            _px, _py = _cand["med"]
            if _dist_reta4(_px, _py, _semente["linha"]) > _TOL_DIST:
                continue
            if not _sobrepoem4(_proj_s, _proj4(_cand["linha"], _ux, _uy), _TOL_OVL):
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
        _cx4 = sum(_pts_x) / len(_pts_x)
        _cy4 = sum(_pts_y) / len(_pts_y)
        _ref = max(_grp, key=lambda m: m["comp"])
        _C4 = round(_ref["comp"], 3)
        _longas = sorted(_grp, key=lambda m: -m["comp"])
        _L4 = (
            round(_dist_reta4(*_longas[1]["med"], _longas[0]["linha"]), 3)
            if len(_longas) >= 2
            else ""
        )
        if _C4 < 0.05:
            continue
        _A4 = round(_L4 * _C4, 4) if _L4 else ""
        _amb4 = _nome_amb4(_cx4, _cy4)
        _idx4 = len(df4)
        df4.loc[_idx4, ("", "Ambiente")] = _amb4
        df4.loc[_idx4, ("", "Local")] = "Parede de Contenção"
        df4.loc[_idx4, ("Parede de contenção", "L [m]")] = _L4
        df4.loc[_idx4, ("Parede de contenção", "C [m]")] = _C4
        df4.loc[_idx4, ("Parede de contenção", "A [m²]")] = _A4

    # ── df6: Cercamentos e Grades (ARQ - Cercamentos, ARQ - Grades) ──────────
    def _ang6(v):
        d = v.get("dados", {})
        if "fim" in d and "inicio" in d:
            dx = d["fim"][0] - d["inicio"][0]
            dy = d["fim"][1] - d["inicio"][1]
            return math.degrees(math.atan2(dy, dx)) % 180
        return 0.0

    def _med6(v):
        d = v.get("dados", {})
        if "vertices" in d and d["vertices"]:
            vs = d["vertices"]
            return (sum(p[0] for p in vs) / len(vs), sum(p[1] for p in vs) / len(vs))
        if "inicio" in d and "fim" in d:
            return (
                (d["inicio"][0] + d["fim"][0]) / 2,
                (d["inicio"][1] + d["fim"][1]) / 2,
            )
        return (0.0, 0.0)

    def _comp6(v):
        d = v.get("dados", {})
        if "comprimento" in d:
            return d["comprimento"]
        if "vertices" in d and len(d["vertices"]) >= 2:
            vs = d["vertices"]
            return sum(math.dist(vs[i][:2], vs[i + 1][:2]) for i in range(len(vs) - 1))
        return 0.0

    def _proj6(v, ux, uy):
        d = v.get("dados", {})
        if "inicio" in d and "fim" in d:
            t0 = d["inicio"][0] * ux + d["inicio"][1] * uy
            t1 = d["fim"][0] * ux + d["fim"][1] * uy
            return (min(t0, t1), max(t0, t1))
        if "vertices" in d and d["vertices"]:
            ts = [p[0] * ux + p[1] * uy for p in d["vertices"]]
            return (min(ts), max(ts))
        return (0.0, 0.0)

    def _dist6(px, py, v):
        d = v.get("dados", {})
        if "inicio" in d and "fim" in d:
            sx, sy = d["inicio"][:2]
            fx, fy = d["fim"][:2]
            dx, dy = fx - sx, fy - sy
            den = dx * dx + dy * dy
            if den < 1e-12:
                return math.dist([px, py], [sx, sy])
            t = ((px - sx) * dx + (py - sy) * dy) / den
            return math.dist([px, py], [sx + t * dx, sy + t * dy])
        return float("inf")

    def _ovlp6(a, b, tol=0.05):
        return a[1] >= b[0] + tol and b[1] >= a[0] + tol

    def _nome6(cx, cy):
        info = _get_amb_sp(cx, cy)
        return info["nome"] if info else "Não identificado"

    _TOL6_ANG = 2.0
    _TOL6_DIST = 0.5

    _linhas_df6 = []

    for _layer6, _peca6, _local6 in [
        ("ARQ - Cercamentos", "Cerca/Tela", "Perímetro"),
        ("ARQ - Grades", "Grade", "Perímetro"),
    ]:
        _ents6 = [
            e
            for e in dados_automaticos.get("entidades", [])
            if e.get("layer") == _layer6
            and e.get("tipo") in ["LINE", "LWPOLYLINE"]
            and "dados" in e
            and _comp6(e) >= 0.5
        ]

        _meta6 = [
            {"idx": i, "linha": v, "ang": _ang6(v), "med": _med6(v), "comp": _comp6(v)}
            for i, v in enumerate(_ents6)
        ]
        _meta6.sort(key=lambda m: -m["comp"])

        _used6 = set()
        _grupos6 = []
        for _s in _meta6:
            if _s["idx"] in _used6:
                continue
            _grp = [_s]
            _used6.add(_s["idx"])
            _as = _s["ang"]
            _rs = math.radians(_as)
            _ux, _uy = math.cos(_rs), math.sin(_rs)
            _ps = _proj6(_s["linha"], _ux, _uy)
            for _c in _meta6:
                if _c["idx"] in _used6:
                    continue
                _da = min(abs(_c["ang"] - _as), 180 - abs(_c["ang"] - _as))
                if _da > _TOL6_ANG:
                    continue
                if _dist6(*_c["med"], _s["linha"]) > _TOL6_DIST:
                    continue
                if not _ovlp6(_ps, _proj6(_c["linha"], _ux, _uy)):
                    continue
                _grp.append(_c)
                _used6.add(_c["idx"])
            _grupos6.append(_grp)

        for _grp in _grupos6:
            _meds = [m["med"] for m in _grp]
            _cx = sum(p[0] for p in _meds) / len(_meds)
            _cy = sum(p[1] for p in _meds) / len(_meds)
            _ref = max(_grp, key=lambda m: m["comp"])
            _C6 = round(_ref["comp"], 3)
            if _C6 < 0.05:
                continue
            _longas = sorted(_grp, key=lambda m: -m["comp"])
            _h6 = ""
            if len(_longas) >= 2:
                _h6v = round(_dist6(*_longas[1]["med"], _longas[0]["linha"]), 3)
                _h6 = _h6v if _h6v and _h6v >= 0.01 else ""
            _A6 = round(_h6 * _C6, 4) if _h6 else ""
            _amb6 = _nome6(_cx, _cy)
            _linhas_df6.append(
                {
                    "amb": _amb6,
                    "local": _local6,
                    "peca": _peca6,
                    "C": _C6,
                    "h": _h6,
                    "A": _A6,
                }
            )

    # Consolidar linhas idênticas em df6 e nomear com (n)
    _contagem_df6 = {}
    for _r in _linhas_df6:
        _k = (_r["amb"], _r["local"], _r["peca"], _r["C"], _r["h"])
        _contagem_df6[_k] = _contagem_df6.get(_k, 0) + 1

    _vistos_df6 = set()
    for _r in _linhas_df6:
        _k = (_r["amb"], _r["local"], _r["peca"], _r["C"], _r["h"])
        if _k in _vistos_df6:
            continue
        _vistos_df6.add(_k)
        _n = _contagem_df6[_k]
        _nome_final = f"{_r['amb']} ({_n})" if _n > 1 else _r["amb"]
        _idx6 = len(df6)
        df6.loc[_idx6, ("", "Ambiente")] = _nome_final
        df6.loc[_idx6, ("", "Local")] = _r["local"]
        df6.loc[_idx6, ("", "Peça")] = _r["peca"]
        df6.loc[_idx6, ("Material de fechamento", "C [m]")] = _r["C"]
        df6.loc[_idx6, ("Material de fechamento", "h [m]")] = _r["h"]
        df6.loc[_idx6, ("Material de fechamento", "A [m²]")] = _r["A"]
        df6.loc[_idx6, ("Mourões", "Qnt")] = ""
        df6.loc[_idx6, ("Mourões", "C [m]")] = ""
        df6.loc[_idx6, ("Mourões", "h [m]")] = ""
        df6.loc[_idx6, ("Esticador", "Qnt")] = ""
        df6.loc[_idx6, ("Esticador", "C [m]")] = ""
        df6.loc[_idx6, ("Esticador", "h [m]")] = ""
        df6.loc[_idx6, ("Concertina", "C [m]")] = ""

    # Consolidar linhas idênticas em df4 e nomear com (n)
    _linhas_df4 = [{col: df4.at[idx, col] for col in df4.columns} for idx in df4.index]

    _chave_df4 = lambda r: (
        str(r.get(("", "Ambiente"), "")),
        str(r.get(("", "Local"), "")),
        str(r.get(("Dimensões", "C Proj [m]"), "")),
        str(r.get(("Dimensões", "L [m]"), "")),
        str(r.get(("Parede de contenção", "C [m]"), "")),
        str(r.get(("Parede de contenção", "L [m]"), "")),
    )

    _contagem_df4 = {}
    for _r in _linhas_df4:
        _k = _chave_df4(_r)
        _contagem_df4[_k] = _contagem_df4.get(_k, 0) + 1

    df4_consolidado = pd.DataFrame(columns=colunas_alvenarias4)
    _vistos_df4 = set()
    for _r in _linhas_df4:
        _k = _chave_df4(_r)
        if _k in _vistos_df4:
            continue
        _vistos_df4.add(_k)
        _n = _contagem_df4[_k]
        _idx4 = len(df4_consolidado)
        for _col in df4.columns:
            df4_consolidado.loc[_idx4, _col] = _r[_col]
        _amb_orig = str(_r.get(("", "Ambiente"), ""))
        df4_consolidado.loc[_idx4, ("", "Ambiente")] = (
            f"{_amb_orig} ({_n})" if _n > 1 else _amb_orig
        )
    df4 = df4_consolidado

    # ── df10: Resumo consolidado de Estruturas, Pisos e Paredes ─────────────
    # Estruturas: pilares e vigas de Estrutural - Pilares e Estrutural - Vigas
    def _rpt10(pt):
        return (round(pt[0], 2), round(pt[1], 2))

    def _ang10(v):
        d = v["dados"]
        dx = d["fim"][0] - d["inicio"][0]
        dy = d["fim"][1] - d["inicio"][1]
        return math.degrees(math.atan2(dy, dx)) % 180

    def _med10(v):
        d = v["dados"]
        return ((d["inicio"][0] + d["fim"][0]) / 2, (d["inicio"][1] + d["fim"][1]) / 2)

    def _dist10(px, py, v):
        d = v["dados"]
        sx, sy = d["inicio"][:2]
        fx, fy = d["fim"][:2]
        dx, dy = fx - sx, fy - sy
        den = dx * dx + dy * dy
        if den < 1e-12:
            return math.dist([px, py], [sx, sy])
        t = ((px - sx) * dx + (py - sy) * dy) / den
        return math.dist([px, py], [sx + t * dx, sy + t * dy])

    def _proj10(v, ux, uy):
        d = v["dados"]
        t0 = d["inicio"][0] * ux + d["inicio"][1] * uy
        t1 = d["fim"][0] * ux + d["fim"][1] * uy
        return (min(t0, t1), max(t0, t1))

    def _ovlp10(a, b, tol=0.05):
        return a[1] >= b[0] + tol and b[1] >= a[0] + tol

    def _nome10(cx, cy):
        info = _get_amb_sp(cx, cy)
        return info["nome"] if info else "Não identificado"

    _TOL10 = 2.0
    _TOL10D = 0.5

    entidades10 = dados_automaticos.get("entidades", [])

    # ── Pilares ──
    _pil_lines = [
        e
        for e in entidades10
        if e.get("layer") == "Estrutural - Pilares"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
    ]
    _adj10 = {}
    _edges10 = []
    for _i, _ln in enumerate(_pil_lines):
        _p1 = _rpt10(_ln["dados"]["inicio"])
        _p2 = _rpt10(_ln["dados"]["fim"])
        _edges10.append((_i, _p1, _p2))
        _adj10.setdefault(_p1, []).append(_i)
        _adj10.setdefault(_p2, []).append(_i)
    _vis10 = set()
    _cgrps10 = []
    for _i in range(len(_pil_lines)):
        if _i in _vis10:
            continue
        _comp, _q = [], [_i]
        _vis10.add(_i)
        while _q:
            _cur = _q.pop(0)
            _comp.append(_cur)
            if _cur < len(_edges10):
                for _nb in _adj10.get(_edges10[_cur][1], []) + _adj10.get(
                    _edges10[_cur][2], []
                ):
                    if _nb not in _vis10:
                        _vis10.add(_nb)
                        _q.append(_nb)
        _cgrps10.append(_comp)

    _pil_rows = []
    for _comp in _cgrps10:
        if len(_comp) < 2:
            continue
        _vals = sorted(
            [round(_pil_lines[i]["dados"].get("comprimento", 0), 3) for i in _comp]
        )
        _pts_x = [
            c
            for i in _comp
            for c in [
                _pil_lines[i]["dados"]["inicio"][0],
                _pil_lines[i]["dados"]["fim"][0],
            ]
        ]
        _pts_y = [
            c
            for i in _comp
            for c in [
                _pil_lines[i]["dados"]["inicio"][1],
                _pil_lines[i]["dados"]["fim"][1],
            ]
        ]
        _cx = sum(_pts_x) / len(_pts_x)
        _cy = sum(_pts_y) / len(_pts_y)
        _L = _vals[0]
        _C = _vals[-1]
        if not _L or not _C or _L <= 0:
            continue
        _A = round(_L * _C, 4)
        _pil_rows.append(
            {"amb": _nome10(_cx, _cy), "peca": "Pilar", "C": _C, "L": _L, "A": _A}
        )

    # consolidar pilares idênticos
    _cnt_pil = {}
    for r in _pil_rows:
        k = (r["amb"], r["C"], r["L"])
        _cnt_pil[k] = _cnt_pil.get(k, 0) + 1
    _seen_pil = set()
    for r in _pil_rows:
        k = (r["amb"], r["C"], r["L"])
        if k in _seen_pil:
            continue
        _seen_pil.add(k)
        _n = _cnt_pil[k]
        _idx = len(df10)
        df10.loc[_idx, ("", "Ambiente")] = f"{r['amb']} ({_n})" if _n > 1 else r["amb"]
        df10.loc[_idx, ("", "Local")] = "Estrutura"
        df10.loc[_idx, ("Estruturas", "Peça")] = r["peca"]
        df10.loc[_idx, ("Estruturas", "Qtd")] = _n
        df10.loc[_idx, ("Estruturas", "C")] = r["C"]
        df10.loc[_idx, ("Estruturas", "L")] = r["L"]
        df10.loc[_idx, ("Estruturas", "h")] = ""
        df10.loc[_idx, ("Estruturas", "A_tot")] = round(r["A"] * _n, 4)

    # ── Vigas ──
    _vig_lines = [
        e
        for e in entidades10
        if e.get("layer") == "Estrutural - Vigas"
        and e.get("tipo") == "LINE"
        and "dados" in e
        and "inicio" in e["dados"]
        and "fim" in e["dados"]
    ]
    _meta_v10 = [
        {
            "idx": i,
            "linha": v,
            "ang": _ang10(v),
            "med": _med10(v),
            "comp": v["dados"].get("comprimento", 0),
        }
        for i, v in enumerate(_vig_lines)
    ]
    _meta_v10.sort(key=lambda m: -m["comp"])
    _used_v10 = set()
    _grps_v10 = []
    for _s in _meta_v10:
        if _s["idx"] in _used_v10:
            continue
        _grp = [_s]
        _used_v10.add(_s["idx"])
        _as = _s["ang"]
        _rs = math.radians(_as)
        _ux, _uy = math.cos(_rs), math.sin(_rs)
        _ps = _proj10(_s["linha"], _ux, _uy)
        for _c in _meta_v10:
            if _c["idx"] in _used_v10:
                continue
            _da = min(abs(_c["ang"] - _as), 180 - abs(_c["ang"] - _as))
            if _da > _TOL10:
                continue
            if _dist10(*_c["med"], _s["linha"]) > _TOL10D:
                continue
            if not _ovlp10(_ps, _proj10(_c["linha"], _ux, _uy)):
                continue
            _grp.append(_c)
            _used_v10.add(_c["idx"])
        _grps_v10.append(_grp)

    _vig_rows = []
    for _grp in _grps_v10:
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
        _ref = max(_grp, key=lambda m: m["comp"])
        _C = round(_ref["comp"], 3)
        _longas = sorted(_grp, key=lambda m: -m["comp"])
        _L = (
            round(_dist10(*_longas[1]["med"], _longas[0]["linha"]), 3)
            if len(_longas) >= 2
            else ""
        )
        if _C < 0.05:
            continue
        _A = round(_L * _C, 4) if _L else ""
        _vig_rows.append(
            {"amb": _nome10(_cx, _cy), "peca": "Viga", "C": _C, "L": _L, "A": _A}
        )

    _cnt_vig = {}
    for r in _vig_rows:
        k = (r["amb"], r["C"], r["L"])
        _cnt_vig[k] = _cnt_vig.get(k, 0) + 1
    _seen_vig = set()
    for r in _vig_rows:
        k = (r["amb"], r["C"], r["L"])
        if k in _seen_vig:
            continue
        _seen_vig.add(k)
        _n = _cnt_vig[k]
        _idx = len(df10)
        df10.loc[_idx, ("", "Ambiente")] = f"{r['amb']} ({_n})" if _n > 1 else r["amb"]
        df10.loc[_idx, ("Estruturas", "Peça")] = r["peca"]
        df10.loc[_idx, ("Estruturas", "Qtd")] = _n
        df10.loc[_idx, ("Estruturas", "C")] = r["C"]
        df10.loc[_idx, ("Estruturas", "L")] = r["L"]
        df10.loc[_idx, ("Estruturas", "h")] = ""
        df10.loc[_idx, ("Estruturas", "A_tot")] = (
            round(r["A"] * _n, 4) if r["A"] else ""
        )

    # ── Paredes (consolidado dict já calculado) ──
    for amb, cats in consolidado.items():
        for cat, info in cats.items():
            _c = info["c"]
            if _c > 800:
                _c /= 100
            _c = round(_c, 2)
            _h = info["h"]
            _l = info["l"]
            _per = round(2 * (_c + _l), 3) if _l else ""
            _A = round(_c * _h, 2)
            _idx = len(df10)
            df10.loc[_idx, ("", "Ambiente")] = amb
            df10.loc[_idx, ("Estruturas", "Peça")] = cat
            df10.loc[_idx, ("Paredes", "C")] = _c
            df10.loc[_idx, ("Paredes", "L")] = _l
            df10.loc[_idx, ("Paredes", "h")] = _h
            df10.loc[_idx, ("Paredes", "Per")] = _per
            df10.loc[_idx, ("Paredes", "A_tot")] = _A

    # ── Pisos (df4 já populado) ──
    for _idx4 in df4.index:
        _local4 = df4.at[_idx4, ("", "Local")]
        if _local4 != "Piso":
            continue
        _C4 = df4.at[_idx4, ("Dimensões", "C Proj [m]")]
        _L4 = df4.at[_idx4, ("Dimensões", "L [m]")]
        _amb4 = df4.at[_idx4, ("", "Ambiente")]
        if not _C4 or not _L4:
            continue
        _per4 = round(2 * (float(_C4) + float(_L4)), 3)
        _A4 = round(float(_C4) * float(_L4), 4)
        _idx = len(df10)
        df10.loc[_idx, ("", "Ambiente")] = _amb4
        df10.loc[_idx, ("Estruturas", "Peça")] = "Piso"
        df10.loc[_idx, ("Pisos", "C")] = _C4
        df10.loc[_idx, ("Pisos", "L")] = _L4
        df10.loc[_idx, ("Pisos", "h")] = ""
        df10.loc[_idx, ("Pisos", "Per")] = _per4
        df10.loc[_idx, ("Pisos", "A_tot")] = _A4

    def garantir_minimo_linhas(df, colunas, n=10):
        if df.empty:
            df = pd.DataFrame([{col: None for col in colunas} for _ in range(n)])
            df.columns = [
                col[1] if col[0] == "" else f"{col[0]} {col[1]}" for col in df.columns
            ]

        return df

    df = garantir_minimo_linhas(df, colunas_alvenarias)
    df2 = garantir_minimo_linhas(df2, colunas_alvenarias2)
    df3 = garantir_minimo_linhas(df3, colunas_alvenarias3)
    df4 = garantir_minimo_linhas(df4, colunas_alvenarias4)
    df5 = garantir_minimo_linhas(df5, colunas_alvenarias5)
    df6 = garantir_minimo_linhas(df6, colunas_alvenarias6)
    df7 = garantir_minimo_linhas(df7, colunas_alvenarias7)
    df8 = garantir_minimo_linhas(df8, colunas_alvenarias8)
    df9 = garantir_minimo_linhas(df9, colunas_alvenarias9)
    df10 = garantir_minimo_linhas(df10, colunas_alvenarias10)

    tabela_map = {
        "4.1 Painéis": df,
        "4.2 Vergas e Contra Vergas": df2,
        "4.3 Guias, Calçadas e Passeios": df3,
        "4.4 Rampas, Patamares e Passarelas": df4,
        "4.5 Pavimentos": df5,
        "4.6 Cercamentos": df6,
        "4.7 Regularização de Superfícies Verticais": df7,
        "4.8 Regularização de Superfícies Horizontais": df8,
        "4.9 Juntas de Dilatação": df9,
        "4.10 Impermeabilização": df10,
    }

    return tabela_map
