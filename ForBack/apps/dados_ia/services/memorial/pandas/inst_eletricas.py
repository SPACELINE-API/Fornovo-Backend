import pandas as pd
import json
import os
import re
import math
from collections import defaultdict

colunas_eletricas = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),
        ("", "", "Circuito"),
        ("Cabeamento", "", "Qnt Cabos"),
        ("Cabeamento", "C [m] / A [mm²]", "1,5"),
        ("Cabeamento", "C [m] / A [mm²]", "2,5"),
        ("Cabeamento", "C [m] / A [mm²]", "4"),
        ("Cabeamento", "C [m] / A [mm²]", "10"),
        ("Cabeamento", "C [m] / A [mm²]", "16"),
        ("Cabeamento", "C [m] / A [mm²]", "25"),
        ("Cabeamento", "C [m] / A [mm²]", "100"),
        ("", "Postes", "ø [m]"),
        ("", "Postes", "C [m]"),
        ("", "Cruzetas", "C [m]"),
        ("", "Cruzetas", "L [m]"),
        ("", "Suportes", "C [m]"),
        ("", "Suportes", "L [m]"),
        ("", "Isoladores", "ø [m]"),
        ("", "Isoladores", "C [m]"),
    ]
)

colunas_eletricas1 = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),
        ("", "", "Circuito"),
        ("Cabeamento", "", "Qnt Cabos"),
        ("Cabeamento", "C [m] / A [mm²]", "1,5"),
        ("Cabeamento", "C [m] / A [mm²]", "2,5"),
        ("Cabeamento", "C [m] / A [mm²]", "4"),
        ("Cabeamento", "C [m] / A [mm²]", "10"),
        ("Cabeamento", "C [m] / A [mm²]", "16"),
        ("Cabeamento", "C [m] / A [mm²]", "25"),
        ("Cabeamento", "C [m] / A [mm²]", "100"),
        ("Eletroduto", "Metálicos", "DN [mm]"),
        ("Eletroduto", "Metálicos", "C [m]"),
        ("Eletroduto", "Corrugado", "DN [mm]"),
        ("Eletroduto", "Corrugado", "C [m]"),
        ("Eletroduto", "PVC Liso", "DN [mm]"),
        ("Eletroduto", "PVC Liso", "C [m]"),
    ]
)

colunas_eletricas2 = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),
        ("", "", "Circuito"),
        ("Quadros de energia", "Tipo", ""),
        ("Quadros de energia", "Qtd Disjuntores", ""),
        ("Cabeamento", "A [mm²]", "1,5 C [m]"),
        ("Cabeamento", "A [mm²]", "2,5 C [m]"),
        ("Cabeamento", "A [mm²]", "4 C [m]"),
        ("Cabeamento", "A [mm²]", "10 C [m]"),
        ("Cabeamento", "A [mm²]", "16 C [m]"),
        ("Dutos", "Eletrocalha", "C [m]"),
        ("Dutos", "Eletrocalha", "L [cm]"),
        ("Dutos", "Eletrocalha", "h [cm]"),
        ("Dutos", "Eletroduto", "DN [mm]"),
        ("Dutos", "Eletroduto", "C [m]"),
        ("", "Conduletes", "B"),
        ("", "Conduletes", "C"),
        ("", "Conduletes", "E"),
        ("", "Conduletes", "LL"),
        ("", "Conduletes", "LR"),
        ("", "Conduletes", "LB"),
        ("", "Conduletes", "TB"),
        ("", "Conduletes", "T"),
        ("", "Conduletes", "X"),
        ("", "tomadas", "Tipo"),
        ("", "tomadas", "Quantidade"),
        ("", "Interruptores", "Tipo"),
        ("", "Interruptores", "Quantidade"),
        ("", "Luminárias", "Tipo"),
        ("", "Luminárias", "Quantidade"),
        ("Aterramento", "Haste", "Quantidade"),
        ("Aterramento", "Caixa Inspeção", "Quantidade"),
    ]
)

MIN_BLANK_ROWS = 15
DATA_COL = 1


