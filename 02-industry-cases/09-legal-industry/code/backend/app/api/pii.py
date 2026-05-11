"""PII 脱敏 · POST /api/pii/redact

独立暴露 · 用户可以先脱敏文本再上传到其他流程。
"""

from fastapi import APIRouter
from app.models.schemas import PIIRedactRequest, PIIRedactResponse
from app.services.pii_redact import redact

router = APIRouter(prefix="/api/pii", tags=["pii"])


@router.post("/redact", response_model=PIIRedactResponse)
async def do_redact(req: PIIRedactRequest):
    redacted, entities = redact(req.text)
    # 不要把 original 暴露出去(API 上),只暴露 type + placeholder
    safe_entities = [
        {"type": e["type"], "placeholder": e["placeholder"]}
        for e in entities
    ]
    return PIIRedactResponse(
        redacted_text=redacted,
        redacted_entities=safe_entities,
    )
