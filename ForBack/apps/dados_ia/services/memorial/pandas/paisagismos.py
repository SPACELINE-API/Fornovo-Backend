import pandas as pd

colunas_paisagismo = pd.MultiIndex.from_tuples(
    [
        ("", "", "Ambiente"),
        ("", "", "Local"),
    ]
)

def paisagismo():
    df = pd.DataFrame(columns=colunas_paisagismo)

    linhas = []
    for _ in range(10):
        linhas.append({col: None for col in colunas_paisagismo})

    df = pd.DataFrame(linhas, columns=colunas_paisagismo)

    return df