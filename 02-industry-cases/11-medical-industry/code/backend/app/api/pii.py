"""PII 脱敏工具 · 独立端点供测试"""

from fastapi import APIRouter

from app.models.schemas import PIIRedactRequest, PIIRedactResponse
from app.services.pii_redact_med import redact

router = APIRouter(prefix="/api/pii", tags=["pii"])


@router.post("/redact", response_model=PIIRedactResponse)
async def redact_endpoint(req: PIIRedactRequest) -> PIIRedactResponse:
    redacted, summary = redact(req.text)
    return PIIRedactResponse(
        original_length=len(req.text),
        redacted_text=redacted,
        pii_summary=summary,
    )
