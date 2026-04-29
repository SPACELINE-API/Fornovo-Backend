import pandas as pd
import json
import os
import re
import math

colunas_servicos_preliminares = pd.MultiIndex.from_tuples(
    [
        ("Limpeza", "A [m²]"),
    ]
)

colunas_servicos_preliminares2 = pd.MultiIndex.from_tuples(
    [
        ("Serviços", "Banheiros químicos [Un]"),
        ("Serviços", "Andaimes [Un]"),
        ("Serviços", "Contêineres [Un]"),
    ]
)

colunas_servicos_preliminares3 = pd.MultiIndex.from_tuples(
    [
        ("", "Fase"),
        ("", "Ambiente"),
        ("", "Local"),
        ("", "A [m²]"),
    ]
)

colunas_servicos_preliminares4 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Elétrica/SPDA/Rede", "Condulete [m]"),
        ("Elétrica/SPDA/Rede", "Tomadas [Un]"),
        ("Elétrica/SPDA/Rede", "Interruptor [Un]"),
        ("Elétrica/SPDA/Rede", "Luminária [Un]"),
        ("Elétrica/SPDA/Rede", "Dutos [m]"),
        ("Elétrica/SPDA/Rede", "Cabos [m]"),
        ("Elétrica/SPDA/Rede", "Captação [m]"),
        ("Elétrica/SPDA/Rede", "Aterra/o [m]"),
        ("Elétrica/SPDA/Rede", "Quadros [Un]"),
        ("Elétrica/SPDA/Rede", "Postes"),
        (
            "Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio",
            "Cavalete [Un]",
        ),
        (
            "Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio",
            "Reservat [Un]",
        ),
        (
            "Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio",
            "Registros [Un]",
        ),
        (
            "Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio",
            "Válvulas [Un]",
        ),
        (
            "Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio",
            "Torneiras [Un]",
        ),
        ("Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio", "Dutos [m]"),
        ("Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio", "Calhas [m]"),
        ("Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio", "Caixas [Un]"),
        ("Água Fria/Água Pluvial/Esgoto/Pressurizadas/Contra Incêndio", "Drenos [Un]"),
        ("Esquadrias", "Portas [m²]"),
        ("Esquadrias", "Janelas [m²]"),
        ("Telhados", "Telha [m²]"),
        ("Telhados", "Trama [m²]"),
        ("Telhados", "Tesoura [Un]"),
        ("Equipamentos/Acessórios", "Item"),
        ("Equipamentos/Acessórios", "Qnt [Un]"),
    ]
)

colunas_servicos_preliminares5 = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("", "Piso [m²]"),
        ("", "Rodapé [m²]"),
        ("", "Azulejo [m²]"),
        ("", "Forro [m²]"),
        ("Alvenaria", "Tipo"),
        ("Alvenaria", "V [m³]"),
        ("Estrutura", "Fundação [m³]"),
        ("Estrutura", "Pilar [m³]"),
        ("Estrutura", "Viga [m³]"),
        ("Estrutura", "Laje [m³]"),
    ]
)

colunas_servicos_preliminares6 = pd.MultiIndex.from_tuples(
    [("Resíduo", "Comum V [m³]"), ("Resíduo", "Contaminado V [m³]"), ("", "Destino")]
)


