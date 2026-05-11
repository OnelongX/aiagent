"""Pydantic schemas — 前后端字段契约的唯一来源。"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: list[dict] = []


class DocumentReference(BaseModel):
    doc_id: str
    title: str
    chunk_index: int
    score: float


class LogEntry(BaseModel):
    """关键纪律:字段名前后端统一"""
    timestamp: str   # 不是 time!避免字段漂移
    method: str
    path: str
    status: int
    duration_ms: float


class IngestRequest(BaseModel):
    """文档 ingest — doc_id 可选,首次为 None,重建时传入"""
    doc_id: Optional[str] = None
    title: str
    content: str
    category: Optional[str] = None
