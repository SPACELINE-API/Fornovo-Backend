import pandas as pd
import json
import os
import re
import math
from collections import defaultdict

colunas_seguranca = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),
        ("Terminais", "", "Qnt"),
        ("Terminais", "Dimensões", "L [pol]"),
        ("Terminais", "Dimensões", "e [pol]"),
        ("Terminais", "Dimensões", "C [mm]"),
        ("Captação", "", "Barra [m]"),
        ("Captação", "", "Cordoalha [m]"),
        ("Captação", "", "Duto [m]"),
        ("Captação", "", "Terminal Compressão"),
        ("Captação", "", "Fixação"),
        ("Equalização", "", "Cordoalha"),
        ("Equalização", "", "Grampo"),
        ("Aterramento", "Haste", "DN [pol]"),
        ("Aterramento", "Haste", "C [m]"),
        ("Aterramento", "Haste", "Qnt"),
        ("Aterramento", "Caixa Inspeção", "Qnt"),
        ("Aterramento", "Caixa Inspeção", "DN [pol]"),
        ("Aterramento", "Caixa Inspeção", "h [mm]"),
    ]
)

colunas_seguranca1 = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),
        ("", "Extintores Portáteis", "Local"),
        ("", "Extintores Portáteis", "Tipo"),
        ("", "Extintores Portáteis", "Peso [KgF]"),
        ("", "Extintores Portáteis", "Cpcd Extint"),
        ("", "Extintores Portáteis", "Qnt"),
        ("Hidrantes", "", "Qnt"),
        ("Hidrantes", "Dimensões", "L [cm]"),
        ("Hidrantes", "Dimensões", "Prof [m]"),
        ("Hidrantes", "Dimensões", "h [cm]"),
        ("Hidrantes", "Visor", "L [cm]"),
        ("Hidrantes", "Visor", "e [mm]"),
        ("Hidrantes", "Visor", "C [cm]"),
        ("Hidrantes", "Duto de Contra Incêndio", "DN [pol]"),
        ("Hidrantes", "Duto de Contra Incêndio", "h [cm]"),
        ("Hidrantes", "Duto de Contra Incêndio", "C [m]"),
        ("Hidrantes", "Registro", "DN [pol]"),
        ("Hidrantes", "Registro", "Qnt"),
        ("Hidrantes", "Válvula", "DN [pol]"),
        ("Hidrantes", "Válvula", "Qnt"),
        ("Conexões", "", "Tipo"),
        ("Conexões", "Joelhos", "90"),
        ("Conexões", "Joelhos", "45"),
        ("Conexões", "Curva", "90"),
        ("Conexões", "Luvas", "Simples"),
        ("Conexões", "Luvas", "Redução"),
        ("Conexões", "Tês", "Simples"),
        ("Conexões", "Tês", "Redução"),
        ("Conexões", "Junções", "45"),
        ("Conexões", "Junções", "Redução"),
    ]
)