def servicos_preliminares(dados_manuais, dados_automaticos):
    df = pd.DataFrame(columns=colunas_servicos_preliminares)
    df2 = pd.DataFrame(columns=colunas_servicos_preliminares2)
    df3 = pd.DataFrame(columns=colunas_servicos_preliminares3)
    df4 = pd.DataFrame(columns=colunas_servicos_preliminares4)
    df5 = pd.DataFrame(columns=colunas_servicos_preliminares5)
    df6 = pd.DataFrame(columns=colunas_servicos_preliminares6)

    df.loc[0, ("Limpeza", "A [m²]")] = 0.00

    total_banheiros = 0
    total_andaimes = 0
    total_conteineres = 0

    for item in dados_manuais.get("ambientes", []):
        total_banheiros += item.get("banheirosQuimicos", 0)
        total_andaimes += item.get("andaimes", 0)
        total_conteineres += item.get("conteineres", 0)

    df2.loc[0, ("Serviços", "Banheiros químicos [Un]")] = total_banheiros
    df2.loc[0, ("Serviços", "Andaimes [Un]")] = total_andaimes
    df2.loc[0, ("Serviços", "Contêineres [Un]")] = total_conteineres

    idx_linha3 = 0
    for item in dados_manuais.get("ambientes", []):
        df3.loc[idx_linha3, ("", "Fase")] = ""
        df3.loc[idx_linha3, ("", "Ambiente")] = ""
        df3.loc[idx_linha3, ("", "Local")] = ""
        df3.loc[idx_linha3, ("", "A [m²]")] = 0
        idx_linha3 += 1

    df3.loc[idx_linha3, ("", "Fase")] = ""
    df3.loc[idx_linha3, ("", "Ambiente")] = ""
    df3.loc[idx_linha3, ("", "Local")] = "Total"
    df3.loc[idx_linha3, ("", "A [m²]")] = df3[("", "A [m²]")].sum()

    residuo_comum = 0
    residuo_contaminado = 0
    destinos = set()

    for item in dados_manuais.get("ambientes", []):
        residuo_comum += item.get("residuoComum", 0)
        residuo_contaminado += item.get("residuoContaminado", 0)

        destino_atual = item.get("destinacaoResiduo", "")
        if destino_atual:
            destinos.add(str(destino_atual).strip())

    destino_final = ", ".join(sorted(destinos))

    df6.loc[0, ("Resíduo", "Comum V [m³]")] = residuo_comum
    df6.loc[0, ("Resíduo", "Contaminado V [m³]")] = residuo_contaminado
    df6.loc[0, ("", "Destino")] = destino_final

    # ── ambientes_cad: posições dos textos de ambiente no CAD ──────────
    ambientes_cad_sp = []
    for _txt in dados_automaticos.get("textos", []):
        _c = _txt.get("conteudo", "")
        if "m²" in _c.lower():
            _ma = re.search(r"(\d+[.,]\d+)\s*m²", _c, re.IGNORECASE)
            if _ma:
                _parts = _c.split("\\P")
                _aidx = -1
                for _ip, _ps in enumerate(_parts):
                    if re.search(r"\d+[.,]\d+\s*m²", _ps, re.IGNORECASE):
                        _aidx = _ip
                        break
                _raw = " ".join(_parts[:_aidx]) if _aidx > 0 else _parts[0]
                _nome = (
                    re.sub(r"\\[^;\\]+;", "", _raw).replace("{", "").replace("}", "")
                )
                _nome = re.sub(r"\\[Pp]", " ", _nome)
                _nome = re.sub(r"\d+[.,]\d+\s*m²", "", _nome, flags=re.IGNORECASE)
                _nome = re.sub(r"\s+", " ", _nome).strip()
                if _nome and _txt.get("posicao"):
                    ambientes_cad_sp.append({"nome": _nome, "pos": _txt["posicao"]})

    def _get_amb_sp(cx, cy, threshold=200):
        if not ambientes_cad_sp:
            return "Não identificado"
        best = min(
            ambientes_cad_sp,
            key=lambda a: math.hypot(cx - a["pos"][0], cy - a["pos"][1]),
        )
        return (
            best["nome"]
            if math.hypot(cx - best["pos"][0], cy - best["pos"][1]) <= threshold
            else "Não identificado"
        )

    _textos_auto = dados_automaticos.get("textos", [])
    _entidades_auto = dados_automaticos.get("entidades", [])

    # ── 1. Alvenaria a demolir — comprimento por ambiente ─────────────
    _alv_dem_lines = [
        e
        for e in _entidades_auto
        if e.get("layer") == "ARQ - Alvenaria (-)"
        and e.get("tipo") == "LINE"
        and "dados" in e
    ]
    _alv_por_amb = {}
    for _e in _alv_dem_lines:
        _cx = (_e["dados"]["inicio"][0] + _e["dados"]["fim"][0]) / 2
        _cy = (_e["dados"]["inicio"][1] + _e["dados"]["fim"][1]) / 2
        _amb = _get_amb_sp(_cx, _cy)
        _alv_por_amb[_amb] = _alv_por_amb.get(_amb, 0.0) + _e["dados"].get(
            "comprimento", 0.0
        )

    # ── 2. Telhados existentes — área por nome (dedup) ────────────────
    _telh_areas = {}
    for _t in _textos_auto:
        _c = _t.get("conteudo", "")
        if "telhado" in _c.lower() and "existente" in _c.lower():
            _ma = re.search(r"(\d+[.,]\d+)\s*m²", _c)
            if _ma:
                _mn = re.search(r"TELHADO\s+(\d+)", _c, re.IGNORECASE)
                _key = f"TELHADO {_mn.group(1)}" if _mn else "TELHADO"
                _telh_areas[_key] = float(_ma.group(1).replace(",", "."))

    # ── 3. Postes a remover — por ambiente ────────────────────────────
    _postes_rem = {}
    for _t in _textos_auto:
        if "poste a remover" in _t.get("conteudo", "").lower() and _t.get("posicao"):
            _cx, _cy = _t["posicao"][:2]
            _amb = _get_amb_sp(_cx, _cy)
            _postes_rem[_amb] = _postes_rem.get(_amb, 0) + 1

    # ── 4. Grades a remover — por ambiente ────────────────────────────
    _grades_rem = {}
    for _t in _textos_auto:
        if "grade a remover" in _t.get("conteudo", "").lower() and _t.get("posicao"):
            _cx, _cy = _t["posicao"][:2]
            _amb = _get_amb_sp(_cx, _cy)
            _grades_rem[_amb] = _grades_rem.get(_amb, 0) + 1

    # ── 5. Fiação/duto enterrado a remover — por ambiente ─────────────
    _fiacao_rem = {}
    for _t in _textos_auto:
        if "fiação/duto enterrado a remover" in _t.get(
            "conteudo", ""
        ).lower() and _t.get("posicao"):
            _cx, _cy = _t["posicao"][:2]
            _amb = _get_amb_sp(_cx, _cy)
            _fiacao_rem[_amb] = _fiacao_rem.get(_amb, 0) + 1

    _jan_rem_txts = [
        _t
        for _t in _textos_auto
        if "janelas a remover" in _t.get("conteudo", "").lower() and _t.get("posicao")
    ]
    _jan_rem_por_amb = {}
    for _t in _jan_rem_txts:
        _cx, _cy = _t["posicao"][:2]
        _amb = _get_amb_sp(_cx, _cy)
        _jan_rem_por_amb[_amb] = _jan_rem_por_amb.get(_amb, 0) + 1

    _txts_qa = [
        _t
        for _t in _textos_auto
        if _t.get("layer") == "Símbolos - Quadro de Acabamentos" and _t.get("posicao")
    ]
    _id_pat = re.compile(r"^([PpJj][A-Za-z]\d*)$")
    _num_pat = re.compile(r"^\d+$")
    _esq_por_id = {}
    for _t in _txts_qa:
        _cv = _t["conteudo"].strip()
        if _id_pat.match(_cv):
            _pos = _t["posicao"]
            _cands = [
                _u
                for _u in _txts_qa
                if _num_pat.match(_u["conteudo"].strip())
                and _u.get("posicao")
                and abs(_u["posicao"][1] - _pos[1]) < 2.0
                and _u["posicao"][0] > _pos[0]
            ]
            _qtd = (
                int(
                    min(_cands, key=lambda _u: abs(_u["posicao"][0] - _pos[0]))[
                        "conteudo"
                    ]
                )
                if _cands
                else 1
            )
            _esq_por_id[_cv] = _esq_por_id.get(_cv, 0) + _qtd

    _total_portas = sum(
        _v for _k, _v in _esq_por_id.items() if _k.upper().startswith("P")
    )
    _total_janelas = sum(
        _v for _k, _v in _esq_por_id.items() if _k.upper().startswith("J")
    )

    idx_linha4 = 0

    for _amb, _comp in sorted(_alv_por_amb.items()):
        df4.loc[idx_linha4, ("", "Ambiente")] = f"{_amb} — alvenaria a remover"
        idx_linha4 += 1

    for _nome_telh, _area in sorted(_telh_areas.items()):
        df4.loc[idx_linha4, ("", "Ambiente")] = f"{_nome_telh} — a remover"
        df4.loc[idx_linha4, ("Telhados", "Telha [m²]")] = _area
        idx_linha4 += 1

    for _amb, _qtd in sorted(_postes_rem.items()):
        df4.loc[idx_linha4, ("", "Ambiente")] = f"{_amb} — poste a remover"
        df4.loc[idx_linha4, ("Elétrica/SPDA/Rede", "Postes")] = _qtd
        idx_linha4 += 1

    for _amb, _qtd in sorted(_grades_rem.items()):
        df4.loc[idx_linha4, ("", "Ambiente")] = f"{_amb} — grade a remover"
        df4.loc[idx_linha4, ("Equipamentos/Acessórios", "Item")] = "Grade"
        df4.loc[idx_linha4, ("Equipamentos/Acessórios", "Qnt [Un]")] = _qtd
        idx_linha4 += 1

    for _amb, _qtd in sorted(_fiacao_rem.items()):
        df4.loc[idx_linha4, ("", "Ambiente")] = f"{_amb} — fiação/duto a remover"
        df4.loc[idx_linha4, ("Elétrica/SPDA/Rede", "Dutos [m]")] = _qtd
        idx_linha4 += 1

    for _amb, _qtd in sorted(_jan_rem_por_amb.items()):
        df4.loc[idx_linha4, ("", "Ambiente")] = f"{_amb} — janelas a remover"
        df4.loc[idx_linha4, ("Esquadrias", "Janelas [m²]")] = _qtd
        idx_linha4 += 1

    if _total_portas > 0:
        df4.loc[idx_linha4, ("", "Ambiente")] = "Esquadrias a remover — portas"
        df4.loc[idx_linha4, ("Esquadrias", "Portas [m²]")] = _total_portas
        idx_linha4 += 1

    if _total_janelas > 0:
        df4.loc[idx_linha4, ("", "Ambiente")] = "Esquadrias a remover — janelas"
        df4.loc[idx_linha4, ("Esquadrias", "Janelas [m²]")] = _total_janelas
        idx_linha4 += 1

    _area_por_amb = {}
    for _a in ambientes_cad_sp:
        _n = _a["nome"]
        _ar = _a.get("area", 0)
        if _n not in _area_por_amb or _ar > _area_por_amb[_n]:
            _area_por_amb[_n] = _ar

    _alv5_lines = [
        e
        for e in _entidades_auto
        if e.get("layer") == "ARQ - Alvenaria (-)"
        and e.get("tipo") == "LINE"
        and "dados" in e
    ]
    _alv5_por_amb = {}
    for _e in _alv5_lines:
        _cx = (_e["dados"]["inicio"][0] + _e["dados"]["fim"][0]) / 2
        _cy = (_e["dados"]["inicio"][1] + _e["dados"]["fim"][1]) / 2
        _amb = _get_amb_sp(_cx, _cy)
        _alv5_por_amb[_amb] = _alv5_por_amb.get(_amb, 0.0) + _e["dados"].get(
            "comprimento", 0.0
        )

    def _comp_por_amb5(layer):
        _r = {}
        for _e in _entidades_auto:
            if (
                _e.get("layer") != layer
                or _e.get("tipo") != "LINE"
                or "dados" not in _e
            ):
                continue
            _cx = (_e["dados"]["inicio"][0] + _e["dados"]["fim"][0]) / 2
            _cy = (_e["dados"]["inicio"][1] + _e["dados"]["fim"][1]) / 2
            _a = _get_amb_sp(_cx, _cy)
            _r[_a] = _r.get(_a, 0.0) + _e["dados"].get("comprimento", 0.0)
        return _r

    _pilares5_amb = _comp_por_amb5("Estrutural - Pilares")
    _fundacoes5_amb = _comp_por_amb5("Estrutural - Fundações")
    _vigas5_amb = _comp_por_amb5("Estrutural - Vigas")
    _lajes5_amb = _comp_por_amb5("Estrutural - Lajes")

    _demolir_txt_por_amb = {}
    for _t in _textos_auto:
        _c_raw = _t.get("conteudo", "")
        if "demolir" not in _c_raw.lower():
            continue
        _c_clean = re.sub(r"\\[a-zA-Z0-9]+;?", "", _c_raw)
        _c_clean = re.sub(r"[{}]", "", _c_clean).strip()
        _pos = _t.get("posicao")
        _amb = _get_amb_sp(_pos[0], _pos[1]) if _pos else "Não identificado"
        _demolir_txt_por_amb.setdefault(_amb, set()).add(_c_clean)

    _ambientes5 = (
        set(_alv5_por_amb)
        | set(_pilares5_amb)
        | set(_fundacoes5_amb)
        | set(_vigas5_amb)
        | set(_lajes5_amb)
        | set(_demolir_txt_por_amb)
    )

    _ESP_ALV = 0.15
    _H_ALV = 3.0

    idx_linha5 = 0
    for _amb in sorted(_ambientes5):
        _area = _area_por_amb.get(_amb, "")

        _rotulo_demolir = (
            " / ".join(sorted(_demolir_txt_por_amb[_amb]))
            if _amb in _demolir_txt_por_amb
            else "a demolir"
        )
        df5.loc[idx_linha5, ("", "Ambiente")] = f"{_amb} — {_rotulo_demolir}"
        df5.loc[idx_linha5, ("", "Piso [m²]")] = _area
        df5.loc[idx_linha5, ("", "Rodapé [m²]")] = _area
        df5.loc[idx_linha5, ("", "Azulejo [m²]")] = _area
        df5.loc[idx_linha5, ("", "Forro [m²]")] = _area

        if _amb in _alv5_por_amb:
            _comp_alv = _alv5_por_amb[_amb]
            df5.loc[idx_linha5, ("Alvenaria", "Tipo")] = "ARQ - Alvenaria (-)"
            df5.loc[idx_linha5, ("Alvenaria", "V [m³]")] = round(
                _comp_alv * _ESP_ALV * _H_ALV, 3
            )

        if _amb in _pilares5_amb:
            df5.loc[idx_linha5, ("Estrutura", "Pilar [m³]")] = round(
                _pilares5_amb[_amb], 3
            )
        if _amb in _fundacoes5_amb:
            df5.loc[idx_linha5, ("Estrutura", "Fundação [m³]")] = round(
                _fundacoes5_amb[_amb], 3
            )
        if _amb in _vigas5_amb:
            df5.loc[idx_linha5, ("Estrutura", "Viga [m³]")] = round(
                _vigas5_amb[_amb], 3
            )
        if _amb in _lajes5_amb:
            df5.loc[idx_linha5, ("Estrutura", "Laje [m³]")] = round(
                _lajes5_amb[_amb], 3
            )

        idx_linha5 += 1

    return df, df2, df3, df4, df5, df6
