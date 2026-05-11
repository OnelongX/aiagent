"""法规追踪 + 影响分析 · POST /api/regulation/track"""

from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import RegulationTrackingResponse, RegulationUpdate
from app.services.legal_db import fetch_recent_regulations
from app.services.llm import chat

router = APIRouter(prefix="/api/regulation", tags=["regulation"])


class TrackRequest(BaseModel):
    days: int = 7
    business_keywords: list[str] = []   # 客户业务关键词,用于影响匹配


@router.post("/track", response_model=RegulationTrackingResponse)
async def track(req: TrackRequest):
    # 1. 拉最近 N 天的法规更新(mock · 生产环境接 RSS)
    raw_updates = await fetch_recent_regulations(days=req.days)

    # 2. 转 Pydantic
    updates = []
    for u in raw_updates:
        updates.append(RegulationUpdate(
            title=u.get("title", ""),
            source=u.get("source", ""),
            publish_date=u.get("publish_date", ""),
            effective_date=u.get("effective_date"),
            source_url=u.get("source_url", ""),
            affected_industries=u.get("affected_industries", []),
            summary=u.get("summary", ""),
        ))

    # 3. (可选)用 LLM 给每条更新生成「影响分析」(基于客户业务关键词)
    # 注意:LLM 只做关键点提取,具体合规判断仍需律师
    if req.business_keywords:
        for u in updates:
            try:
                u.summary = await _impact_analysis(u, req.business_keywords)
            except Exception:
                pass

    return RegulationTrackingResponse(updates=updates)


async def _impact_analysis(update: RegulationUpdate, business_keywords: list[str]) -> str:
    """让 LLM 把法规变更转成「对客户业务的初步影响分析」。

    严格纪律:
    - 不给绝对结论(「该规对你完全无影响」)
    - 必须强调「初步分析」「需律师确认」
    """
    system = """你是法律合规分析助手。读完法规变更摘要,结合用户业务关键词,
给出**初步影响分析**(2-3 句)。

纪律:
- 用「可能影响 / 建议排查」等保守措辞
- 不要写「无影响」「完全合规」「不需要任何改造」等绝对结论
- 最后一定加「具体合规改造请咨询执业律师」
- 输出中文 · 不要 markdown"""
    user = f"""法规标题:{update.title}
来源:{update.source}
生效:{update.effective_date}
摘要:{update.summary}

用户业务关键词:{', '.join(business_keywords)}

请给出初步影响分析(2-3 句)。"""

    return chat(system, user, max_tokens=400)
