import pandas as pd
import json
import os
import re as _re, math as _math
from collections import defaultdict as _defaultdict, Counter as _Counter

colunas_acabamentos = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Pisos", "Tipo"),
        ("Pisos", "C [m]"),
        ("Pisos", "L [m]"),
        ("Pisos", "e [m]"),
        ("Pisos", "A [m²]"),
        ("Placa Cerâmica", "C [m]"),
        ("Placa Cerâmica", "L [m]"),
        ("Soleiras", "Tipo"),
        ("Soleiras", "C [m]"),
        ("Soleiras", "L [m]"),
        ("Soleiras", "e [m]"),
        ("Rodapés", "Tipo"),
        ("Rodapés", "C [m]"),
        ("Rodapés", "L [m]"),
        ("Rodapés", "h [m]"),
        ("Rodapés", "A [m²]"),
    ]
)

colunas_acabamentos2 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Azulejos e Rodabancas", "Tipo"),
        ("Azulejos e Rodabancas", "C [m]"),
        ("Azulejos e Rodabancas", "h [m]"),
        ("Azulejos e Rodabancas", "e [m]"),
        ("Azulejos e Rodabancas", "A [m²]"),
        ("Placa", "C [m]"),
        ("Placa", "L [m]"),
        ("Peitoris", "Tipo"),
        ("Peitoris", "C [m]"),
        ("Peitoris", "L [m]"),
        ("Peitoris", "e [m]"),
        ("Forros", "Tipo"),
        ("Forros", "C [m]"),
        ("Forros", "L [m]"),
        ("Forros", "A [m²]"),
        ("Placa", "C [m]"),
        ("Placa", "L [m]"),
    ]
)

colunas_acabamentos3 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Emassamento", "h [m]"),
        ("Emassamento", "Per [m]"),
        ("Emassamento", "A [m²] Parede"),
        ("Emassamento", "A [m²] Teto"),
        ("Lixamento", "h [m]"),
        ("Lixamento", "Per [m]"),
        ("Lixamento", "A [m²] Parede"),
        ("Lixamento", "A [m²] Teto"),
        ("Selamento", "h [m]"),
        ("Selamento", "Per [m]"),
        ("Selamento", "A [m²] Parede"),
        ("Selamento", "A [m²] Teto"),
        ("Pintura Acrílica A [m²]", "Parede"),
        ("Pintura Acrílica A [m²]", "Teto"),
        ("Pintura Acrílica A [m²]", "Piso"),
        ("Pintura Acrílica A [m²]", "Pilar"),
        ("Pintura Esmalte A [m²]", "Portas"),
        ("Pintura Esmalte A [m²]", "Janelas"),
        ("Pintura Esmalte A [m²]", "Grades"),
    ]
)

colunas_acabamentos4 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),

        ("Portas e Alçapões", "P/A"),
        ("Portas e Alçapões", "Qnt"),
        ("Portas e Alçapões", "L [cm]"),
        ("Portas e Alçapões", "h [cm]"),
        ("Portas e Alçapões", "e [cm]"),
        ("Portas e Alçapões", "A [m²]"),

        ("Janelas e visores", "P/A"),
        ("Janelas e visores", "Qnt"),
        ("Janelas e visores", "L [cm]"),
        ("Janelas e visores", "h [cm]"),
        ("Janelas e visores", "e [cm]"),
        ("Janelas e visores", "A [m²]"),

        ("Telas", "L [cm]"),
        ("Telas", "h [cm]"),
        ("Telas", "Qnt"),
        ("Telas", "A [m²]"),

        ("Venezianas Industriais", "Peça"),
        ("Venezianas Industriais", "L [cm]"),
        ("Venezianas Industriais", "h [cm]"),
        ("Venezianas Industriais", "Qnt"),
        ("Venezianas Industriais", "A [m²]"),

        ("Protetores de canto", "L [cm]"),
        ("Protetores de canto", "e [mm]"),
        ("Protetores de canto", "C [m]"),

        ("Protetores de Parede", "L [cm]"),
        ("Protetores de Parede", "e [mm]"),
        ("Protetores de Parede", "C [m]"),

        ("Grades", "Tipo"),
        ("Grades", "A [m²]"),
        ("Grades", "Malha [cm]"),
        ("Grades", "e [mm]"),

        ("Afastamento", "Janela"),
        ("Afastamento", "Alvenaria"),

    ]
)

