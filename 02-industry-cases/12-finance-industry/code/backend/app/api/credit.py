"""信贷反欺诈 + 评分 · AI 辅助决策 · 反歧视审计"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import CreditRequest, CreditResponse, CreditFinding
from app.services.pii_redact_fin import redact
from app.services.compliance_block import (
    soften_advisory, ai_disclaimer, detect_discrimination
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/credit", tags=["credit"])


SYSTEM_PROMPT = """你是商业银行互联网贷款风控 AI 辅助。

**硬规则**:
1. **不下最终决定** —— 输出只是辅助 · 最终人工信贷员
2. 严格按 5 个 category:fraud / income / debt / history / policy
3. **严禁基于地域 / 性别 / 民族 / 婚姻状况给建议** —— 这是歧视
4. 评分用 0-1000 区间(类 FICO 体系)
5. 风险等级:AAA / AA / A / B / C / D
6. 建议授信不能超过 (月收入 - 月负债) × 36
7. 输出严格 JSON

输出格式:
{
  "risk_score": 720,
  "risk_band": "A",
  "findings": [
    {
      "category": "debt",
      "description": "月负债收入比 0.6 偏高",
      "severity": "medium",
      "advice": "建议下调授信或要求降负债"
    }
  ],
  "suggested_decision": "approve_with_conditions",
  "suggested_limit": 80000
}"""


@router.post("/score", response_model=CreditResponse)
async def score(req: CreditRequest) -> CreditResponse:
    redacted_name, pii = redact(req.customer_name)

    # 1. 反欺诈黑名单 / 设备硬熔断
    if req.blacklist_hit:
        return CreditResponse(
            risk_score=0,
            risk_band="D",
            findings=[CreditFinding(
                category="fraud",
                description="命中黑名单",
                severity="high",
                advice="拒绝 · 上报反欺诈系统",
            )],
            suggested_decision="decline",
            suggested_limit=0,
            discrimination_check=[],
            must_credit_officer=True,
            pii_summary=pii,
            disclaimer=ai_disclaimer("黑名单熔断 · 不进 LLM"),
        )

    # 2. LLM 评估
    blob = (
        f"年龄:{req.age}\n月收入:{req.income_monthly}\n月负债:{req.debt_monthly}\n"
        f"职业:{req.employment}\n征信摘要:{req.credit_history}\n"
        f"申请金额:{req.loan_amount}\n用途:{req.loan_purpose}\n"
        f"设备风险:{req.device_risk}\n"
    )
    try:
        data = chat_json(SYSTEM_PROMPT, blob, max_tokens=1800)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        data = {
            "risk_score": 500,
            "risk_band": "B",
            "findings": [],
            "suggested_decision": "manual_review",
            "suggested_limit": 0,
        }

    findings = []
    discrim_audit = []
    for f in data.get("findings", []):
        text = soften_advisory(f.get("description", ""))
        adv  = soften_advisory(f.get("advice", ""))
        # 反歧视审计 · 检测 AI 输出是否含歧视性表述
        d_hits = detect_discrimination(text + adv)
        if d_hits:
            discrim_audit.extend(d_hits)
            adv = "[反歧视审计:剔除地域 / 性别 / 民族表述] " + adv
        findings.append(CreditFinding(
            category=f.get("category", "policy"),
            description=text,
            severity=f.get("severity", "low"),
            advice=adv,
        ))

    return CreditResponse(
        risk_score=int(data.get("risk_score", 500)),
        risk_band=data.get("risk_band", "B"),
        findings=findings,
        suggested_decision=data.get("suggested_decision", "manual_review"),
        suggested_limit=int(data.get("suggested_limit", 0)),
        discrimination_check=discrim_audit,
        must_credit_officer=True,
        pii_summary=pii,
        disclaimer=ai_disclaimer("信贷评分仅辅助 · 决定以信贷员 / 风控委员会为准"),
    )
