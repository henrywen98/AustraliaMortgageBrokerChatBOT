import os
import re
import hashlib
from typing import List, Tuple
from tqdm import tqdm
from openai import OpenAI
from .config import (
    CHUNK_CHARS,
    CHUNK_OVERLAP,
    SHORT_CHUNK_CHARS,
    SHORT_CHUNK_OVERLAP,
    LONG_DOC_PAGE_THRESHOLD,
    STORAGE_DIR,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE,
    CHUNKING_VERSION,
)
from .db import init_db, insert_document, insert_chunk, upsert_document_by_sha256, log_operation
from .store import get_collection
from utils.pdf_utils import extract_pdf_text_with_pages

# OpenAI client for embeddings
client = OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(texts: List[str]):
    """Return a list of embedding vectors for the given texts."""
    if not texts:
        return []
    # Batch requests to the OpenAI embeddings API
    out = []
    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE or 32):
        batch = texts[i : i + EMBEDDING_BATCH_SIZE]
        resp = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        out.extend([d.embedding for d in resp.data])
    return out


def chunk_text(text: str, page_from: int, page_to: int, chunk_chars: int, chunk_overlap: int) -> List[Tuple[int, int, str]]:
    """Split text into overlapping chunks. Return list of (page_from, page_to, chunk_text)."""
    t = re.sub(r"[ \t]+", " ", text or "").strip()
    if not t:
        return []
    chunks = []
    n = len(t)
    i = 0
    while i < n:
        end = min(n, i + chunk_chars)
        chunks.append((page_from, page_to, t[i:end].strip()))
        if end == n:
            break
        i = max(0, end - chunk_overlap)
    return chunks


def _sha256_of_file(path: str, chunk_size: int = 8192) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def ingest_file(path: str, uploader: str = "local") -> int:
    """Ingest a single file: copy to storage, extract pages, chunk, write DB and vectors to Chroma.

    Returns the document id.
    """
    init_db()
    ext = os.path.splitext(path)[1].lower()
    title = os.path.basename(path)

    # compute sha to avoid duplicate ingestion
    sha = _sha256_of_file(path)

    # Save a copy to storage dir (idempotent)
    os.makedirs(STORAGE_DIR, exist_ok=True)
    storage_path = os.path.join(STORAGE_DIR, title)
    if not os.path.exists(storage_path):
        with open(path, "rb") as src, open(storage_path, "wb") as dst:
            dst.write(src.read())

    # Extract text by page
    pages = extract_pdf_text_with_pages(path)
    total_pages = len(pages)

    # Choose chunking size
    if total_pages >= LONG_DOC_PAGE_THRESHOLD:
        chunk_chars = CHUNK_CHARS
        chunk_overlap = CHUNK_OVERLAP
    else:
        chunk_chars = SHORT_CHUNK_CHARS
        chunk_overlap = SHORT_CHUNK_OVERLAP

    # Upsert document record
    size_bytes = os.path.getsize(path)
    doc_id = upsert_document_by_sha256(title, storage_path, ext, total_pages, size_bytes, sha, uploader, CHUNKING_VERSION, EMBEDDING_MODEL)

    # Delete previous chunks for this doc
    from .db import delete_chunks_for_doc

    delete_chunks_for_doc(doc_id)

    # Build chunks and embeddings
    all_texts = []
    chunk_meta = []  # (page_from, page_to, inserted_chunk_id placeholder)
    for (pnum, ptext) in pages:
        chs = chunk_text(ptext, pnum, pnum, chunk_chars, chunk_overlap)
        for (pf, pt, txt) in chs:
            cid = insert_chunk(doc_id, pf, pt, txt)
            all_texts.append(txt)
            chunk_meta.append({"chunk_id": cid, "doc_id": doc_id})

    # Compute embeddings and push to Chroma
    if all_texts:
        embs = embed_texts(all_texts)
        col = get_collection()
        ids = [str(m["chunk_id"]) for m in chunk_meta]
        metadatas = [{"doc_id": m["doc_id"], "chunk_id": m["chunk_id"]} for m in chunk_meta]
        col.add(ids=ids, metadatas=metadatas, documents=all_texts, embeddings=embs)

    log_operation("ingest", actor=uploader, details=f"ingested {title} -> doc_id={doc_id}")
    return doc_id

