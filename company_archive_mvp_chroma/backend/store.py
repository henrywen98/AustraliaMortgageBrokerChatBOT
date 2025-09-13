import chromadb
from .config import CHROMA_DIR, HNSW_M, HNSW_EF_CONSTRUCTION

# Persistent client
_client = chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection():
    """Return (and create if needed) the Chroma collection without built-in embedding function.
    We will supply embeddings manually when adding documents to avoid SDK incompatibilities.
    """
    # Some chromadb versions only accept limited metadata keys (e.g. hnsw:space).
    # Avoid passing unknown HNSW params which cause collection creation to fail.
    metadata = {"hnsw:space": "cosine"}
    return _client.get_or_create_collection(name="company_archive", metadata=metadata)


def delete_vectors_for_doc(doc_id: int):
    """Delete all vectors in the collection that belong to a given doc_id (stored in metadata)."""
    col = get_collection()
    # Chroma supports delete where metadata matches; use a filter
    try:
        col.delete(where={"doc_id": doc_id})
    except Exception:
        # Fallback: iterate ids and delete by id list
        res = col.get(where={"doc_id": doc_id}, include=['metadatas', 'ids'])
        ids = res.get('ids', [])
        if ids:
            col.delete(ids=ids)


def get_collection_info():
    col = get_collection()
    try:
        return col.count()
    except Exception:
        return None
