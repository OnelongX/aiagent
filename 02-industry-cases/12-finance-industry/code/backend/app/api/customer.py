"""客户画像 + 流失预警 · 给 RM 用 · 不直接对客户营销"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import CustomerInsightRequest, CustomerInsight
from app.services.pii_redact_fin import redact
from app.services.compliance_block import (
    soften_advisory, has_commercial_content, ai_disclaimer
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/customer", tags=["customer"])


SYSTEM_PROMPT = """你是私行 / 零售部 RM 助手 · 给客户经理画像和留存建议。

**硬规则**:
1. **输出对象是客户经理 / RM** · 不是客户 · 不是营销话术
2. 不写"立即推荐 X 产品""配资 Y 万"等具体动作
3. retention_suggestions 必须是"行动方向"层面 · 不是 push 话术
4. 不歧视年龄 / 性别 / 地域
5. 不出现具体股票代码 / 基金代号
6. 输出严格 JSON

输出格式:
{
  "persona": "稳健型中高净值 · 退休临近 · 偏现金 + 银行理财",
  "churn_risk": "medium",
  "churn_reasons": ["近 30 天大额赎回", "登录频次降低 80%"],
  "retention_suggestions": [
    "建议 RM 1 周内电访 · 了解资金动向(自用 / 转移机构)",
    "可对接资产配置健康检查 · 不是销售单一产品"
  ]
}"""


@router.post("/insight", response_model=CustomerInsight)
async def insight(req: CustomerInsightRequest) -> CustomerInsight:
    redacted_id, pii = redact(f"客户号:{req.customer_id}")

    blob = (
        f"年龄:{req.age}\n资产 AUM:{req.aum_rmb} 元\n"
        f"上次登录:{req.last_active_days} 天前\n"
        f"持有产品类:{', '.join(req.products_held) or '无'}\n"
        f"30 天赎回:{req.redemption_30d}\n"
        f"30 天交互:{req.interaction_count_30d}\n"
        f"NPS:{req.nps_score if req.nps_score is not None else '未填'}\n"
    )

    try:
        data = chat_json(SYSTEM_PROMPT, blob, max_tokens=1500)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        data = {
            "persona": "AI 解析失败 · 请 RM 自行画像",
            "churn_risk": "medium",
            "churn_reasons": ["解析失败"],
            "retention_suggestions": ["建议 RM 人工接触"],
        }

    persona  = soften_advisory(data.get("persona", ""))
    reasons  = [soften_advisory(r) for r in data.get("churn_reasons", [])]
    suggests = [soften_advisory(s) for s in data.get("retention_suggestions", [])]

    # 后置审计 · 营销话术拦截
    suggests = [
        ("[检测到营销话术已过滤] " + s) if has_commercial_content(s) else s
        for s in suggests
    ]

    return CustomerInsight(
        persona=persona,
        churn_risk=data.get("churn_risk", "medium"),
        churn_reasons=reasons,
        retention_suggestions=suggests,
        must_relationship_manager=True,
        pii_summary=pii,
        disclaimer=ai_disclaimer("客户画像仅供 RM 参考 · 严禁直接转客户作为营销内容"),
    )
