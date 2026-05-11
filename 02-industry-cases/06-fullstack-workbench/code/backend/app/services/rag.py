"""RAG service — Chroma 向量检索 + 文档 registry。

核心纪律:
- doc_id 在首次 ingest 时生成 UUID
- rebuild / 改分类时复用原 doc_id
- 避免文档身份与路径耦合
"""

import sqlite3
import uuid
from pathlib import Path
from typing import Optional


# Embedding 模型(BGE-M3 · 中英多语言)
class EmbeddingModel:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            from sentence_transformers import SentenceTransformer
            from app.config import settings
            cls._instance = SentenceTransformer(settings.embedding_model)
        return cls._instance


# Chroma 向量库(单例)
class _VectorStore:
    def __init__(self):
        import chromadb
        path = Path(__file__).parent.parent.parent / "data" / "chroma_db"
        path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(path))
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )


vector_store = _VectorStore()


# 文档 registry(SQLite)
REGISTRY_DB = Path(__file__).parent.parent.parent / "data" / "db_data" / "doc_registry.db"
REGISTRY_DB.parent.mkdir(parents=True, exist_ok=True)


def _init_registry():
    with sqlite3.connect(str(REGISTRY_DB)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS doc_registry (
                doc_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


_init_registry()


def _chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """简单切块。生产环境换 late chunking 或按文档结构切。"""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks


def ingest_document(
    title: str,
    content: str,
    doc_id: Optional[str] = None,
    category: Optional[str] = None,
) -> str:
    """Ingest 文档。

    关键纪律:
    - 首次 ingest:生成 UUID
    - 后续 rebuild / 覆盖:复用 doc_id
    - 文档身份独立于文件路径或 title
    """
    if doc_id is None:
        doc_id = str(uuid.uuid4())

    # 删除旧的 chunks(rebuild 场景)
    try:
        vector_store.collection.delete(where={"doc_id": doc_id})
    except Exception:
        pass

    # 切块 + embed + 入库
    chunks = _chunk_text(content)
    model = EmbeddingModel.get()
    embeddings = model.encode(chunks, normalize_embeddings=True).tolist()

    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    metadatas = [{
        "doc_id": doc_id,
        "title": title,
        "category": category or "default",
        "chunk_index": i,
    } for i in range(len(chunks))]

    vector_store.collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    # 更新 registry
    with sqlite3.connect(str(REGISTRY_DB)) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO doc_registry (doc_id, title, category) VALUES (?, ?, ?)",
            (doc_id, title, category or "default"),
        )

    return doc_id


def search_knowledge(query: str, top_k: int = 5) -> list[dict]:
    """向量检索。"""
    model = EmbeddingModel.get()
    embedding = model.encode([query], normalize_embeddings=True).tolist()[0]

    results = vector_store.collection.query(
        query_embeddings=[embedding],
        n_results=top_k,
    )

    hits = []
    if results and results["ids"] and results["ids"][0]:
        for i, doc_id_str in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            hits.append({
                "doc_id": meta["doc_id"],
                "title": meta["title"],
                "chunk_index": meta["chunk_index"],
                "content": results["documents"][0][i],
                "score": 1 - results["distances"][0][i],
            })
    return hits


def list_documents() -> list[dict]:
    """列出所有 ingested 文档。"""
    with sqlite3.connect(str(REGISTRY_DB)) as conn:
        rows = conn.execute(
            "SELECT doc_id, title, category, created_at FROM doc_registry ORDER BY created_at DESC"
        ).fetchall()
    return [
        {"doc_id": r[0], "title": r[1], "category": r[2], "created_at": r[3]}
        for r in rows
    ]
