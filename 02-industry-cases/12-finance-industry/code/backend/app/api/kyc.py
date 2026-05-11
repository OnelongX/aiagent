"""KYC 智能审核 · AI 给风险点 · 不替代人脸 · 最终人工"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import KYCRequest, KYCResponse, KYCFinding
from app.services.pii_redact_fin import redact
from app.services.compliance_block import (
    soften_advisory, detect_strong_advisory, ai_disclaimer
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/kyc", tags=["kyc"])


SYSTEM_PROMPT = """你是商业银行 / 证券公司 / 基金公司的 KYC 审核 AI 辅助。

**硬规则**:
1. **不替代真人尽调** —— 你的输出只是给合规专员的辅助清单
2. 不下"通过 / 拒绝"结论 · 用"建议增强尽调""建议人工复核"等软语言
3. 严格按 6 个 category 分析:identity / income / fund_source / purpose / pep / sanctions
4. 高净值客户 / 政要 / 跨境资金 → 强制增强尽调(EDD)
5. 不歧视 · 不能基于地域 / 性别 / 民族
6. 输出严格 JSON

输出格式:
{
  "overall_risk": "medium",
  "findings": [
    {
      "category": "fund_source",
      "issue": "资金来源描述笼统:仅写'家庭积蓄'",
      "severity": "medium",
      "action": "请提交近 6 月银行流水佐证"
    }
  ],
  "suggested_action": "enhanced_dd"
}"""


@router.post("/review", response_model=KYCResponse)
async def review(req: KYCRequest) -> KYCResponse:
    blob = (
        f"客户:{req.customer_name}\n"
        f"身份证:{req.id_card}\n"
        f"职业:{req.occupation}\n"
        f"年收入:{req.income_yearly}\n"
        f"资金来源:{req.source_of_fund}\n"
        f"用途:{req.purpose}\n"
        f"自报政要关联:{req.pep_self_report}"
    )
    redacted, pii = redact(blob)

    try:
        data = chat_json(SYSTEM_PROMPT, redacted, max_tokens=1800)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        data = {
            "overall_risk": "medium",
            "findings": [{
                "category": "identity",
                "issue": "AI 解析失败 · 建议人工尽调",
                "severity": "medium",
                "action": "由合规专员人工完成 KYC",
            }],
            "suggested_action": "enhanced_dd",
        }

    findings = []
    for f in data.get("findings", []):
        text = soften_advisory(f.get("issue", ""))
        action = soften_advisory(f.get("action", ""))
        if detect_strong_advisory(text + action):
            text = "[已软化强建议语言] " + text
        findings.append(KYCFinding(
            category=f.get("category", "identity"),
            issue=text,
            severity=f.get("severity", "medium"),
            action=action,
        ))

    # PEP 自报 → 强制 EDD
    suggested = data.get("suggested_action", "enhanced_dd")
    if req.pep_self_report and suggested == "accept":
        suggested = "enhanced_dd"
        findings.append(KYCFinding(
            category="pep",
            issue="自报政要 / 公职关联",
            severity="high",
            action="按 PEP 制度执行增强尽调 + 高级管理人员审批",
        ))

    return KYCResponse(
        overall_risk=data.get("overall_risk", "medium"),
        findings=findings,
        suggested_action=suggested,
        must_human_review=True,
        pii_summary=pii,
        disclaimer=ai_disclaimer("KYC 仅辅助 · 最终以合规专员签字为准"),
    )
