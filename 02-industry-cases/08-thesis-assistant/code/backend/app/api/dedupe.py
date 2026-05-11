"""相似度检测 · POST /api/dedupe

工程纪律:
- 不是真的"查重",只是本地相似度提示
- 输出"建议加引用",不输出"如何避开查重"
- 真实查重必须接知网 / Turnitin / iThenticate
"""

from fastapi import APIRouter
from app.models.schemas import DedupeRequest, DedupeResponse, SimilarityHit
from app.services.similarity import detect_overlap

router = APIRouter(prefix="/api", tags=["dedupe"])


# 禁词 · 任何输出都不允许含这些词(防包装抄袭)
FORBIDDEN_WORDS = [
    "改写后无法识别",
    "避免查重",
    "伪装原创",
    "绕过检测",
    "降低重复率",
]


def _sanitize(text: str) -> str:
    """检查输出是否含禁词 · 含则替换为合规建议"""
    for w in FORBIDDEN_WORDS:
        if w in text:
            return "建议改写或加引用 · 标明原始来源"
    return text


@router.post("/dedupe", response_model=DedupeResponse)
async def dedupe(req: DedupeRequest):
    issues_raw = detect_overlap(
        user_text=req.text,
        compare_against=req.compare_against,
        threshold=req.threshold,
    )

    issues = []
    for i in issues_raw:
        issues.append(SimilarityHit(
            user_chunk=i["user_chunk"],
            similar_chunk=i["similar_chunk"],
            similarity=i["similarity"],
            suggestion=_sanitize(i["suggestion"]),
        ))

    return DedupeResponse(issues=issues)
