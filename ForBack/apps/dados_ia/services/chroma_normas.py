from pathlib import Path
import shutil

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHROMA_DIR = Path.home() / ".chroma_normas_db"
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


def inserir_norma(pdf_path: str) -> dict:
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    texto = "\n".join(p.page_content for p in pages)

    if not texto.strip():
        return {"ok": False, "erro": "PDF sem conteúdo legível."}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300
    )

    chunks = splitter.split_text(texto)

    if not chunks:
        return {"ok": False, "erro": "Nenhum chunk gerado."}

    db = get_db()

    LOTE = 200
    total_lotes = -(-len(chunks) // LOTE)

    for i in range(0, len(chunks), LOTE):
        lote = chunks[i:i + LOTE]
        db.add_texts(lote)

    return {
        "ok": True,
        "chunks_inseridos": len(chunks),
        "lotes": total_lotes
    }


def total_chunks() -> int:
    db = get_db()
    return db._collection.count()
