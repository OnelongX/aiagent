"""AML 反洗钱筛查 · 规则评分 + 可疑交易上报建议"""

import logging
from fastapi import APIRouter

from app.models.schemas import AMLRequest, AMLResponse
from app.services.market_db import aml_suspicious_score, aml_level
from app.services.compliance_block import ai_disclaimer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/aml", tags=["aml"])


@router.post("/screen", response_model=AMLResponse)
async def screen(req: AMLRequest) -> AMLResponse:
    score, rules = aml_suspicious_score(req.transaction.model_dump())
    level = aml_level(score)

    if level == "high":
        action = (
            "→ 强制上报可疑交易(STR)\n"
            "→ 触发账户限额 / 冻结审查\n"
            "→ 报反洗钱中心(央行)· 不告知客户"
        )
        must_report = True
    elif level == "medium":
        action = (
            "→ 反洗钱专员人工复核\n"
            "→ 同步调取客户近 3 月流水\n"
            "→ 联系客户经理了解资金背景"
        )
        must_report = False
    elif level == "low":
        action = "→ 留痕 · 进入定期监测列表"
        must_report = False
    else:
        action = "→ 正常处理"
        must_report = False

    return AMLResponse(
        score=score,
        level=level,
        rules_hit=rules,
        must_report=must_report,
        suggested_action=action,
        disclaimer=ai_disclaimer("AML 评分仅辅助 · 上报决定以反洗钱专员为准"),
    )
