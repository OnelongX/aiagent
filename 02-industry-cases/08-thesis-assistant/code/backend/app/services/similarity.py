"""本地相似度检测 · 用 sentence-transformers · 不是真的"查重"。

工程纪律:
- 输出"相似 + 建议加引用",不输出"如何避开查重"
- 真实查重必须接专业服务(知网 / Turnitin / iThenticate)
"""

from typing import Optional


class _EmbModel:
    _instance = None

    @classmethod
    def get(cls):
        if cls._instance is None:
            from sentence_transformers import SentenceTransformer
            from app.config import settings
            cls._instance = SentenceTransformer(settings.embedding_model)
        return cls._instance


def chunk_text(text: str, chunk_size: int = 100, overlap: int = 20) -> list[str]:
    """按字数切块(简化版 · 生产环境按句子切更稳)。"""
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start >= len(text):
            break
    return chunks


def cosine_sim(a, b) -> float:
    import numpy as np
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def detect_overlap(
    user_text: str,
    compare_against: list[str],
    threshold: float = 0.85,
) -> list[dict]:
    """检测 user_text 中哪些段落跟 compare_against 高度相似。"""
    user_chunks = chunk_text(user_text)
    if not user_chunks or not compare_against:
        return []

    model = _EmbModel.get()
    user_embs = model.encode(user_chunks, normalize_embeddings=True)
    ref_embs = model.encode(compare_against, normalize_embeddings=True)

    issues = []
    for i, u_emb in enumerate(user_embs):
        max_sim = 0.0
        max_ref = ""
        for j, r_emb in enumerate(ref_embs):
            s = cosine_sim(u_emb, r_emb)
            if s > max_sim:
                max_sim = s
                max_ref = compare_against[j]
        if max_sim >= threshold:
            issues.append({
                "user_chunk": user_chunks[i],
                "similar_chunk": max_ref[:200],
                "similarity": round(max_sim, 4),
                "suggestion": "建议改写或加引用(标明来源)",
            })

    return issues
