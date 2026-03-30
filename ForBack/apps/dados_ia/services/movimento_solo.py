from openpyxl.cell.cell import MergedCell

MAX_AMBIENTES = 80
SOLO_LINHA_TERRAPLANAGEM = 17   
SOLO_LINHA_ATERRO        = 43  
SOLO_LINHA_ENROCAMENTO   = 69 
SOLO_LINHA_CONTENCAO     = 95  
SOLO_LINHA_TALUDAMENTO   = 121  
SOLO_LINHA_NIVELAMENTO   = 148  
TERRA_COL_AMB    = 2
TERRA_COL_TIPO   = 5
TERRA_COL_H      = 9
TERRA_COL_LASTRO = 10
TERRA_COL_V      = 12
SOLO_COL_AMB = 2
SOLO_COL_I   = 5
SOLO_COL_V   = 10


def _escrever(ws, linha, coluna, valor):
    if valor is None:
        return
    celula = ws.cell(row=linha, column=coluna)
    if isinstance(celula, MergedCell):
        for rng in ws.merged_cells.ranges:
            if celula.coordinate in rng:
                ws.cell(row=rng.min_row, column=rng.min_col).value = valor
                return
    else:
        celula.value = valor


def _escrever_linha_padrao(ws, linha, nome, inclinacao, volume):
    _escrever(ws, linha, SOLO_COL_AMB, nome)
    _escrever(ws, linha, SOLO_COL_I,   inclinacao)
    _escrever(ws, linha, SOLO_COL_V,   volume)


def preencher_movimento_solo(wb, ambientes: list):
    if 'Movimento de Solo' not in wb.sheetnames:
        return

    ws = wb['Movimento de Solo']

    for i, amb in enumerate(ambientes[:MAX_AMBIENTES]):
        nome       = amb.get('nome', '')
        inclinacao = float(amb.get('inclinacaoTerreno')     or 0)
        prof_escav = float(amb.get('profundidadeEscavacao') or 0)
        volumes    = amb.get('volumes') or {}

        v_terra = float(volumes.get('terraplanagem') or 0)
        v_escav = float(volumes.get('escavacao')     or 0)
        v_aterro  = float(volumes.get('aterro')      or 0)
        v_enroc   = float(volumes.get('enrocamento') or 0)
        v_cont    = float(volumes.get('contencao')   or 0)
        v_talud   = float(volumes.get('taludamento') or 0)
        v_nivel   = float(volumes.get('nivelamento') or 0)
        v_comp    = float(volumes.get('compactacao') or 0)

        if v_terra or v_escav or prof_escav:
            linha = SOLO_LINHA_TERRAPLANAGEM + i
            _escrever(ws, linha, TERRA_COL_AMB,    nome)
            _escrever(ws, linha, TERRA_COL_TIPO,   'Corte')
            _escrever(ws, linha, TERRA_COL_H,      prof_escav)
            _escrever(ws, linha, TERRA_COL_V,      v_escav) 

        if v_aterro:
            linha = SOLO_LINHA_ATERRO + i
            _escrever_linha_padrao(ws, linha, nome, inclinacao, v_aterro)

        if v_enroc:
            linha = SOLO_LINHA_ENROCAMENTO + i
            _escrever_linha_padrao(ws, linha, nome, None, v_enroc)

        if v_cont:
            linha = SOLO_LINHA_CONTENCAO + i
            _escrever_linha_padrao(ws, linha, nome, None, v_cont)

        if v_talud:
            linha = SOLO_LINHA_TALUDAMENTO + i
            _escrever_linha_padrao(ws, linha, nome, None, v_talud)

        v_nivel_total = round(v_nivel + v_comp, 3)
        if v_nivel_total:
            linha = SOLO_LINHA_NIVELAMENTO + i
            _escrever_linha_padrao(ws, linha, nome, None, v_nivel_total)