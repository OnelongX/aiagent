"""Chat API — 流式 SSE 接口。"""

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest
from app.services.chat import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])
_service = ChatService()


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """流式聊天 · 返回 SSE。"""
    def event_stream():
        for chunk in _service.stream_reply(req.message, req.history):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