colunas_acabamentos5 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),

        ("Acessórios", "Bacia sanitária"),
        ("Acessórios", "Mictório"),
        ("Acessórios", "Lavatórios"),
        ("Acessórios", "Cubas"),
        ("Acessórios", "Tanques"),
        ("Acessórios", "Torneiras"),

        ("Barras de Apoio", "Qnt"),
        ("Barras de Apoio", "C [m]"),
        ("Barras de Apoio", "ø [mm]"),
        ("Barras de Apoio", "h [m]"),

        ("Corrimãos e guarda-corpos", "Qnt"),
        ("Corrimãos e guarda-corpos", "C [m]"),
        ("Corrimãos e guarda-corpos", "ø [mm]"),
        ("Corrimãos e guarda-corpos", "h [m]"),
    ]
)

colunas_acabamentos6 = pd.MultiIndex.from_tuples(
    [
    ("", "", "Ambiente"),
    ("Bancadas e Pias", "Dimensões", "A [m²]"),
    ("Bancadas e Pias", "Dimensões", "h [m]"),

    ("Bancadas e Pias", "Tampos", "C [m]"),
    ("Bancadas e Pias", "Tampos", "L [m]"),
    ("Bancadas e Pias", "Tampos", "e [m]"),

    ("Bancadas e Pias", "Frontão", "C [m]"),
    ("Bancadas e Pias", "Frontão", "L [m]"),
    ("Bancadas e Pias", "Frontão", "e [m]"),

    ("Bancadas e Pias", "Saia", "C [m]"),
    ("Bancadas e Pias", "Saia", "L [m]"),
    ("Bancadas e Pias", "Saia", "e [m]"),

    ("Divisórias", "", "Tipo"),
    ("Divisórias", "", "Qnt"),
    ("Divisórias", "Peça", "C [m]"),
    ("Divisórias", "Peça", "h [m]"),
    ("Divisórias", "Peça", "A [m²]"),
    ("Divisórias", "Portas", "L [m]"),
    ("Divisórias", "Portas", "h [m]"),
    ("Divisórias", "Portas", "A [m²]"),

    ("Boxes", "", "Tipo"),
    ("Boxes", "", "Qnt"),
    ("Boxes", "Peça", "C [cm]"),
    ("Boxes", "Portas", "L [cm]"),
    ("Boxes", "Peça", "e [mm]"),
    ("Boxes", "Portas", "Sobreposição [cm]"),
    ("Boxes", "Portas", "A [m²]"),
    ]
)

colunas_acabamentos7 = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),
        ("Mobiliário", "", "Tipo"),
        ("Mobiliário", "Dimensões", "C [m]"),
        ("Mobiliário", "Dimensões", "L [m]"),
        ("Mobiliário", "Dimensões", "h [m]"),
        ("Mobiliário", "", "A [m²]"),
    ]
)


