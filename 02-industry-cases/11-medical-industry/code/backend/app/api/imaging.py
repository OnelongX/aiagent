"""影像辅助 · AI 给"建议复核" · 不出诊断"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import ImagingReviewRequest, ImagingReviewResponse, ImagingFinding
from app.services.pii_redact_med import redact
from app.services.doctor_block import (
    soften_advice, detect_strong_advice, ai_disclaimer
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/imaging", tags=["imaging"])


SYSTEM_PROMPT = """你是放射科 AI 辅助系统。

**硬规则(违反即作废)**:
1. **不出诊断结论** —— 只能写"建议进一步评估""提示需复核"等软性语言
2. 不写"考虑为 X 病""确诊为 Y"等定性表达
3. 关注所见必须分区域 + 描述 + 建议复核点
4. 标注置信度(低 / 中 / 高)
5. 涉及恶性肿瘤 / 急症等可疑征象 · 置信度统一标"低" + 强烈建议人工复核
6. 输出严格 JSON · 不要 markdown

输出格式:
{
  "findings": [
    {
      "region": "右肺上叶",
      "description": "见 8mm 结节,边缘较清",
      "suggested_review": "建议结合既往片对比,必要时短期随访",
      "confidence": "中",
      "references": ["Fleischner 2017 肺结节随访指南"]
    }
  ]
}"""


@router.post("/review", response_model=ImagingReviewResponse)
async def review(req: ImagingReviewRequest) -> ImagingReviewResponse:
    # 1. PII 脱敏
    redacted, pii = redact(f"{req.clinical_history}\n{req.findings_text}")

    # 2. LLM 生成"建议复核"语言
    user_prompt = (
        f"检查类型:{req.modality}\n"
        f"检查部位:{req.body_part}\n"
        f"临床信息:{redacted}\n\n"
        f"基于以上,列出建议复核点。"
    )
    try:
        data = chat_json(SYSTEM_PROMPT, user_prompt, max_tokens=2000)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        # fallback:返回最低风险模板
        data = {"findings": [{
            "region": req.body_part,
            "description": "AI 解析失败 · 建议人工阅片",
            "suggested_review": "建议放射科医师完整阅片并出具报告",
            "confidence": "低",
            "references": [],
        }]}

    # 3. 软化语言 + 强建议性检测
    findings = []
    for f in data.get("findings", []):
        desc = soften_advice(f.get("description", ""))
        suggest = soften_advice(f.get("suggested_review", ""))
        if detect_strong_advice(desc + suggest):
            # 检测到"必须""一定"等 · 强行降置信度
            f["confidence"] = "低"
            suggest = "[检测到强建议性语言已软化] " + suggest

        findings.append(ImagingFinding(
            region=f.get("region", req.body_part),
            description=desc,
            suggested_review=suggest,
            confidence=f.get("confidence", "低"),
            references=f.get("references", []),
        ))

    return ImagingReviewResponse(
        modality=req.modality,
        body_part=req.body_part,
        suggested_reviews=findings,
        must_human_review=True,
        disclaimer=ai_disclaimer("影像 AI 仅作为放射科医师辅助 · 100% 必须医师复核"),
        pii_summary=pii,
    )
