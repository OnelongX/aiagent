"""Chat service — LLM 调用 + RAG 上下文 + 流式输出。

核心编排 3 件事:
1. RAG 检索(始终跑)
2. 关键词触发的扩展检索(可选)
3. 历史压缩(最近 N 轮)

模型层走 OpenAI 协议兼容 endpoint(推荐:livetoken)
"""

import sqlite3
from pathlib import Path
from collections.abc import Generator
from openai import OpenAI

from app.config import settings
from app.services.rag import search_knowledge


DEFAULT_SYSTEM_PROMPT = """你是一名 AI 工作台助手。
回答规则:
- 用中文回答
- 如果有检索到的知识库内容,优先基于知识库回答,并标注引用来源
- 结构化输出:先概述,再分点展开
- 知识范围外的问题诚实说不知道"""

_PROMPT_FILE = Path(__file__).parent.parent.parent / "data" / "system_prompt.txt"
DB_PATH = Path(__file__).parent.parent.parent / "data" / "db_data" / "chat_history.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

MAX_HISTORY_PAIRS = 20


def get_system_prompt() -> str:
    """系统 prompt 工程化:文件优先,代码兜底,可热改。"""
    if _PROMPT_FILE.exists():
        custom = _PROMPT_FILE.read_text(encoding="utf-8").strip()
        if custom:
            return custom
    return DEFAULT_SYSTEM_PROMPT


def set_system_prompt(prompt: str):
    _PROMPT_FILE.parent.mkdir(parents=True, exist_ok=True)
    _PROMPT_FILE.write_text(prompt, encoding="utf-8")


def _init_db():
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                pinned INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                references_json TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages(conversation_id)")


_init_db()


class ChatService:
    def __init__(self):
        # OpenAI 协议兼容客户端
        # base_url 指向 livetoken / 官方 / 其他 endpoint
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base,
        )

    def _build_rag_context(self, query: str) -> tuple[str, list]:
        """RAG 检索 → 拼上下文 + 引用元数据。"""
        hits = search_knowledge(query, top_k=5)
        if not hits:
            return "", []

        context_parts = []
        refs = []
        for i, h in enumerate(hits, 1):
            context_parts.append(f"[{i}] {h['title']}\n{h['content']}")
            refs.append({
                "doc_id": h["doc_id"],
                "title": h["title"],
                "chunk_index": h["chunk_index"],
                "score": h["score"],
            })
        return "\n\n".join(context_parts), refs

    def stream_reply(self, message: str, history: list) -> Generator[dict, None, None]:
        """流式生成回复 — yield 每个 chunk。"""
        # 1. RAG 检索
        rag_context, refs = self._build_rag_context(message)

        # 2. 历史压缩
        compact_history = history[-MAX_HISTORY_PAIRS * 2:]

        # 3. 组装 messages
        sys_prompt = get_system_prompt()
        if rag_context:
            sys_prompt += f"\n\n# 知识库参考内容:\n{rag_context}"

        messages = [{"role": "system", "content": sys_prompt}]
        messages.extend(compact_history)
        messages.append({"role": "user", "content": message})

        # 4. 调 LLM(流式)
        stream = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            stream=True,
            temperature=0.7,
        )

        # 先输出引用元数据
        if refs:
            yield {"type": "references", "data": refs}

        # 逐 token 输出
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield {"type": "delta", "data": delta}
