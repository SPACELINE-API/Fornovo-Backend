import pandas as pd
import json
import re
import math
from collections import defaultdict

colunas_telefonia = pd.MultiIndex.from_tuples(
    [
        ("", "", "Local"),
        ("Quadros de Rede", "Circuito", ""),
        ("Quadros de Rede", "Tipo", ""),
        ("Quadros de Rede", "Qtd", ""),
        ("Cabeamentos", "Rede", "C [m]"),
        ("Cabeamentos", "Patch Cord", "C [m]"),
        ("Cabeamentos", "Câmera", "C [m]"),
        ("Cabeamentos", "TV", "C [m]"),
        ("Cabeamentos", "Telefonia", "C [m]"),
        ("Dutos", "Eletrocalha", "L [cm]"),
        ("Dutos", "Eletrocalha", "h [cm]"),
        ("Dutos", "Eletrocalha", "C [m]"),
        ("Dutos", "Septo", "Elétrica [cm]"),
        ("Dutos", "Septo", "Lógica [cm]"),
        ("Dutos", "Eletroduto", "DN [mm]"),
        ("Dutos", "Eletroduto", "C [m]"),
        ("Conduletes", "", "B"),
        ("Conduletes", "", "C"),
        ("Conduletes", "", "E"),
        ("Conduletes", "", "LL"),
        ("Conduletes", "", "LR"),
        ("Conduletes", "", "LB"),
        ("Conduletes", "", "TB"),
        ("Conduletes", "", "T"),
        ("Conduletes", "", "X"),
        ("Tomadas", "", "RJ 45"),
        ("Tomadas", "", "Keystone"),
        ("Aterramento", "Haste", "DN [pol]"),
        ("Aterramento", "Haste", "C [m]"),
        ("Aterramento", "Haste", "Qtd"),
        ("Aterramento", "Caixa Inspeção", "Qtd"),
        ("Aterramento", "Caixa Inspeção", "DN [pol]"),
        ("Aterramento", "Caixa Inspeção", "h [mm]"),
    ]
)

