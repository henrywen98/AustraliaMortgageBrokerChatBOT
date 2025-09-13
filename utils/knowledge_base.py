"""
Lightweight stub for future RAG integration.

The full implementation has been archived under `archive/rag/` to reduce
runtime dependencies. This stub preserves the interface so callers can
import and instantiate without pulling in heavy packages.
"""

from typing import List, Dict


class _DummyCollection:
    def count(self) -> int:
        return 0


class KnowledgeBase:
    """Stubbed knowledge base with no-op methods.

    - `ingest_pdf` returns 0
    - `search` returns an empty list
    - `col.count()` returns 0
    """

    def __init__(self, persist_dir: str = "data/chroma", embedding_model: str = "text-embedding-3-small", openai_api_key_var: str = "OPENAI_API_KEY") -> None:
        self.persist_dir = persist_dir
        self.embedding_model = embedding_model
        self.col = _DummyCollection()

    def ingest_pdf(self, path: str, source: str | None = None) -> int:
        return 0

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, str]]:
        return []

