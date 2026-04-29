import pandas as pd
import os
import re
from collections import defaultdict

colunas_mecanicas = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),

        ("Ar condicionado", "", "Quantidade"),
        ("Ar condicionado", "", "Potência [BTU]"),
        ("Ar condicionado", "Dutos", "Refrig [m]"),
        ("Ar condicionado", "Dutos", "Dreno [m]"),
        ("Ar condicionado", "", "Cabo elétrico [KgF]"),
        ("Ar condicionado", "", "Gás refrig [m]"),

        ("Ventilador", "", "Quantidade"),
        ("Ventilador", "", "Tipo"),

        ("Exaustor", "", "Quantidade"),
        ("Exaustor", "", "Tipo"),
    ]
)


def mecanica():
    df = pd.DataFrame(columns=colunas_mecanicas)

    linhas = []
    for _ in range(10):
        linhas.append({col: None for col in colunas_mecanicas})

    df = pd.DataFrame(linhas, columns=colunas_mecanicas)

    return df.sort_index(axis = 1)