def telefonia(json_path, dxf_path):
    df_telefonia = pd.DataFrame(columns=colunas_telefonia)

    with open(json_path, "r", encoding="utf-8") as f:
        dados_manuais = json.load(f)

    with open(dxf_path, "r", encoding="utf-8") as a:
        dados_automaticos = json.load(a)

    _txts_all = dados_automaticos.get("textos", [])
    _ents_all = dados_automaticos.get("entidades", [])

    _ambientes = []
    for _txt in _txts_all:
        _c_limpo = re.sub(r"\\[^;\\]+;", "", _txt.get("conteudo", "")).replace("{", "").replace("}", "").replace(r"\P", " ").strip()
        if "m²" in _c_limpo.lower() and "mm" not in _c_limpo.lower() and _txt.get("posicao"):
            _nome = re.sub(r"\d+[.,]\d+\s*m²", "", _c_limpo, flags=re.IGNORECASE)
            _nome = re.sub(r"P\s*=\s*\d+[.,]\d+\s*M", "", _nome, flags=re.IGNORECASE)
            _nome = re.sub(r"PD\s*=\s*\d+[.,]\d+\s*M", "", _nome, flags=re.IGNORECASE)
            _nome = re.sub(r"\s+", " ", _nome).strip()
            if len(_nome) > 2:
                _ambientes.append({"nome": _nome.upper(), "pos": _txt["posicao"]})

    def _get_amb(cx, cy):
        if not _ambientes:
            return "GERAL"
        return min(_ambientes, key=lambda a: math.hypot(cx - a["pos"][0], cy - a["pos"][1]))["nome"]

    _pos_calhas_rede = []
    _cams_por_amb = defaultdict(int)
    _dutos_logica = defaultdict(lambda: defaultdict(float))

    for t in _txts_all:
        _c_limpo = re.sub(r"\\[^;\\]+;", "", t.get("conteudo", "")).replace("{", "").replace("}", "").replace(r"\P", " ").strip().upper()
        _cx, _cy = t.get("posicao", [0, 0, 0])[:2]

        if "CÂMERA" in _c_limpo or "CFTV" in _c_limpo:
            _amb = _get_amb(_cx, _cy)
            _cams_por_amb[_amb] += 1

        if "ELETROCALHA" in _c_limpo and "100" in _c_limpo and "50" in _c_limpo:
            _pos_calhas_rede.append({"pos": t.get("posicao", [0, 0, 0])})

    def _is_calha_rede(cx, cy, limite=3000):
        if not _pos_calhas_rede:
            return False
        _mais_prox = min(_pos_calhas_rede, key=lambda c: math.hypot(cx - c["pos"][0], cy - c["pos"][1]))
        return math.hypot(cx - _mais_prox["pos"][0], cy - _mais_prox["pos"][1]) < limite

    for e in _ents_all:
        _layer = e.get("layer", "").upper()
        if any(k in _layer for k in ["LOGICA", "LÓGICA", "DADOS", "TELEFONIA", "TV", "CFTV", "REDE"]):
            if e.get("tipo") in ["LINE", "LWPOLYLINE", "POLYLINE"]:
                _comp = e.get("dados", {}).get("comprimento", 0)
                if _comp > 0:
                    _cx, _cy = 0, 0
                    if "inicio" in e.get("dados", {}):
                        _cx, _cy = e.get("dados")["inicio"][:2]
                    elif e.get("dados", {}).get("vertices", []):
                        _cx, _cy = e.get("dados")["vertices"][0][:2]

                    _amb = _get_amb(_cx, _cy)
                    if _is_calha_rede(_cx, _cy):
                        _dutos_logica[_amb]["Calha_10x5"] += _comp
                    else:
                        _dutos_logica[_amb]["Eletroduto_25"] += _comp

    ambientes_manuais = dados_manuais.get("ambientes", [])
    manuais_dict = {i.get("nome", "").upper(): i for i in ambientes_manuais}
    ambientes_cad = set(_dutos_logica.keys()).union(set(_cams_por_amb.keys()))
    all_ambs = set(manuais_dict.keys()).union(ambientes_cad)

    for amb in sorted(all_ambs):
        item = manuais_dict.get(amb, {})
        nome_original = item.get("nome", amb)

        calha_auto = _dutos_logica[amb]["Calha_10x5"]
        tubo_auto = _dutos_logica[amb]["Eletroduto_25"]
        cams_auto = _cams_por_amb[amb]

        cabeamentos = item.get("cabeamentos", [])
        if not cabeamentos and (calha_auto > 0 or tubo_auto > 0 or cams_auto > 0):
            cabeamentos = [{}]

        for cab in cabeamentos:
            idx = len(df_telefonia)

            df_telefonia.loc[idx, ("", "", "Local")] = nome_original
            df_telefonia.loc[idx, ("Quadros de Rede", "Circuito", "")] = cab.get("circuito", "")
            df_telefonia.loc[idx, ("Quadros de Rede", "Tipo", "")] = ""
            df_telefonia.loc[idx, ("Quadros de Rede", "Qtd", "")] = item.get("quadrosRede", "")

            man_rede = cab.get("comprimento", "") if cab.get("circuito", "") in ("dados", "rede") else ""
            auto_rede = round(calha_auto + tubo_auto, 2) if (calha_auto + tubo_auto) > 0 else ""
            df_telefonia.loc[idx, ("Cabeamentos", "Rede", "C [m]")] = auto_rede if auto_rede != "" else man_rede

            df_telefonia.loc[idx, ("Cabeamentos", "Patch Cord", "C [m]")] = item.get("patchCords", "")

            man_cams = item.get("cameras", "")
            auto_cams = cams_auto * 15 if cams_auto > 0 else ""
            df_telefonia.loc[idx, ("Cabeamentos", "Câmera", "C [m]")] = auto_cams if auto_cams != "" else man_cams

            df_telefonia.loc[idx, ("Dutos", "Eletrocalha", "L [cm]")] = 10 if calha_auto > 0 else ""
            df_telefonia.loc[idx, ("Dutos", "Eletrocalha", "h [cm]")] = 5 if calha_auto > 0 else ""
            df_telefonia.loc[idx, ("Dutos", "Eletrocalha", "C [m]")] = round(calha_auto, 2) if calha_auto > 0 else ""

            df_telefonia.loc[idx, ("Dutos", "Septo", "Elétrica [cm]")] = ""
            df_telefonia.loc[idx, ("Dutos", "Septo", "Lógica [cm]")] = ""

            df_telefonia.loc[idx, ("Dutos", "Eletroduto", "DN [mm]")] = 25 if tubo_auto > 0 else ""

            man_tubo = cab.get("comprimento", "")
            auto_tubo = round(tubo_auto, 2) if tubo_auto > 0 else ""
            df_telefonia.loc[idx, ("Dutos", "Eletroduto", "C [m]")] = auto_tubo if auto_tubo != "" else man_tubo

            df_telefonia.loc[idx, ("Conduletes", "", "B")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "C")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "E")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "LL")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "LR")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "LB")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "TB")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "T")] = ""
            df_telefonia.loc[idx, ("Conduletes", "", "X")] = ""

            df_telefonia.loc[idx, ("Tomadas", "", "RJ 45")] = cab.get("tomadas", "")
            df_telefonia.loc[idx, ("Tomadas", "", "Keystone")] = ""

            df_telefonia.loc[idx, ("Aterramento", "Haste", "DN [pol]")] = ""
            df_telefonia.loc[idx, ("Aterramento", "Haste", "C [m]")] = ""
            df_telefonia.loc[idx, ("Aterramento", "Haste", "Qtd")] = item.get("hastesAterramento", "")
            df_telefonia.loc[idx, ("Aterramento", "Caixa Inspeção", "Qtd")] = item.get("caixasInspecao", "")
            df_telefonia.loc[idx, ("Aterramento", "Caixa Inspeção", "DN [pol]")] = ""
            df_telefonia.loc[idx, ("Aterramento", "Caixa Inspeção", "h [mm]")] = ""

    return df_telefonia

if __name__ == "__main__":
    df = telefonia(
        r"C:\Users\vinic\Desktop\lalala.json",
        r"C:\Users\vinic\Downloads\PNR.json"
    )
    print(df)