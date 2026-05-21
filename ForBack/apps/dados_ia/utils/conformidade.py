import re
import unicodedata
from io import BytesIO

from docx import Document


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.upper().strip()


def _primeiro_inteiro(celulas: list) -> int | None:
    for texto in celulas:
        match = re.search(r"\b(\d+)\b", texto)
        if match:
            return int(match.group(1))
    return None


def _eh_tabela_sumario(table) -> bool:
    if not table.rows:
        return False
    cabecalho = _normalizar(" ".join(c.text for c in table.rows[0].cells))
    return "STATUS" in cabecalho and "QTD" in cabecalho


def extrair_sumario_docx(arquivo) -> dict | None:
    """
    Lê o Sumário Executivo de um relatório .docx gerado por gerar_docx_bytes.
    Retorna contagens ou None se a tabela não for encontrada.
    """
    doc = Document(arquivo)
    conforme = nao_conforme = inconclusivo = total = 0
    encontrou = False

    for table in doc.tables:
        if not _eh_tabela_sumario(table):
            continue

        for row in table.rows[1:]:
            celulas = [c.text.strip() for c in row.cells]
            if not celulas:
                continue

            rotulo = _normalizar(celulas[0])
            qtd = _primeiro_inteiro(celulas[1:])

            if qtd is None:
                continue

            if rotulo == "TOTAL":
                total = qtd
                encontrou = True
            elif "INCONCLUSIVO" in rotulo:
                inconclusivo = qtd
                encontrou = True
            elif "NAO CONFORME" in rotulo:
                nao_conforme = qtd
                encontrou = True
            elif "CONFORME" in rotulo:
                conforme = qtd
                encontrou = True

        if encontrou:
            break

    if not encontrou:
        return None

    if total == 0:
        total = conforme + nao_conforme + inconclusivo

    return {
        "conforme": conforme,
        "nao_conforme": nao_conforme,
        "inconclusivo": inconclusivo,
        "total": total,
    }


def extrair_sumario_arquivo(file_field) -> dict | None:
    with file_field.open("rb") as f:
        conteudo = f.read()
    return extrair_sumario_docx(BytesIO(conteudo))


def classificar_conformidade(valor: int) -> tuple[str, str]:
    if valor >= 85:
        return "Excelente", "#16a34a"
    if valor >= 70:
        return "Atenção", "#ca8a04"
    return "Risco", "#dc2626"


def calcular_percentual(conforme: int, total: int) -> int:
    if total <= 0:
        return 0
    return round(conforme / total * 100)


def agregar_sumarios(sumarios: list[dict]) -> dict:
    conforme = sum(s["conforme"] for s in sumarios)
    nao_conforme = sum(s["nao_conforme"] for s in sumarios)
    inconclusivo = sum(s["inconclusivo"] for s in sumarios)
    total = sum(s["total"] for s in sumarios)
    valor = calcular_percentual(conforme, total)
    status, cor = classificar_conformidade(valor)

    return {
        "valor": valor,
        "status": status,
        "cor": cor,
        "metricas": [
            {"label": "Verificações conformes", "valor": conforme},
            {"label": "Total de verificações", "valor": total},
        ],
        "detalhe": {
            "conforme": conforme,
            "nao_conforme": nao_conforme,
            "inconclusivo": inconclusivo,
            "total_verificacoes": total,
            "relatorios_analisados": len(sumarios),
        },
    }
