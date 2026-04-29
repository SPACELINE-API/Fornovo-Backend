import pandas as pd
import json
import os
import re
import math
from collections import defaultdict

colunas_ambientais = pd.MultiIndex.from_tuples(
    [
        ("", "Ambiente"),
        ("Plaquetas", "Local"),
        ("Plaquetas", "Saída"),
        ("Plaquetas", "Extintor"),
        ("Plaquetas", "Quadro Força"),
        ("Plaquetas", "Hidrante"),
        ("Plaquetas", "Alarme"),
        ("Plaquetas", "Proibido fumar"),
        ("Plaquetas", "Perigo Inflamável"),
        ("Plaquetas", "Risco Explosão"),
        ("Sinalização de via", "Contra mão"),
        ("Sinalização de via", "Curva Direita"),
        ("Sinalização de via", "Curva Esquerda"),
        ("Sinalização de via", "40 Km/h"),
        ("Sinalização de via", "Pare"),
    ]
)

def ambientais():
    df = pd.DataFrame(columns=colunas_ambientais)

    linhas = []
    for _ in range(10):
        linhas.append({col: None for col in colunas_ambientais})

    df = pd.DataFrame(linhas, columns=colunas_ambientais)

    return df
