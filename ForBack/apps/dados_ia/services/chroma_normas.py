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


def inserir_norma(pdf_path: str, metadados: dict) -> dict:
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

    nome_arquivo = Path(pdf_path).name

    print(nome_arquivo)
    print('Inserindo norma no chroma')

    metadados_base = {
        "fonte": nome_arquivo,
        "nome": metadados.get("nome", "") if metadados else "",
        "codigo": metadados.get("codigo", "") if metadados else "",
        "serie": metadados.get("serie", "") if metadados else "",
        "ano": metadados.get("ano", "") if metadados else "",
        "descricao": metadados.get("descricao", "") if metadados else ""
    }
    
    # Se o dict de metadados trouxer campos extra (como id_norma), eles são adicionados aqui
    if metadados:
        for k, v in metadados.items():
            if k not in metadados_base:
                metadados_base[k] = v

    for i in range(0, len(chunks), LOTE):
        lote = chunks[i:i + LOTE]
        lista_metadados = [metadados_base for _ in lote]
        db.add_texts(lote, metadatas=lista_metadados)

    return {
        "ok": True,
        "chunks_inseridos": len(chunks),
        "lotes": total_lotes
    }

def apagar_norma(id_norma: int) -> bool:
    db = get_db()
    db.delete(where={"id_norma": id_norma})
    return True

