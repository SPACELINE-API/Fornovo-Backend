import pandas as pd

colunas_pressurizadas = pd.MultiIndex.from_tuples(
    [
        ("", "", "Circuito"),

        ("Gás Pressurizado", "Dutos", "DN [mm]"),
        ("Gás Pressurizado", "Dutos", "h [cm]"),
        ("Gás Pressurizado", "Dutos", "C [m]"),

        ("Gás Pressurizado", "Reguladores", "DN [mm]"),
        ("Gás Pressurizado", "Reguladores", "Qnt"),
        ("Gás Pressurizado", "Reguladores", "Tipo"),
        ("Gás Pressurizado", "Reguladores", "Redução Pressão de"),
        ("Gás Pressurizado", "Reguladores", "Redução Pressão para"),

        ("Gás Pressurizado", "Válvulas", "DN [mm]"),
        ("Gás Pressurizado", "Válvulas", "Qnt"),
        ("Gás Pressurizado", "Válvulas", "Tipo"),

        ("Gás Pressurizado", "Registros", "DN [mm]"),
        ("Gás Pressurizado", "Registros", "Qnt"),
        ("Gás Pressurizado", "Registros", "Tipo"),

        ("Gás Pressurizado", "Reservatório", "Qnt"),
        ("Gás Pressurizado", "Reservatório", "Tipo"),

        ("Conexões", "", "Tipo"),
        ("Conexões", "Joelhos", "90"),
        ("Conexões", "Joelhos", "45"),

        ("Conexões", "Curva", "90"),

        ("Conexões", "Luva", "Simples"),
        ("Conexões", "Luva", "Redução"),

        ("Conexões", "Tês", "Simples"),
        ("Conexões", "Tês", "Redução"),

        ("Conexões", "Junções", "45"),
        ("Conexões", "Junções", "Redução"),
    ]
)

def pressurizada():
    df = pd.DataFrame(columns=colunas_pressurizadas)

    linhas = []
    for _ in range(10):
        linhas.append({col: None for col in colunas_pressurizadas})

    df = pd.DataFrame(linhas, columns=colunas_pressurizadas)

    return df