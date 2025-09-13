import os
import hashlib
from datetime import datetime
from typing import Dict, List
from .config import LIBRARY_DIR, CHUNKING_VERSION, EMBEDDING_MODEL
from .db import get_documents, upsert_document_by_sha256, mark_document_deleted, update_document_status, log_operation, init_db
from .store import delete_vectors_for_doc
from .ingest import ingest_file


LOCKFILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sync.lock")


def _acquire_lock() -> bool:
    """获取同步锁，防止并发执行"""
    if os.path.exists(LOCKFILE):
        return False
    with open(LOCKFILE, "w") as f:
        f.write(str(os.getpid()))
    return True


def _release_lock():
    """释放同步锁"""
    try:
        os.remove(LOCKFILE)
    except Exception:
        pass


def compute_sha256(path: str, chunk_size: int = 8192) -> str:
    """计算文件的SHA256哈希值"""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def scan_library() -> List[Dict]:
    """扫描库目录中的所有文件"""
    res = []
    for root, _, files in os.walk(LIBRARY_DIR):
        for fn in files:
            full = os.path.join(root, fn)
            try:
                st = os.stat(full)
                res.append({
                    "path": full,
                    "title": fn,
                    "size": st.st_size,
                    "mtime": int(st.st_mtime),
                })
            except Exception:
                continue
    return res


def sync_library_once(progress_callback=None):
    """执行一次同步：添加/修改/删除以使Chroma和DB反映LIBRARY_DIR的状态"""
    if not _acquire_lock():
        return {"status": "locked"}
    
    # 确保数据库已初始化
    try:
        init_db()
    except Exception:
        pass
    
    try:
        disk_files = {d["path"]: d for d in scan_library()}
        docs = get_documents(limit=10000)
        db_by_path = {d["path"]: d for d in docs}

        # 检测删除：数据库中存在但文件已丢失
        for path, doc in list(db_by_path.items()):
            if path not in disk_files:
                mark_document_deleted(doc["id"])
                try:
                    delete_vectors_for_doc(doc["id"])
                except Exception:
                    pass
                log_operation("delete_document", actor="sync", details=f"doc_id={doc['id']};path={path}")

        # 检测新文件或更改的文件
        for path, info in disk_files.items():
            existing = db_by_path.get(path)
            need_hash = True
            
            if existing:
                # 检查文件是否已更改
                existing_updated = existing.get("updated_at")
                existing_mtime = 0
                if isinstance(existing_updated, int):
                    existing_mtime = existing_updated
                else:
                    try:
                        existing_mtime = int(datetime.fromisoformat(str(existing_updated)).timestamp())
                    except Exception:
                        try:
                            existing_mtime = int(float(existing_updated))
                        except Exception:
                            existing_mtime = 0

                if existing.get("size_bytes") == info["size"] and existing_mtime >= info["mtime"]:
                    need_hash = False
            
            if need_hash:
                sha = compute_sha256(path)
            else:
                sha = existing.get("sha256")

            # 更新或插入文档元数据
            doc_id = upsert_document_by_sha256(
                title=info["title"],
                path=path,
                ext=os.path.splitext(info["title"])[1].lower().lstrip("."),
                pages=0,
                size_bytes=info["size"],
                sha256=sha,
                uploader="library",
                chunking_version=CHUNKING_VERSION,
                embedding_model=EMBEDDING_MODEL,
            )

            # 删除旧向量并重新摄取以确保一致性
            try:
                delete_vectors_for_doc(doc_id)
            except Exception:
                pass
            
            try:
                ingest_file(path, uploader="library")
                log_operation("ingest_via_sync", actor="sync", details=f"doc_id={doc_id};path={path}")
                if progress_callback:
                    progress_callback({"path": path, "status": "ok"})
            except Exception as e:
                update_document_status(doc_id, "failed")
                log_operation("ingest_failed", actor="sync", details=f"doc_id={doc_id};path={path};error={e}")
                if progress_callback:
                    progress_callback({"path": path, "status": "failed", "error": str(e)})

        return {"status": "ok"}
    finally:
        _release_lock()
