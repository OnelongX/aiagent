"""LLM client · OpenAI 协议兼容"""

import json
import logging
from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_api_base,
        )
    return _client


def chat(system: str, user: str, max_tokens: int = 1500, temperature: float = 0.2) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""


def chat_json(system: str, user: str, max_tokens: int = 2000) -> dict:
    txt = chat(
        system + "\n\n严格输出 JSON 对象,不要任何解释文字、不要 markdown 代码块。",
        user,
        max_tokens=max_tokens,
        temperature=0.1,
    )
    txt = txt.strip()
    if txt.startswith("```"):
        txt = txt.split("```")[1]
        if txt.startswith("json"):
            txt = txt[4:]
    try:
        return json.loads(txt.strip())
    except Exception as e:
        logger.error(f"JSON parse failed: {e} · raw: {txt[:200]}")
        return {"_error": str(e), "_raw": txt[:500]}
