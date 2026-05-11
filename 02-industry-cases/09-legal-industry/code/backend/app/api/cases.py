"""类案检索 · POST /api/cases/search"""

from fastapi import APIRouter
from app.models.schemas import (
    CaseSearchRequest, CaseSearchResponse
)
from app.services.legal_db import search_cases
from app.services.pii_redact import redact

router = APIRouter(prefix="/api/cases", tags=["cases"])


def authority_weight(level: str) -> float:
    return {
        "最高院": 1.0,
        "高院":   0.8,
        "中院":   0.6,
        "基层":   0.4,
    }.get(level, 0.5)


@router.post("/search", response_model=CaseSearchResponse)
async def search(req: CaseSearchRequest):
    # 1. PII 脱敏
    redacted_facts, _ = redact(req.case_facts)

    # 2. 调真实判例库(本 demo 是 mock)
    raw_cases = await search_cases(
        keywords=[req.claim_type],
        claim_type=req.claim_type,
        jurisdiction=req.jurisdiction,
        limit=req.top_k,
    )

    # 3. 加权排序(审级权威 + 近期性 + 跨地区匹配)
    from datetime import date
    cur_year = date.today().year
    for c in raw_cases:
        try:
            case_year = int(c.judgment_date[:4])
        except Exception:
            case_year = cur_year - 5

        recency = max(0, 1 - (cur_year - case_year) / 10)  # 10 年内
        auth = authority_weight(c.court_level)

        c.similarity = round(
            0.3 * c.factual_similarity
            + 0.3 * c.legal_basis_overlap
            + 0.2 * auth
            + 0.1 * recency
            + 0.1 * (1.0 if req.jurisdiction in c.court else 0.5),
            3,
        )

    raw_cases.sort(key=lambda x: -x.similarity)

    # 4. 检测跨地区
    cross_juris = any(
        req.jurisdiction not in c.court for c in raw_cases
    )

    return CaseSearchResponse(
        cases=raw_cases[: req.top_k],
        cross_jurisdiction_warning=cross_juris,
    )
