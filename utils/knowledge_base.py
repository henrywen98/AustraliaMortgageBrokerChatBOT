import os
import re
from typing import List, Dict

import chromadb
from openai import OpenAI

from config import CHROMA_DIR, EMBEDDING_MODEL, OPENAI_API_KEY_VAR
from .pdf_utils import extract_pdf_text_with_pages


class KnowledgeBase:
    """Simple PDF ingestion and search using ChromaDB and OpenAI embeddings."""

    def __init__(
        self,
        persist_dir: str = CHROMA_DIR,
        embedding_model: str = EMBEDDING_MODEL,
        openai_api_key_var: str = OPENAI_API_KEY_VAR,
    ) -> None:
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.embedding_model = embedding_model
        api_key = os.getenv(openai_api_key_var)
        self.client = OpenAI(api_key=api_key)
        self.chroma = chromadb.PersistentClient(path=self.persist_dir)
        self.col = self.chroma.get_or_create_collection("mortgage_docs")

    # ----------------------- Embeddings -----------------------
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        resp = self.client.embeddings.create(model=self.embedding_model, input=texts)
        return [d.embedding for d in resp.data]

    # ----------------------- Chunking -----------------------
    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        t = re.sub(r"[ \t]+", " ", text or "").strip()
        if not t:
            return []
        out = []
        i = 0
        n = len(t)
        while i < n:
            j = min(n, i + chunk_size)
            out.append(t[i:j].strip())
            if j == n:
                break
            i = max(0, j - overlap)
        return out

    # ----------------------- Ingestion -----------------------
    def ingest_pdf(self, path: str, source: str | None = None) -> int:
        """Ingest a PDF file and return number of chunks added."""
        pages = extract_pdf_text_with_pages(path)
        chunks = []
        metas = []
        for pnum, ptext in pages:
            for chunk in self._chunk_text(ptext):
                chunks.append(chunk)
                metas.append({"source": source or os.path.basename(path), "page": pnum})
        if not chunks:
            return 0
        embeddings = self._embed_texts(chunks)
        ids = [f"{os.path.basename(path)}-{i}" for i in range(len(chunks))]
        self.col.add(ids=ids, documents=chunks, metadatas=metas, embeddings=embeddings)
        return len(chunks)

    # ----------------------- Retrieval -----------------------
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        if not query:
            return []
        q_emb = self._embed_texts([query])[0]
        res = self.col.query(query_embeddings=[q_emb], n_results=top_k)
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        out = []
        for doc, meta in zip(docs, metas):
            src = meta.get("source", "unknown")
            page = meta.get("page")
            source = f"{src} p.{page}" if page else src
            out.append({"content": doc, "source": source})
        return out
