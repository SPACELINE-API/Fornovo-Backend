import pandas as pd
import os

from .inst_telefonia import telefonia
from .levantamento_campo import levantamento_campo
from .movimentosolo_manual import movimento_solo
from .serviços_preliminares import servicos_preliminares
from .estruturas_manual import estruturas
from .alvenarias import alvenarias
from .acabamentos import acabamentos
from .inst_eletricas import eletricas
from .inst_mecanica import mecanica
from .inst_pressurizadas import pressurizada
from .inst_segurança import seguranca
from .comunicações_ambientais import ambientais
from .paisagismos import paisagismo

def exportar_tabelas(mapa_abas, destino):
    writer = pd.ExcelWriter(destino, engine='xlsxwriter')
    workbook = writer.book
    
    fmt_nome_sheet = workbook.add_format({
        'bold': True, 
        'font_size': 16, 
        'font_color': '#2F5597'
    })
    fmt_titulo_secao = workbook.add_format({'bold': True, 'font_size': 12})
    fmt_header = workbook.add_format({
        'bold': True, 'border': 1, 'border_color': 'black',
        'align': 'center', 'valign': 'vcenter', 'bg_color': '#E0E0E0', 'text_wrap': True
    })
    fmt_corpo = workbook.add_format({
        'border': 1, 'border_color': 'black',
        'align': 'left', 'valign': 'vcenter'
    })

    s_row_ini = 3
    s_col_ini = 1

    for nome_aba, conteudo in mapa_abas.items():
        aba_limpa = nome_aba[:31]
        worksheet = workbook.add_worksheet(aba_limpa)
        writer.sheets[aba_limpa] = worksheet
        
        worksheet.write(1, s_col_ini, nome_aba.upper(), fmt_nome_sheet)
        
        current_row = s_row_ini

        if isinstance(conteudo, dict):
            itens = [(titulo, dados[0]) for titulo, dados in conteudo.items()]
        elif isinstance(conteudo, list):
            itens = []
            for item in conteudo:
                if isinstance(item, tuple):
                    itens.append(item)
                else:
                    itens.append((None, item))
        else:
            itens = [(None, conteudo)]

        for titulo, df in itens:
            if df is None or df.empty:
                continue

            if titulo:
                worksheet.write(current_row, s_col_ini, titulo, fmt_titulo_secao)
                current_row += 1

            n_rows, n_cols = df.shape
            
            if isinstance(df.columns, pd.MultiIndex):
                n_niveis = df.columns.nlevels
                for lvl in range(n_niveis):
                    labels = df.columns.get_level_values(lvl)
                    i = 0
                    while i < n_cols:
                        j = i + 1
                        while j < n_cols and labels[j] == labels[i]:
                            j += 1
                        texto = str(labels[i]) if pd.notnull(labels[i]) and "Unnamed" not in str(labels[i]) else ""
                        r, c1, c2 = current_row + lvl, s_col_ini + i, s_col_ini + j - 1
                        
                        if j - i > 1 and texto != "":
                            worksheet.merge_range(r, c1, r, c2, texto, fmt_header)
                        else:
                            worksheet.write(r, c1, texto, fmt_header)
                        i = j
                start_data = current_row + n_niveis
            else:
                for c_idx, col in enumerate(df.columns):
                    worksheet.write(current_row, s_col_ini + c_idx, str(col), fmt_header)
                start_data = current_row + 1

            df_exp = df.copy()
            df_exp.columns = range(n_cols)
            df_exp.to_excel(writer, sheet_name=aba_limpa, startrow=start_data, 
                            startcol=s_col_ini, index=False, header=False)

            if n_rows > 0:
                area = (start_data, s_col_ini, start_data + n_rows - 1, s_col_ini + n_cols - 1)
                worksheet.conditional_format(*area, {'type': 'no_blanks', 'format': fmt_corpo})
                worksheet.conditional_format(*area, {'type': 'blanks', 'format': fmt_corpo})

            for i in range(n_cols):
                col_data = df.iloc[:, i]
                serie_len = col_data.apply(lambda x: len(str(x)) if pd.notnull(x) and not isinstance(x, (pd.Series, pd.DataFrame)) else 0)
                max_d = serie_len.max() if not serie_len.empty else 0
                
                if isinstance(df.columns, pd.MultiIndex):
                    max_h = max([len(str(df.columns[i][lvl])) if pd.notnull(df.columns[i][lvl]) else 0 
                                 for lvl in range(df.columns.nlevels)])
                else:
                    max_h = len(str(df.columns[i]))
                
                largura_final = max(int(max_d), max_h) + 5
                worksheet.set_column(s_col_ini + i, s_col_ini + i, min(largura_final, 100))

            current_row = start_data + n_rows + 3

    writer.close()

def gerar_memorial(path_man, path_cad, destino_pasta):
    dfs_levantamento = list(levantamento_campo(path_man, path_cad))
    df_servicos = list(servicos_preliminares(path_man, path_cad))
    tabela_map_solo = movimento_solo(path_man, path_cad)
    tabela_map_estruturas = estruturas(path_man, path_cad)
    tabela_map_alvenarias = alvenarias(path_man, path_cad)
    df_acabamentos = list(acabamentos(path_man, path_cad))
    tabela_map_eletrica = eletricas(path_man, path_cad)
    df_mecanica = list(mecanica())
    df_pressurizada = pressurizada()
    df_seguranca = list(seguranca(path_cad))
    df_ambientais = ambientais()
    df_tel = telefonia(path_man, path_cad)
    df_paisagismo = paisagismo()

    mapa_abas = {
        "Levantamento de Campo": dfs_levantamento,
        "Serviços Preliminares": df_servicos,
        "Movimento de Solo": tabela_map_solo,
        "Estruturas": tabela_map_estruturas,
        "Alvenarias": tabela_map_alvenarias,
        "Acabamentos": df_acabamentos,
        "Inst. Hidraulica": [],
        "Inst. Elétricas": tabela_map_eletrica,
        "Inst. de Telefonia e Rede": df_tel,
        "Inst. Mecânicas": df_mecanica,
        "Inst. Pressurizadas": df_pressurizada,
        "Inst. de Segurança": df_seguranca,
        "Comunicações Ambientais": df_ambientais,
        "Paisagismos": df_paisagismo,
        "Entrega de obra": []
    }

    arquivo_final = os.path.join(destino_pasta, "memorial_descritivo_completo.xlsx")
    if os.path.exists(arquivo_final):
        os.remove(arquivo_final)
    
    exportar_tabelas(mapa_abas, arquivo_final)
    return arquivo_final

if __name__ == "__main__":
    path_tables = r"C:\Users\vinic\Desktop\Material Fatec\API_4_Semestre(projeto)\Fornovo-Backend\ForBack\media\output_tables"
    json_manual = r"C:\Users\vinic\Desktop\lalala.json"
    json_pnr = r"C:\Users\vinic\Downloads\PNR.json"
    
    resultado = gerar_memorial_completo(json_manual, json_pnr, path_tables)
    print(f"Memorial gerado com sucesso em: {resultado}")