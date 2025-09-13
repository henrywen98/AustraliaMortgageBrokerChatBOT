import sqlite3
import time
from typing import List, Optional, Dict
from .config import DB_PATH


def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            title TEXT,
            path TEXT UNIQUE,
            ext TEXT,
            pages INTEGER DEFAULT 0,
            size_bytes INTEGER DEFAULT 0,
            sha256 TEXT UNIQUE,
            uploader TEXT,
            chunking_version INTEGER,
            embedding_model TEXT,
            status TEXT DEFAULT 'ok',
            created_at INTEGER,
            updated_at INTEGER
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY,
            doc_id INTEGER,
            page_from INTEGER,
            page_to INTEGER,
            text TEXT,
            created_at INTEGER,
            FOREIGN KEY(doc_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS operations_log (
            id INTEGER PRIMARY KEY,
            op_type TEXT,
            actor TEXT,
            details TEXT,
            created_at INTEGER
        )
        """
    )

    conn.commit()
    # Run lightweight migrations: add missing columns if the DB was created by an older schema
    try:
        cur.execute("PRAGMA table_info(chunks)")
        cols = [r[1] for r in cur.fetchall()]
        if 'created_at' not in cols:
            cur.execute("ALTER TABLE chunks ADD COLUMN created_at INTEGER")
    except Exception:
        pass

    try:
        cur.execute("PRAGMA table_info(documents)")
        cols = [r[1] for r in cur.fetchall()]
        if 'created_at' not in cols:
            cur.execute("ALTER TABLE documents ADD COLUMN created_at INTEGER")
        if 'updated_at' not in cols:
            cur.execute("ALTER TABLE documents ADD COLUMN updated_at INTEGER")
    except Exception:
        pass

    conn.commit()
    conn.close()


def _now():
    return int(time.time())


def log_operation(op_type: str, actor: str = "system", details: str = "") -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO operations_log (op_type, actor, details, created_at) VALUES (?, ?, ?, ?)",
        (op_type, actor, details, _now()),
    )
    conn.commit()
    oid = cur.lastrowid
    conn.close()
    return oid


def get_recent_operations(limit: int = 100):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM operations_log ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def insert_document(title: str, path: str, file_type: str, pages: int, uploader: str = "local") -> int:
    now = _now()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO documents (title, path, ext, pages, uploader, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (title, path, file_type, pages, uploader, now, now),
    )
    conn.commit()
    doc_id = cur.lastrowid
    conn.close()
    return doc_id


def upsert_document_by_sha256(title: str, path: str, ext: str, pages: int, size_bytes: int, sha256: str, uploader: str, chunking_version: int, embedding_model: str) -> int:
    now = _now()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM documents WHERE sha256 = ?", (sha256,))
    row = cur.fetchone()
    if row:
        doc_id = row[0]
        cur.execute(
            "UPDATE documents SET title=?, path=?, ext=?, pages=?, size_bytes=?, uploader=?, chunking_version=?, embedding_model=?, updated_at=? WHERE id=?",
            (title, path, ext, pages, size_bytes, uploader, chunking_version, embedding_model, now, doc_id),
        )
    else:
        cur.execute(
            "INSERT INTO documents (title, path, ext, pages, size_bytes, sha256, uploader, chunking_version, embedding_model, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (title, path, ext, pages, size_bytes, sha256, uploader, chunking_version, embedding_model, now, now),
        )
        doc_id = cur.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def mark_document_deleted(doc_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE documents SET status='deleted', updated_at=? WHERE id=?", (_now(), doc_id))
    conn.commit()
    conn.close()


def update_document_status(doc_id: int, status: str, note: Optional[str] = None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE documents SET status=?, updated_at=? WHERE id=?", (status, _now(), doc_id))
    conn.commit()
    conn.close()


def insert_chunk(doc_id: int, page_from: int, page_to: int, text: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO chunks (doc_id, page_from, page_to, text, created_at) VALUES (?, ?, ?, ?, ?)",
        (doc_id, page_from, page_to, text, _now()),
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def get_chunks_by_ids(chunk_ids: List[int]) -> List[Dict]:
    if not chunk_ids:
        return []
    conn = get_conn()
    cur = conn.cursor()
    q = f"SELECT c.*, d.title FROM chunks c LEFT JOIN documents d ON c.doc_id=d.id WHERE c.id IN ({','.join(['?']*len(chunk_ids))})"
    cur.execute(q, tuple(chunk_ids))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_documents(limit: Optional[int] = 100) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_chunks_by_doc(doc_id: int) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM chunks WHERE doc_id=? ORDER BY page_from", (doc_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_document_by_sha256(sha256: str) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE sha256=?", (sha256,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_document_by_sha256(sha256: str) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE sha256=?", (sha256,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_chunks_for_doc(doc_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM chunks WHERE doc_id=?", (doc_id,))
    conn.commit()
    conn.close()