def seguranca(dados_automaticos):
    df = pd.DataFrame(columns=colunas_seguranca)
    df1 = pd.DataFrame(columns=colunas_seguranca1)

    _txts_all = dados_automaticos.get("textos", [])
    _ents_all = dados_automaticos.get("entidades", [])

    _ambientes = []
    for _txt in _txts_all:
        _c_limpo = (
            re.sub(r"\\[^;\\]+;", "", _txt.get("conteudo", ""))
            .replace("{", "")
            .replace("}", "")
            .replace(r"\P", " ")
            .strip()
        )
        if (
            "m²" in _c_limpo.lower()
            and "mm" not in _c_limpo.lower()
            and _txt.get("posicao")
        ):
            _nome = re.sub(r"\d+[.,]\d+\s*m²", "", _c_limpo, flags=re.IGNORECASE)
            _nome = re.sub(r"P\s*=\s*\d+[.,]\d+\s*M", "", _nome, flags=re.IGNORECASE)
            _nome = re.sub(r"PD\s*=\s*\d+[.,]\d+\s*M", "", _nome, flags=re.IGNORECASE)
            _nome = re.sub(r"\s+", " ", _nome).strip()
            if len(_nome) > 2:
                _ambientes.append({"nome": _nome.upper(), "pos": _txt["posicao"]})

    def _get_amb(cx, cy, limite=6000):
        if not _ambientes:
            return "GERAL"
        _mais_prox = min(
            _ambientes, key=lambda a: math.hypot(cx - a["pos"][0], cy - a["pos"][1])
        )
        if math.hypot(cx - _mais_prox["pos"][0], cy - _mais_prox["pos"][1]) > limite:
            return "GERAL"
        return _mais_prox["nome"]

    _spda_dados = defaultdict(lambda: defaultdict(float))
    _incendio_dados = defaultdict(lambda: defaultdict(float))
    _extintores = defaultdict(list)

    for e in _ents_all:
        _layer = e.get("layer", "").upper()
        _tipo = e.get("tipo", "")

        _cx, _cy = [0, 0]
        if "inicio" in e.get("dados", {}):
            _cx, _cy = e["dados"]["inicio"][:2]
        elif e.get("dados", {}).get("vertices", []):
            _cx, _cy = e["dados"]["vertices"][0][:2]

        _amb = _get_amb(_cx, _cy)

        if _tipo in ["LINE", "LWPOLYLINE", "POLYLINE"]:
            _comp = e.get("dados", {}).get("comprimento", 0)
            if _comp > 0:
                if "BARRA CHATA" in _layer:
                    _spda_dados[_amb][("Captação", "", "Barra [m]")] += _comp
                elif "MALHA SPDA" in _layer:
                    _spda_dados[_amb][("Captação", "", "Cordoalha [m]")] += _comp
                elif "TUBO DESCIDA" in _layer:
                    _spda_dados[_amb][("Captação", "", "Duto [m]")] += _comp
                elif "MALHA TERRA" in _layer:
                    _spda_dados[_amb][("Equalização", "", "Cordoalha")] += _comp
                elif "CONTRA INCÊNDIO" in _layer:
                    _incendio_dados[_amb][
                        ("Hidrantes", "Duto de Contra Incêndio", "C [m]")
                    ] += _comp

        if "FIXADOR GELCAM" in _layer:
            _spda_dados[_amb][("Captação", "", "Fixação")] += 1
        elif "TERMINAL COMPRESSÃO" in _layer:
            _spda_dados[_amb][("Captação", "", "Terminal Compressão")] += 1
        elif "HASTE" in _layer:
            _spda_dados[_amb][("Aterramento", "Haste", "Qnt")] += 0.25
        elif "INSPEÇÃO" in _layer:
            _spda_dados[_amb][("Aterramento", "Caixa Inspeção", "Qnt")] += 0.25

    for t in _txts_all:
        _c_original = t.get("conteudo", "")
        _c_limpo = (
            re.sub(r"\\[^;\\]+;", "", _c_original)
            .replace("{", "")
            .replace("}", "")
            .replace(r"\P", " ")
        )
        _c_upper = _c_limpo.upper()
        _cx, _cy = t.get("posicao", [0, 0, 0])[:2]
        _amb = _get_amb(_cx, _cy)

        if "EXTINTOR" in _c_upper:
            _tipo_ext = "ÁGUA"
            _peso_ext = ""
            if "PQS" in _c_upper or "PÓ" in _c_upper:
                _tipo_ext = "PQS ABC"
            elif "CO2" in _c_upper:
                _tipo_ext = "CO2"

            _m_peso = re.search(r"(\d+)\s*(KG|L)", _c_upper)
            if _m_peso:
                _peso_ext = _m_peso.group(1)

            _extintores[_amb].append({"tipo": _tipo_ext, "peso": _peso_ext})

    all_ambs = (
        set(_spda_dados.keys()) | set(_incendio_dados.keys()) | set(_extintores.keys())
    )
    if not all_ambs:
        all_ambs.add("GERAL")

    for amb in sorted(all_ambs):
        idx = len(df)
        df.loc[idx, ("", "", "Ambiente")] = amb

        df.loc[idx, ("Captação", "", "Barra [m]")] = round(
            _spda_dados[amb][("Captação", "", "Barra [m]")], 2
        )
        df.loc[idx, ("Captação", "", "Cordoalha [m]")] = round(
            _spda_dados[amb][("Captação", "", "Cordoalha [m]")], 2
        )
        df.loc[idx, ("Captação", "", "Duto [m]")] = round(
            _spda_dados[amb][("Captação", "", "Duto [m]")], 2
        )
        df.loc[idx, ("Captação", "", "Terminal Compressão")] = math.ceil(
            _spda_dados[amb][("Captação", "", "Terminal Compressão")]
        )
        df.loc[idx, ("Captação", "", "Fixação")] = math.ceil(
            _spda_dados[amb][("Captação", "", "Fixação")]
        )
        df.loc[idx, ("Equalização", "", "Cordoalha")] = round(
            _spda_dados[amb][("Equalização", "", "Cordoalha")], 2
        )
        df.loc[idx, ("Aterramento", "Haste", "Qnt")] = math.ceil(
            _spda_dados[amb][("Aterramento", "Haste", "Qnt")]
        )
        df.loc[idx, ("Aterramento", "Caixa Inspeção", "Qnt")] = math.ceil(
            _spda_dados[amb][("Aterramento", "Caixa Inspeção", "Qnt")]
        )

        idx1 = len(df1)
        df1.loc[idx1, ("", "", "Ambiente")] = amb

        ext_list = _extintores[amb]
        if ext_list:
            df1.loc[idx1, ("", "Extintores Portáteis", "Local")] = "Piso/Parede"
            df1.loc[idx1, ("", "Extintores Portáteis", "Tipo")] = ext_list[0]["tipo"]
            df1.loc[idx1, ("", "Extintores Portáteis", "Peso [KgF]")] = ext_list[0][
                "peso"
            ]
            df1.loc[idx1, ("", "Extintores Portáteis", "Qnt")] = len(ext_list)

        df1.loc[idx1, ("Hidrantes", "Duto de Contra Incêndio", "C [m]")] = round(
            _incendio_dados[amb][("Hidrantes", "Duto de Contra Incêndio", "C [m]")], 2
        )

    return df, df1