def limpar_texto_cad(texto):
    t = re.sub(r"\\[^;\\]+;", "", texto)
    t = t.replace("{", "").replace("}", "")
    t = t.replace(r"\P", " ").replace(r"\p", " ")
    return t.strip()


def get_material_tubo(texto):
    t = texto.lower()
    if "corrugado" in t:
        return "Corrugado"
    if "galvanizado" in t or "metálico" in t:
        return "Metálicos"
    return "PVC Liso"


def eletricas(dados_manuais, dados_automaticos):
    df = pd.DataFrame(columns=colunas_eletricas)
    df1 = pd.DataFrame(columns=colunas_eletricas1)
    df2 = pd.DataFrame(columns=colunas_eletricas2)

    _txts_all = dados_automaticos.get("textos", [])
    _ents_all = dados_automaticos.get("entidades", [])

    _ambientes_ele = []
    for _txt in _txts_all:
        _c_limpo = limpar_texto_cad(_txt.get("conteudo", ""))
        _c_lower = _c_limpo.lower()

        if "m²" in _c_lower and "mm" not in _c_lower and _txt.get("posicao"):
            _nome = re.sub(r"\d+[.,]\d+\s*m²", "", _c_limpo, flags=re.IGNORECASE)
            _nome = re.sub(r"P\s*=\s*\d+[.,]\d+\s*M", "", _nome, flags=re.IGNORECASE)
            _nome = re.sub(r"PD\s*=\s*\d+[.,]\d+\s*M", "", _nome, flags=re.IGNORECASE)
            _nome = re.sub(r"\s+", " ", _nome).strip()

            if _nome and len(_nome) > 2:
                _ambientes_ele.append({"nome": _nome.upper(), "pos": _txt["posicao"]})

    def _get_amb_ele(cx, cy):
        if not _ambientes_ele:
            return "GERAL"
        return min(
            _ambientes_ele, key=lambda a: math.hypot(cx - a["pos"][0], cy - a["pos"][1])
        )["nome"]

    _circuitos_cad = []
    for _txt in _txts_all:
        _layer = _txt.get("layer", "").upper()
        if "ELE" in _layer or "ELÉTRICA" in _layer:
            _c_limpo = (
                limpar_texto_cad(_txt.get("conteudo", ""))
                .replace("(", "")
                .replace(")", "")
                .strip()
            )
            if re.match(r"^C\d+$", _c_limpo, re.IGNORECASE):
                _circuitos_cad.append(
                    {"nome": _c_limpo.upper(), "pos": _txt.get("posicao", [0, 0, 0])}
                )

    def _get_circuito_ele(cx, cy):
        if not _circuitos_cad:
            return "C?"
        return min(
            _circuitos_cad, key=lambda c: math.hypot(cx - c["pos"][0], cy - c["pos"][1])
        )["nome"]

    _bitolas_comerciais = ["1,5", "2,5", "4", "10", "16", "25", "100"]
    _cabos_encontrados = defaultdict(lambda: defaultdict(float))

    for _txt in _txts_all:
        _layer = _txt.get("layer", "").upper()

        if "ELE" in _layer or "ELÉTRICA" in _layer:
            _c_limpo = limpar_texto_cad(_txt.get("conteudo", ""))
            _cx, _cy = _txt.get("posicao", [0, 0, 0])[:2]

            _m_cabo1 = re.search(
                r"(\d+)?\s*#\s*(\d+[.,]\d+|\d+)\s*(?:mm)?", _c_limpo, re.IGNORECASE
            )
            _m_cabo2 = re.search(
                r"\b(\d+[.,]\d+|\d+)\s*mm[²2]?\b", _c_limpo, re.IGNORECASE
            )

            _qnt = 1
            _bitola = None

            if _m_cabo1:
                _qnt = int(_m_cabo1.group(1)) if _m_cabo1.group(1) else 1
                _bitola = _m_cabo1.group(2).replace(".", ",")

            elif _m_cabo2:
                _bitola = _m_cabo2.group(1).replace(".", ",")

            elif _c_limpo.replace(".", ",") in _bitolas_comerciais:
                _bitola = _c_limpo.replace(".", ",")

            if _bitola and _bitola in _bitolas_comerciais:
                _amb = _get_amb_ele(_cx, _cy)
                _circ = _get_circuito_ele(_cx, _cy)

                _cabos_encontrados[(_amb, _circ)][_bitola] += _qnt

    for (_amb, _circ), _bitolas in sorted(_cabos_encontrados.items()):
        _idx = len(df)
        df.loc[_idx, ("", "", "Ambiente")] = _amb
        df.loc[_idx, ("", "", "Circuito")] = _circ
        df.loc[_idx, ("Cabeamento", "", "Qnt Cabos")] = sum(_bitolas.values())
        for _b, _qtd in _bitolas.items():
            df.loc[_idx, ("Cabeamento", "C [m] / A [mm²]", _b)] = _qtd

    _postes_encontrados = defaultdict(int)
    _ids_postes_vistos = set()

    for _txt in _txts_all:
        _c_limpo = limpar_texto_cad(_txt.get("conteudo", ""))
        if "poste" in _c_limpo.lower():
            _match_poste = re.search(r"poste\s*(\d+)", _c_limpo, re.IGNORECASE)
            _id_poste = _match_poste.group(1) if _match_poste else _c_limpo

            if _id_poste not in _ids_postes_vistos:
                _ids_postes_vistos.add(_id_poste)
                _cx, _cy = _txt.get("posicao", [0, 0, 0])[:2]
                _amb = _get_amb_ele(_cx, _cy)
                _postes_encontrados[_amb] += 1

    for _amb, _qtd in _postes_encontrados.items():
        _idx = len(df)
        df.loc[_idx, ("", "", "Ambiente")] = _amb
        df.loc[_idx, ("", "Postes", "C [m]")] = 6.0
        df.loc[_idx, ("", "Postes", "ø [m]")] = 0.2

    _padrao_tubo = re.compile(
        r"(?:%%[cC]|ø|Ø|DN)\s*(\d+[,.]?\d*(?:/\d+)?)\s*(\"|mm)?", re.IGNORECASE
    )
    _mapa_diametros = {
        "1/4": "25",
        "12": "20",
        "5/8": "20",
        "3/4": "25",
        "1": "32",
        "1.1/4": "40",
        "1.1/2": "50",
        "2": "60",
    }

    _textos_tubos = []
    for _txt in _txts_all:
        _layer = _txt.get("layer", "").upper()
        if "ELE" in _layer or "ELÉTRICA" in _layer:
            _c_limpo = limpar_texto_cad(_txt.get("conteudo", ""))
            _m_tubo = _padrao_tubo.search(_c_limpo)
            if _m_tubo:
                _val = _m_tubo.group(1).replace(",", ".")
                _dn = _mapa_diametros.get(_val, _val)
                _mat = get_material_tubo(_c_limpo)
                _textos_tubos.append(
                    {"dn": _dn, "material": _mat, "pos": _txt.get("posicao", [0, 0, 0])}
                )

    def _get_tubo_ele(cx, cy):
        if not _textos_tubos:
            return ("25", "PVC Liso")
        _best = min(
            _textos_tubos, key=lambda t: math.hypot(cx - t["pos"][0], cy - t["pos"][1])
        )
        return (_best["dn"], _best["material"])

    _dutos_encontrados = defaultdict(float)
    for _e in _ents_all:
        _layer = _e.get("layer", "").upper()
        if _layer in ["ELE-CIRCUITO", "ELÉTRICA"]:
            _tipo = _e.get("tipo", "")
            if _tipo in ["LINE", "LWPOLYLINE", "POLYLINE"]:
                _comp = _e.get("dados", {}).get("comprimento", 0)
                if _comp > 0:
                    _pts = _e.get("dados", {}).get("vertices", [])
                    if not _pts and "inicio" in _e.get("dados", {}):
                        _pts = [_e["dados"]["inicio"]]
                    if _pts:
                        _cx, _cy = _pts[0][:2]
                        _amb = _get_amb_ele(_cx, _cy)
                        _circ = _get_circuito_ele(_cx, _cy)
                        _dn, _mat = _get_tubo_ele(_cx, _cy)
                        _dutos_encontrados[(_amb, _circ, _mat, _dn)] += _comp

    for (_amb, _circ, _mat, _dn), _comp in sorted(_dutos_encontrados.items()):
        _idx = len(df1)
        df1.loc[_idx, ("", "", "Ambiente")] = _amb
        df1.loc[_idx, ("", "", "Circuito")] = _circ
        df1.loc[_idx, ("Eletroduto", _mat, "DN [mm]")] = _dn
        df1.loc[_idx, ("Eletroduto", _mat, "C [m]")] = round(_comp, 2)

    _dados_df2 = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    _hastes_aterramento = defaultdict(int)
    _caixas_aterramento = defaultdict(int)

    for _txt in _txts_all:
        _layer = _txt.get("layer", "").upper()
        _c_limpo = limpar_texto_cad(_txt.get("conteudo", ""))
        _cx, _cy = _txt.get("posicao", [0, 0, 0])[:2]

        if "ELE" in _layer or "ELÉTRICA" in _layer:
            _amb = _get_amb_ele(_cx, _cy)
            _circ = _get_circuito_ele(_cx, _cy)

            if (
                re.match(r"^(QDG|QDC|QD)\b", _c_limpo, re.IGNORECASE)
                or "QUADRO" in _c_limpo.upper()
            ):
                if len(_c_limpo) < 50:
                    _dados_df2[_amb][_circ][
                        ("Quadros de energia", "Tipo", "")
                    ] = _c_limpo.upper()

            _m_cond = re.search(
                r'CONEXÃO TIPO\s*["\']?([A-Z]+)["\']?', _c_limpo, re.IGNORECASE
            )
            if _m_cond:
                _tipo_cond = _m_cond.group(1).upper()
                if _tipo_cond in ["B", "C", "E", "LL", "LR", "LB", "TB", "T", "X"]:
                    _dados_df2[_amb][_circ][("", "Conduletes", _tipo_cond)] += 1

    for _e in _ents_all:
        _layer = _e.get("layer", "").upper()
        _cx, _cy = [0, 0]

        if "inicio" in _e.get("dados", {}):
            _cx, _cy = _e["dados"]["inicio"][:2]
        elif "insercao" in _e.get("dados", {}):
            _cx, _cy = _e["dados"]["insercao"][:2]
        elif _e.get("dados", {}).get("vertices", []):
            _cx, _cy = _e["dados"]["vertices"][0][:2]

        _amb = _get_amb_ele(_cx, _cy)

        if "HASTE" in _layer:
            _hastes_aterramento[_amb] += 1
        if "CX. INSPEÇÃO" in _layer or "CAIXA" in _layer:
            _caixas_aterramento[_amb] += 1

        if _e.get("tipo") == "INSERT":
            _nome_bloco = _e.get("dados", {}).get("nome", "").upper()
            if "TOMADA" in _nome_bloco or "TUG" in _nome_bloco:
                _dados_df2[_amb]["GERAL"][("", "tomadas", "Quantidade")] += 1
                _dados_df2[_amb]["GERAL"][("", "tomadas", "Tipo")] = "Padrão"
            elif "LUMIN" in _nome_bloco or "LED" in _nome_bloco:
                _dados_df2[_amb]["GERAL"][("", "Luminárias", "Quantidade")] += 1
                _dados_df2[_amb]["GERAL"][("", "Luminárias", "Tipo")] = "Plafon/LED"

    for _amb, _qtd in _hastes_aterramento.items():
        _dados_df2[_amb]["GERAL"][("Aterramento", "Haste", "Quantidade")] = _qtd
    for _amb, _qtd in _caixas_aterramento.items():
        _dados_df2[_amb]["GERAL"][
            ("Aterramento", "Caixa Inspeção", "Quantidade")
        ] = _qtd

    for _amb, _circs in _dados_df2.items():
        for _circ, _colunas_valores in _circs.items():
            _idx = len(df2)
            df2.loc[_idx, ("", "", "Ambiente")] = _amb
            df2.loc[_idx, ("", "", "Circuito")] = _circ
            for _col, _val in _colunas_valores.items():
                df2.loc[_idx, _col] = _val

    tabela_map = {
        "Circuitos Aéreos": df,
        "Circuitos Subterrâneos": df1,
        "Circuitos Internos": df2,
    }
    return tabela_map
