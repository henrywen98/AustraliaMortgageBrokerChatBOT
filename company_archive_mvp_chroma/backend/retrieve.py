from typing import List, Dict
from .store import get_collection
from .db import get_chunks_by_ids
from .ingest import embed_texts


def search_chunks(query: str, top_k: int = 6) -> List[Dict]:
    """Search and return chunk dicts (ordered) for the query.

    This computes the query embedding using the same codepath as ingestion
    (embed_texts) and calls Chroma with query_embeddings to avoid mismatched
    embedding dimensions or relying on Chroma's built-in embedding call.
    """
    collection = get_collection()

    # compute embedding for query using the same model as ingest
    q_embs = embed_texts([query]) if query else []
    if q_embs:
        res = collection.query(query_embeddings=[q_embs[0]], n_results=top_k)
    else:
        # fallback - should rarely be used
        res = collection.query(query_texts=[query], n_results=top_k)

    metas = res.get("metadatas", [[]])[0] if res else []
    chunk_ids = [m.get("chunk_id") for m in metas if m and "chunk_id" in m]
    chunks = get_chunks_by_ids(chunk_ids)
    # keep ordering consistent with returned chunk_ids
    id_pos = {cid: i for i, cid in enumerate(chunk_ids)}
    chunks.sort(key=lambda c: id_pos.get(c["id"], 1e9))
    return chunks
