"""LLM service — OpenAI 协议兼容客户端封装。

跟 #6 / #7 一致:
- 走 LLM_API_BASE(推荐 livetoken)
- 不耦合具体厂商,改 endpoint 即可切模型
"""

import json
from openai import OpenAI
from app.config import settings


_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base,
        )
    return _client


def chat(
    system: str,
    user: str,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4000,
    json_mode: bool = False,
) -> str:
    """同步 chat 调用 · 返回文本。"""
    client = get_client()
    kwargs = {
        "model": model or settings.llm_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


def chat_json(system: str, user: str, **kwargs) -> dict:
    """同步 chat 调用 · 期望返回 JSON · 自动 parse。"""
    raw = chat(system, user, json_mode=True, **kwargs)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # 兜底:可能 LLM 没严格输出 JSON
        return {"error": "invalid_json", "raw": raw}
