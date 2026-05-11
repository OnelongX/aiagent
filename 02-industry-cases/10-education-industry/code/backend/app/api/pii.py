"""教育版 PII 脱敏 · POST /api/pii/redact"""

from fastapi import APIRouter
from app.models.schemas import EduPIIRequest, EduPIIResponse
from app.services.pii_redact_edu import redact

router = APIRouter(prefix="/api/pii", tags=["pii"])


@router.post("/redact", response_model=EduPIIResponse)
async def do_redact(req: EduPIIRequest):
    redacted, entities, minor_detected = redact(req.text)
    safe_entities = [
        {"type": e["type"], "placeholder": e["placeholder"]}
        for e in entities
    ]
    return EduPIIResponse(
        redacted_text=redacted,
        redacted_entities=safe_entities,
        minor_data_detected=minor_detected,
    )
