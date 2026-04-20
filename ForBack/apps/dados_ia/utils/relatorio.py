import re
import io
from dataclasses import dataclass, field
from docx import Document


@dataclass
class Item:
    emoji: str = ""
    codigo: str = ""
    descricao: str = ""
    status: str = ""
    justificativa: str = ""
    recomendacao: str = ""
    layers_confirmados: str = ""
    layers_ausentes: str = ""
    evidencias: list = field(default_factory=list)

@dataclass
class Grupo:
    titulo: str = ""
    resumo: str = ""
    itens: list = field(default_factory=list)

@dataclass
class Sumario:
    conforme: int = 0
    nao_conforme: int = 0
    inconclusivo: int = 0
    perc_conf: str = "0%"
    perc_nconf: str = "0%"
    perc_incon: str = "0%"
    total: int = 0


def parse_relatorio(md: str):
    lines = md.split("\n")
    meta = {}
    grupos = []
    grupo_atual = None
    item_atual = None
    secao = None
    sumario = Sumario()

    for line in lines:
        if line.startswith("**Arquivo analisado:**"):
            m = re.search(r"`(.+?)`", line)
            meta["arquivo"] = m.group(1) if m else line.split(":**")[1].strip()
        if line.startswith("**Data/Hora:**"):
            meta["data_hora"] = line.split(":**")[1].strip()
        if line.startswith("**Normas de referência:**"):
            meta["normas"] = line.split(":**")[1].strip()
        if line.startswith("**Total de verificações:**"):
            meta["total"] = line.split(":**")[1].strip()

        m = re.search(r"✅ Conforme\s+\|\s+(\d+)\s+\|\s+([\d%]+)", line)
        if m:
            sumario.conforme = int(m.group(1))
            sumario.perc_conf = m.group(2)
        m = re.search(r"❌ Não Conforme\s+\|\s+(\d+)\s+\|\s+([\d%]+)", line)
        if m:
            sumario.nao_conforme = int(m.group(1))
            sumario.perc_nconf = m.group(2)
        m = re.search(r"⚠️\s+Inconclusivo\s+\|\s+(\d+)\s+\|\s+([\d%]+)", line)
        if m:
            sumario.inconclusivo = int(m.group(1))
            sumario.perc_incon = m.group(2)

        m = re.match(r"^## (.+?)\s+\*\((.+?)\)\*", line)
        if m:
            grupo_atual = Grupo(titulo=m.group(1), resumo=m.group(2))
            grupos.append(grupo_atual)
            item_atual = None
            secao = None
            continue

        m = re.match(r"^### (✅|❌|⚠️)\s+\[(.+?)\]\s+(.+)", line)
        if m and grupo_atual:
            item_atual = Item(
                emoji=m.group(1),
                codigo=m.group(2),
                descricao=re.sub(r"\*\*", "", m.group(3)),
            )
            grupo_atual.itens.append(item_atual)
            secao = None
            continue

        if not item_atual:
            continue

        if line.startswith("**Status:**"):
            item_atual.status = line.split(":**")[1].strip().replace("`", "")
        elif line.startswith("**Justificativa:**"):
            item_atual.justificativa = line.split(":**", 1)[1].strip()
        elif line.startswith("**Recomendação:**"):
            item_atual.recomendacao = line.split(":**", 1)[1].strip()
        elif line.startswith("**Layers confirmados:**"):
            item_atual.layers_confirmados = line.split(":**", 1)[1].strip().replace("`", "")
        elif line.startswith("**Layers não encontrados:**"):
            item_atual.layers_ausentes = line.split(":**", 1)[1].strip().replace("`", "")
        elif line.startswith("**Evidências"):
            secao = "evidencias"
        elif secao == "evidencias" and line.startswith("- "):
            item_atual.evidencias.append(line[2:].strip())

    sumario.total = sumario.conforme + sumario.nao_conforme + sumario.inconclusivo
    return meta, sumario, grupos


def gerar_docx_bytes(markdown_text: str) -> bytes:
    meta, sumario, grupos = parse_relatorio(markdown_text)

    doc = Document()

    doc.add_heading("RELATÓRIO DE CONFORMIDADE NBR", level=1)
    doc.add_paragraph(f"Arquivo: {meta.get('arquivo', '-')}")
    doc.add_paragraph(f"Data/Hora: {meta.get('data_hora', '-')}")
    doc.add_paragraph(f"Normas: {meta.get('normas', '-')}")

    doc.add_heading("Sumário", level=2)
    doc.add_paragraph(f"Conformes: {sumario.conforme} ({sumario.perc_conf})")
    doc.add_paragraph(f"Não Conformes: {sumario.nao_conforme} ({sumario.perc_nconf})")
    doc.add_paragraph(f"Inconclusivos: {sumario.inconclusivo} ({sumario.perc_incon})")

    for grupo in grupos:
        doc.add_heading(f"{grupo.titulo} — {grupo.resumo}", level=2)
        for item in grupo.itens:
            doc.add_heading(f"[{item.codigo}] {item.descricao}", level=3)
            doc.add_paragraph(f"Status: {item.emoji} {item.status}")
            if item.justificativa:
                doc.add_paragraph(f"Justificativa: {item.justificativa}")
            if item.recomendacao and item.recomendacao.lower() not in ("nenhuma", "nenhum"):
                doc.add_paragraph(f"Recomendação: {item.recomendacao}")
            if item.layers_confirmados:
                doc.add_paragraph(f"Layers confirmados: {item.layers_confirmados}")
            if item.layers_ausentes:
                doc.add_paragraph(f"Layers ausentes: {item.layers_ausentes}")
            if item.evidencias:
                doc.add_paragraph("Evidências:")
                for ev in item.evidencias:
                    doc.add_paragraph(f"• {ev}", style="List Bullet")

    doc.add_paragraph("Gerado automaticamente — Pipeline RAG Local (Ollama + LangChain + ChromaDB)")

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()