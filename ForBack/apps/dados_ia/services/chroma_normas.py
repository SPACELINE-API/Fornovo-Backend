from pathlib import Path
import shutil
import re
from copy import deepcopy

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from . import ollama_installer

BASE_DIR = Path(__file__).resolve().parents[3]
CHROMA_DIR = BASE_DIR / "media" / "chroma_normas_db"
MODELO_EMBEDDING = "nomic-embed-text"


def get_embeddings():
    return OllamaEmbeddings(model=MODELO_EMBEDDING)


def get_db():
    try:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

        db = Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=get_embeddings()
        )

        _ = db._collection.count()
        return db

    except Exception:
        shutil.rmtree(CHROMA_DIR, ignore_errors=True)
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)

        return Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=get_embeddings()
        )


def normalizar_codigo(codigo: str) -> str:
    if not codigo:
        return "SEM_CODIGO"
    codigo = codigo.upper()
    codigo = re.sub(r"[^A-Z0-9]", "", codigo)
    return codigo

def limpar_texto(texto: str) -> str:
    texto = re.sub(r"[^\x00-\x7FÀ-ÿ]", " ", texto)
    texto = re.sub(r"[ \t]+", " ", texto)
    linhas = texto.splitlines()
    linhas_limpas = []

    for linha in linhas:
        l = linha.strip()

        if not l:
            continue

        if re.fullmatch(r"[\W_]+", l):
            continue

        if len(l) <= 2:
            continue

        linhas_limpas.append(l)

    texto = "\n".join(linhas_limpas)

    texto = re.sub(r"\n{2,}", "\n", texto)

    return texto.strip()


def inserir_norma(pdf_path: str, metadados: dict) -> dict:
    print('[DEBUG] Verificações Ollama')
    ollama_installer.ensure_ollama_ready(['nomic-embed-text'])

    print(f"[DEBUG] Iniciando inserção do PDF: {pdf_path}")

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    print(f"[DEBUG] Total de páginas carregadas: {len(pages)}")

    texto = "\n".join(p.page_content for p in pages)
    texto = limpar_texto(texto)

    print(f"[DEBUG] Tamanho do texto extraído: {len(texto)} caracteres")

    if not texto.strip():
        print("[ERRO] Texto vazio após extração")
        return {"ok": False, "erro": "PDF sem conteúdo legível."}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300
    )

    chunks = splitter.split_text(texto)

    print(f"[DEBUG] Total de chunks gerados: {len(chunks)}")

    if not chunks:
        print("[ERRO] Nenhum chunk foi gerado")
        return {"ok": False, "erro": "Nenhum chunk gerado."}

    db = get_db()

    LOTE = 200
    total_lotes = -(-len(chunks) // LOTE)

    nome_arquivo = Path(pdf_path).name

    codigo_raw = metadados.get("codigo", "") if metadados else ""
    codigo_norm = normalizar_codigo(codigo_raw)

    metadados_base = {
        "fonte": nome_arquivo,
        "nome": metadados.get("nome", "") if metadados else "",
        "codigo": codigo_raw,
        "codigo_normalizado": codigo_norm,
        "serie": metadados.get("serie", "") if metadados else "",
        "ano": metadados.get("ano", "") if metadados else "",
        "descricao": metadados.get("descricao", "") if metadados else ""
    }

    print(f"[DEBUG] Metadados base: {metadados_base}")

    print(f"[INFO] Arquivo: {nome_arquivo}")
    print(f"[INFO] Inserindo norma no chroma em {total_lotes} lotes")

    for i in range(0, len(chunks), LOTE):
        lote = chunks[i:i + LOTE]
        idx_lote = i // LOTE + 1

        lista_metadados = []

        for j, chunk in enumerate(lote):
            meta = deepcopy(metadados_base)

            meta["chunk_index_global"] = i + j
            meta["chunk_index_lote"] = j
            meta["lote"] = idx_lote
            meta["chunk_id"] = f"{codigo_norm}_{i + j}"

            lista_metadados.append(meta)

        print(f"[DEBUG] Processando lote {idx_lote}/{total_lotes} com {len(lote)} chunks")

        try:
            db.add_texts(lote, metadatas=lista_metadados)
            print(f"[DEBUG] Lote {idx_lote} inserido com sucesso")
        except Exception as e:
            print(f"[ERRO] Falha ao inserir lote {idx_lote}: {e}")
            return {"ok": False, "erro": str(e)}

    try:
        total_db = db._collection.count()
        print(f"[DEBUG] Total de registros no Chroma após inserção: {total_db}")
    except Exception as e:
        print(f"[ERRO] Não foi possível contar registros: {e}")

    print("[INFO] Inserção finalizada com sucesso")

    return {
        "ok": True,
        "chunks_inseridos": len(chunks),
        "lotes": total_lotes
    }


def apagar_norma(codigo: int) -> bool:
    db = get_db()
    codigo_norm = normalizar_codigo(str(codigo))
    db.delete(where={"codigo_normalizado": codigo_norm})
    return True