def acabamentos(json_path, dxf_path):
    df = pd.DataFrame(columns=colunas_acabamentos)
    df2 = pd.DataFrame(columns=colunas_acabamentos2)
    df3 = pd.DataFrame(columns=colunas_acabamentos3)
    df4 = pd.DataFrame(columns=colunas_acabamentos4)
    df5 = pd.DataFrame(columns=colunas_acabamentos5)
    df6 = pd.DataFrame(columns=colunas_acabamentos6)
    df7 = pd.DataFrame(columns=colunas_acabamentos7)

    with open(json_path, "r", encoding="utf-8") as m:
        dados_manuais = json.load(m)

    with open(dxf_path, "r", encoding="utf-8") as a:
        dados_automaticos = json.load(a)

    output_dir = r"C:\Users\vinic\Desktop\Material Fatec\API_4_Semestre(projeto)\Fornovo-Backend\ForBack\media\output_tables"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "tabela6.xlsx")

    # ── Extração do Quadro de Acabamentos (Símbolos - Quadro de Acabamentos) ──

    _col_map = {
        6686.8: ("Pisos", "Granilite"),
        6688.8: ("Pisos", "Piso Cerâmico"),
        6690.8: ("Rodapés", "Granilite"),
        6692.8: ("Rodapés", "Rodapé Cerâmico"),
        6694.8: ("Paredes", "Rev. Cer./Pint. Acrílica"),
        6696.8: ("Paredes", "Pintura Acrílica"),
        6698.8: ("Teto", "PVC"),
        6700.8: ("Teto", "Fib. Min. Armstrong"),
        6702.8: ("Teto", "Gesso"),
    }

    ambientes_y = [
        ("ALOJAMENTO 1", -3705.3),
        ("ALOJAMENTO 2", -3707.3),
        ("ALOJAMENTO 3", -3709.3),
        ("ALOJAMENTO 4", -3711.3),
        ("ÁREA 1", -3713.3),
        ("AUDITÓRIO", -3715.3),
        ("BANHEIRO 1", -3717.3),
        ("BANHEIRO 2", -3719.3),
        ("BANHEIRO 3", -3721.3),
        ("BANHEIRO 4", -3723.3),
        ("CIRCULAÇÃO 1", -3725.3),
        ("CIRCULAÇÃO 2", -3727.3),
        ("CIRCULAÇÃO 3", -3729.3),
        ("COPA", -3731.3),
        ("PASSADIÇO", -3733.3),
        ("RESERVA", -3735.3),
        ("SALA 1", -3737.3),
        ("SALA 2", -3739.3),
        ("SALA 3", -3741.3),
        ("SALA 4", -3743.3),
        ("SALA 5", -3745.3),
        ("SALA 6", -3747.3),
        ("SALA 7", -3749.3),
    ]

    qac_circles = [
        e
        for e in dados_automaticos.get("entidades", [])
        if e.get("layer") == "Símbolos - Quadro de Acabamentos"
        and e.get("tipo") == "CIRCLE"
        and "dados" in e
        and abs(e["dados"].get("raio", 0) - 0.40) < 0.05
        and 6682 <= e["dados"].get("centro", [0])[0] <= 6710
        and -3755 <= e["dados"].get("centro", [0, -9999])[1] <= -3700
    ]

    def _match_col(cx):
        nearest = min(_col_map.keys(), key=lambda kx: abs(kx - cx))
        return _col_map[nearest] if abs(nearest - cx) < 1.5 else None

    for _amb, _ay in ambientes_y:
        _circles_amb = [
            e for e in qac_circles if abs(e["dados"]["centro"][1] - _ay) < 0.8
        ]
        if not _circles_amb:
            continue

        _pisos_amb = []
        _rodapes_amb = []
        _paredes_amb = []

        for _c in _circles_amb:
            _cx = _c["dados"]["centro"][0]
            _col = _match_col(_cx)
            if not _col:
                continue
            _cat, _mat = _col
            if _cat == "Pisos":
                _pisos_amb.append(_mat)
            elif _cat == "Rodapés":
                _rodapes_amb.append(_mat)
            elif _cat == "Paredes":
                _paredes_amb.append(_mat)

        _idx = len(df)
        df.loc[_idx, ("", "Ambiente")] = _amb
        df.loc[_idx, ("Pisos", "Tipo")] = " / ".join(_pisos_amb) if _pisos_amb else ""
        df.loc[_idx, ("Rodapés", "Tipo")] = (
            " / ".join(_rodapes_amb) if _rodapes_amb else ""
        )

    import re as _re, math as _math
    from collections import defaultdict as _defaultdict, Counter as _Counter

    _txts_all = dados_automaticos.get("textos", [])
    _ents_all  = dados_automaticos.get("entidades", [])

    _txts_qa_all = [
        t for t in _txts_all
        if t.get("layer") == "Símbolos - Quadro de Acabamentos" and t.get("posicao")
    ]

    _id_pat   = _re.compile(r"^([PpJjVv][A-Za-z0-9]+\d*)$")
    _dim_pat  = _re.compile(r"^(\d+[.,]\d+)\s*[xX]\s*(\d+[.,]\d+)(?:\s*/\s*(\d+[.,]\d+))?$")
    _area_pat = _re.compile(r"^(\d+[.,]\d+)$")

    _qa_esq = [
        t for t in _txts_qa_all
        if 5980 <= t["posicao"][0] <= 6200 and -3665 <= t["posicao"][1] <= -3560
    ]

    _linhas_qa = {}
    for _t in _qa_esq:
        _yk = round(_t["posicao"][1] * 2) / 2
        _linhas_qa.setdefault(_yk, []).append(_t)

    _catalogo = {}
    for _y, _txts in sorted(_linhas_qa.items(), reverse=True):
        _ts = sorted(_txts, key=lambda t: t["posicao"][0])
        _cols = [(_t["posicao"][0], _t["conteudo"].strip()) for _t in _ts]
        _id_col = next((_c for _c in _cols if _id_pat.match(_c[1]) and _c[1] not in ("Janela","Porta","Visor")), None)
        if not _id_col:
            continue
        _esq_id = _id_col[1]
        _tipo = "Porta" if _esq_id.upper().startswith("P") else ("Janela" if _esq_id.upper().startswith("J") else "Visor")
        _dim_col  = next((_c for _c in _cols if _dim_pat.match(_c[1])), None)
        _area_col = next((_c for _c in _cols if _area_pat.match(_c[1].replace(",","."))), None)
        _descr_col = next((_c for _c in _cols if _c[0] > 6025 and not _area_pat.match(_c[1].replace(",",".")) and not _id_pat.match(_c[1]) and not _dim_pat.match(_c[1])), None)
        _L, _h, _peit, _A, _descr = "", "", "", "", ""
        if _dim_col:
            _m = _dim_pat.match(_dim_col[1])
            if _m:
                _L    = float(_m.group(1).replace(",", "."))
                _h    = float(_m.group(2).replace(",", "."))
                _peit = float(_m.group(3).replace(",", ".")) if _m.group(3) else ""
        if _area_col:
            _A = float(_area_col[1].replace(",", "."))
        if _descr_col:
            _descr = _descr_col[1]
        _catalogo[_esq_id] = {"tipo": _tipo, "L": _L, "h": _h, "peitoril": _peit, "A": _A, "descricao": _descr}

    _ambientes_cad4 = []
    for _txt in _txts_all:
        _c = _txt.get("conteudo", "")
        if "m²" not in _c.lower():
            continue
        _ma = _re.search(r"(\d+[.,]\d+)\s*m²", _c, _re.IGNORECASE)
        if not _ma:
            continue
        _parts = _c.split("\\P"); _aidx = -1
        for _ip, _ps in enumerate(_parts):
            if _re.search(r"\d+[.,]\d+\s*m²", _ps, _re.IGNORECASE): _aidx = _ip; break
        _raw = " ".join(_parts[:_aidx]) if _aidx > 0 else _parts[0]
        _nome = _re.sub(r"\\[^;\\]+;", "", _raw).replace("{", "").replace("}", "")
        _nome = _re.sub(r"\\[Pp]", " ", _nome)
        _nome = _re.sub(r"\d+[.,]\d+\s*m²", "", _nome, flags=_re.IGNORECASE)
        _nome = _re.sub(r"\s+", " ", _nome).strip()
        if _nome and _txt.get("posicao"):
            _ambientes_cad4.append({"nome": _nome, "pos": _txt["posicao"]})

    def _get_amb4(cx, cy, thr=20):
        if not _ambientes_cad4:
            return "Não identificado"
        _best = min(_ambientes_cad4, key=lambda a: _math.hypot(cx - a["pos"][0], cy - a["pos"][1]))
        return _best["nome"] if _math.hypot(cx - _best["pos"][0], cy - _best["pos"][1]) <= thr else "Não identificado"

    _txts_planta_ids = [
        t for t in _txts_all
        if _id_pat.match(t.get("conteudo", "").strip())
        and t.get("posicao")
        and not (5980 <= t["posicao"][0] <= 6200)
        and not (6580 <= t["posicao"][0] <= 6710)
        and not (10100 <= t["posicao"][0] <= 10570)
    ]

    _amb_ids = _defaultdict(list)
    for _t in _txts_planta_ids:
        _esq_id = _t["conteudo"].strip()
        if _esq_id not in _catalogo:
            continue
        _cx, _cy = _t["posicao"][:2]
        _amb = _get_amb4(_cx, _cy)
        _amb_ids[_amb].append(_esq_id)

    for _amb in sorted(_amb_ids):
        _contagem = _Counter(_amb_ids[_amb])
        _portas  = {_k: _v for _k, _v in _contagem.items() if _catalogo[_k]["tipo"] == "Porta"}
        _janelas = {_k: _v for _k, _v in _contagem.items() if _catalogo[_k]["tipo"] == "Janela"}
        _visores = {_k: _v for _k, _v in _contagem.items() if _catalogo[_k]["tipo"] == "Visor"}

        _all_groups = [("Portas e Alçapões", _portas), ("Janelas e visores", _janelas), ("Janelas e visores", _visores)]

        for _grupo_label, _grupo in [("Portas e Alçapões", _portas), ("Janelas e visores", {**_janelas, **_visores})]:
            for _esq_id, _qnt in sorted(_grupo.items()):
                _cat = _catalogo[_esq_id]
                _idx = len(df4)
                _A_total = round(_cat["A"] * _qnt, 3) if _cat["A"] != "" else ""
                df4.loc[_idx, ("", "Ambiente")]                        = _amb
                df4.loc[_idx, (_grupo_label, "P/A")]                   = _esq_id
                df4.loc[_idx, (_grupo_label, "Qnt")]                   = _qnt
                df4.loc[_idx, (_grupo_label, "L [cm]")]                = round(_cat["L"] * 100) if _cat["L"] != "" else ""
                df4.loc[_idx, (_grupo_label, "h [cm]")]                = round(_cat["h"] * 100) if _cat["h"] != "" else ""
                df4.loc[_idx, (_grupo_label, "e [cm]")]                = ""
                df4.loc[_idx, (_grupo_label, "A [m²]")]                = _A_total
                df4.loc[_idx, ("Afastamento", "Janela")]               = _cat["peitoril"] if _cat["peitoril"] != "" else ""
                df4.loc[_idx, ("Afastamento", "Alvenaria")]            = ""

    _ambientes_cad3 = {}
    for _txt in _txts_all:
        _c = _txt.get("conteudo", "")
        if "m²" not in _c.lower():
            continue
        _ma = _re.search(r"(\d+[.,]\d+)\s*m²", _c, _re.IGNORECASE)
        if not _ma:
            continue
        _parts = _c.split("\\P"); _aidx = -1
        for _ip, _ps in enumerate(_parts):
            if _re.search(r"\d+[.,]\d+\s*m²", _ps, _re.IGNORECASE): _aidx = _ip; break
        _raw = " ".join(_parts[:_aidx]) if _aidx > 0 else _parts[0]
        _nome = _re.sub(r"\\[^;\\]+;", "", _raw).replace("{", "").replace("}", "")
        _nome = _re.sub(r"\\[Pp]", " ", _nome)
        _nome = _re.sub(r"\d+[.,]\d+\s*m²", "", _nome, flags=_re.IGNORECASE)
        _nome = _re.sub(r"\s+", " ", _nome).strip()
        _area = float(_ma.group(1).replace(",", "."))
        if _nome and (_nome not in _ambientes_cad3 or _area > _ambientes_cad3[_nome]):
            _ambientes_cad3[_nome] = _area

    _esmalte_portas  = _defaultdict(float)
    _esmalte_janelas = _defaultdict(float)
    for _row in df4.itertuples():
        _amb3 = getattr(_row, "_1", "")
        _pa   = getattr(_row, "_2", "")
        _a_m2 = getattr(_row, "_7", None)
        if not _amb3 or not _pa or _a_m2 == "" or _a_m2 != _a_m2:
            continue
        try:
            _val = float(_a_m2)
        except (TypeError, ValueError):
            continue
        if str(_pa).upper().startswith("P"):
            _esmalte_portas[_amb3]  += _val
        else:
            _esmalte_janelas[_amb3] += _val

    for _amb, _area_teto in sorted(_ambientes_cad3.items()):
        _idx3 = len(df3)
        df3.loc[_idx3, ("", "Ambiente")]                     = _amb
        df3.loc[_idx3, ("Emassamento",  "A [m²] Teto")]     = _area_teto
        df3.loc[_idx3, ("Lixamento",    "A [m²] Teto")]     = _area_teto
        df3.loc[_idx3, ("Selamento",    "A [m²] Teto")]     = _area_teto
        df3.loc[_idx3, ("Pintura Acrílica A [m²]", "Teto")] = _area_teto
        df3.loc[_idx3, ("Pintura Acrílica A [m²]", "Piso")] = _area_teto
        if _amb in _esmalte_portas:
            df3.loc[_idx3, ("Pintura Esmalte A [m²]", "Portas")]  = round(_esmalte_portas[_amb], 3)
        if _amb in _esmalte_janelas:
            df3.loc[_idx3, ("Pintura Esmalte A [m²]", "Janelas")] = round(_esmalte_janelas[_amb], 3)

    _polys_mob = [
        e for e in _ents_all
        if e.get("layer") == "Hidrossanitário - Mobiliário"
        and e.get("tipo") == "LWPOLYLINE"
        and "dados" in e
        and e["dados"].get("fechada")
    ]
    _mob_por_amb = _defaultdict(int)
    for _e in _polys_mob:
        _pts = _e["dados"].get("pontos", [])
        if not _pts:
            continue
        _cx = sum(p[0] for p in _pts) / len(_pts)
        _cy = sum(p[1] for p in _pts) / len(_pts)
        _mob_por_amb[_get_amb4(_cx, _cy)] += 1

    _torn_por_amb = _defaultdict(int)
    for _t in _txts_all:
        if "torneira" in _t.get("conteudo", "").lower() and _t.get("posicao"):
            _cx, _cy = _t["posicao"][:2]
            _torn_por_amb[_get_amb4(_cx, _cy)] += 1

    _ambientes5 = set(_mob_por_amb) | set(_torn_por_amb)
    for _amb in sorted(_ambientes5):
        if _torn_por_amb.get(_amb, 0) > 0:
            _idx5 = len(df5)
            df5.loc[_idx5, ("", "Ambiente")] = _amb 
            df5.loc[_idx5, ("Acessórios", "Torneiras")] = _torn_por_amb[_amb]
    

    _txts_all = dados_automaticos.get("textos", [])
    _ents_all  = dados_automaticos.get("entidades", [])

    _ambientes_cad6 = []
    for _txt in _txts_all:
        _c = _txt.get("conteudo", "")
        if "m²" not in _c.lower():
            continue
        _ma = _re.search(r"(\d+[.,]\d+)\s*m²", _c, _re.IGNORECASE)
        if not _ma:
            continue
        _parts = _c.split("\\P"); _aidx = -1
        for _ip, _ps in enumerate(_parts):
            if _re.search(r"\d+[.,]\d+\s*m²", _ps, _re.IGNORECASE): _aidx = _ip; break
        _raw = " ".join(_parts[:_aidx]) if _aidx > 0 else _parts[0]
        _nome = _re.sub(r"\\[^;\\]+;", "", _raw).replace("{","").replace("}","")
        _nome = _re.sub(r"\\[Pp]", " ", _nome)
        _nome = _re.sub(r"\d+[.,]\d+\s*m²", "", _nome, flags=_re.IGNORECASE)
        _nome = _re.sub(r"\s+", " ", _nome).strip()
        if _nome and _txt.get("posicao"):
            _ambientes_cad6.append({"nome": _nome, "pos": _txt["posicao"]})

    def _get_amb6(cx, cy, thr=200):
        if not _ambientes_cad6:
            return "Não identificado"
        _best = min(_ambientes_cad6, key=lambda a: _math.hypot(cx - a["pos"][0], cy - a["pos"][1]))
        return _best["nome"] if _math.hypot(cx - _best["pos"][0], cy - _best["pos"][1]) <= thr else "Não identificado"

    _t_balcao = next(
        (t for t in _txts_all if "balcão" in t.get("conteudo", "").lower() and t.get("posicao")),
        None,
    )
    if _t_balcao:
        _cx6, _cy6 = _t_balcao["posicao"][:2]
        _amb_bal = _get_amb6(_cx6, _cy6)
        _m_e = _re.search(r"e\s*=\s*(\d+[.,]\d+)\s*m", _t_balcao["conteudo"], _re.IGNORECASE)
        _m_h = _re.search(r"h\s*=\s*(\d+[.,]\d+)\s*m", _t_balcao["conteudo"], _re.IGNORECASE)
        _idx6 = len(df6)
        df6.loc[_idx6, ("", "", "Ambiente")]                   = _amb_bal
        df6.loc[_idx6, ("Bancadas e Pias", "Frontão", "e [m]")] = float(_m_e.group(1).replace(",", ".")) if _m_e else ""
        df6.loc[_idx6, ("Bancadas e Pias", "Dimensões", "h [m]")] = float(_m_h.group(1).replace(",", ".")) if _m_h else ""

    _t_div = next(
        (t for t in _txts_all if "divisória" in t.get("conteudo", "").lower() and "drywall" in t.get("conteudo", "").lower() and t.get("posicao")),
        None,
    )
    if _t_div:
        _cx6, _cy6 = _t_div["posicao"][:2]
        _amb_div = _get_amb6(_cx6, _cy6)
        _m_e2 = _re.search(r"espessura\s*=\s*(\d+)\s*cm", _t_div["conteudo"], _re.IGNORECASE)
        _idx6 = len(df6)
        df6.loc[_idx6, ("", "", "Ambiente")]          = _amb_div
        df6.loc[_idx6, ("Divisórias", "", "Tipo")]    = "Drywall"
        df6.loc[_idx6, ("Divisórias", "Peça", "C [m]")] = round(float(_m_e2.group(1)) / 100, 2) if _m_e2 else ""

    _pd1_por_amb = _defaultdict(lambda: {"qnt": 0, "A": 0.0})
    for _row in df4.itertuples():
        _amb6r = getattr(_row, "_1", "")
        _pa    = getattr(_row, "_2", "")
        _qnt   = getattr(_row, "_3", 0)
        _a_m2  = getattr(_row, "_7", "")
        if str(_pa).upper() == "PD1" and _amb6r:
            try:
                _pd1_por_amb[_amb6r]["qnt"] += int(_qnt)
                _pd1_por_amb[_amb6r]["A"]   += float(_a_m2)
            except (TypeError, ValueError):
                pass

    for _amb, _vals in sorted(_pd1_por_amb.items()):
        _idx6 = len(df6)
        df6.loc[_idx6, ("", "", "Ambiente")]              = _amb
        df6.loc[_idx6, ("Divisórias", "", "Tipo")]        = "MDF/Fórmica"
        df6.loc[_idx6, ("Divisórias", "", "Qnt")]         = _vals["qnt"]
        df6.loc[_idx6, ("Divisórias", "Portas", "L [m]")] = 1.0
        df6.loc[_idx6, ("Divisórias", "Portas", "h [m]")] = 2.5
        df6.loc[_idx6, ("Divisórias", "Portas", "A [m²]")] = round(_vals["A"], 3)
    
    def garantir_minimo_linhas(df, colunas, n=10):
        if df.empty:
            df = pd.DataFrame([{col: None for col in colunas} for _ in range(n)])
            df.columns = [
                col[1] if col[0] == "" else f"{col[0]} {col[1]}"
                for col in df.columns
            ]

        return df
    
    df = garantir_minimo_linhas(df, colunas_acabamentos)
    df2 = garantir_minimo_linhas(df2, colunas_acabamentos2)
    df3 = garantir_minimo_linhas(df3, colunas_acabamentos3)
    df4 = garantir_minimo_linhas(df4, colunas_acabamentos4)
    df5 = garantir_minimo_linhas(df5, colunas_acabamentos5)
    df6 = garantir_minimo_linhas(df6, colunas_acabamentos6)

    return (
        df.sort_index(axis=1),
        df2.sort_index(axis=1),
        df3.sort_index(axis=1),
        df4.sort_index(axis=1),
        df5.sort_index(axis=1),
        df6.sort_index(axis=1)
    )