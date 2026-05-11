"""合同审查 · POST /api/contract/review"""

from fastapi import APIRouter
from app.models.schemas import (
    ContractReviewRequest, ContractReviewResponse, ContractRisk
)
from app.services.llm import chat_json
from app.services.pii_redact import redact
from app.services.lawyer_block import detect_legal_advice, soften_advice

router = APIRouter(prefix="/api/contract", tags=["contract"])


SYSTEM_PROMPT = """你是资深商务合同审查律师助理。审查输入的合同条款,识别风险并给出修订建议。

输出严格 JSON:
{
  "overall_level": "CRITICAL|HIGH|MEDIUM|LOW",
  "summary": "整份合同的关键风险摘要(100 字内)",
  "risks": [
    {
      "clause": "原条款片段",
      "level": "CRITICAL|HIGH|MEDIUM|LOW",
      "issue": "存在的问题(法律视角)",
      "suggestion": "修订建议(条款文字 · 不要给出绝对结论)"
    }
  ]
}

纪律:
- 不要写"必胜"/"建议起诉"等绝对建议性语言
- 修订建议应是替代条款本身,而不是诉讼策略
- 涉及金额、责任限额、管辖法院等关键条款必标记 HIGH+
- 输出中文"""


@router.post("/review", response_model=ContractReviewResponse)
async def review_contract(req: ContractReviewRequest):
    # 1. PII 脱敏(进 LLM 前)
    redacted, _ = redact(req.contract_text)

    # 2. 拼 user prompt
    user = f"""合同类型:{req.contract_type}
法域:{req.jurisdiction}
我方角色:{req.party_role}

合同条款(已脱敏):
{redacted[:8000]}

请审查并按 JSON 格式输出风险清单。"""

    # 3. LLM 调用
    data = chat_json(SYSTEM_PROMPT, user, max_tokens=4000)

    # 4. 解析 + 软化建议性语言
    risks = []
    for r in data.get("risks", []):
        suggestion = r.get("suggestion", "")
        if detect_legal_advice(suggestion):
            suggestion = soften_advice(suggestion)
        risks.append(ContractRisk(
            clause=r.get("clause", "")[:300],
            level=r.get("level", "MEDIUM"),
            issue=r.get("issue", ""),
            suggestion=suggestion,
            ai_drafted=True,
        ))

    return ContractReviewResponse(
        overall_level=data.get("overall_level", "MEDIUM"),
        risks=risks,
        summary=data.get("summary", ""),
    )
