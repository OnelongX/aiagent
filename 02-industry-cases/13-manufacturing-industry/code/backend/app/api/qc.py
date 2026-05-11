"""质检视觉缺陷 · AI 提示 · QC 二审"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import QCInspectionRequest, QCInspectionResponse, QCDefectFinding
from app.services.pii_redact_mfg import redact
from app.services.process_guard import (
    soften_advice, detect_strong_advice, ai_disclaimer
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/qc", tags=["qc"])


SYSTEM_PROMPT = """你是 QC AI 辅助 · 给质检员提供初判建议。

**硬规则**:
1. **不下最终判定** —— 你的输出是初判 · 必须 QC 工程师终判
2. 缺陷描述分:defect_type / region / description / severity / suggested_action / confidence
3. suggested_action 限制为 4 类:scrap(报废)/ rework(返工)/ release(放行)/ hold_for_qc(暂存)
4. 涉及客户敏感缺陷 / 安全件 → confidence 强制"低" + hold_for_qc
5. 不写"必须""100%""绝对" · AI 检测 confidence "高" 也只是高置信度
6. cite_sop 引用 SOP 文档号(若已知)
7. 输出严格 JSON

输出格式:
{
  "findings": [
    {
      "defect_type": "气泡",
      "region": "涂层表面 / 中央 25mm 区域",
      "description": "可见 3 个 0.3mm 气泡 · 间距 2-5mm",
      "severity": "medium",
      "suggested_action": "rework",
      "confidence": "中"
    }
  ],
  "overall_decision": "hold_for_qc",
  "cite_sop": ["SOP-CT-001"]
}"""


@router.post("/inspect", response_model=QCInspectionResponse)
async def inspect(req: QCInspectionRequest) -> QCInspectionResponse:
    redacted_obs, pii = redact(f"{req.defect_obs}\n{req.image_caption}")

    user_prompt = (
        f"产线:{req.line_code}\n产品:{req.product_type}\n"
        f"观察:{redacted_obs}"
    )
    try:
        data = chat_json(SYSTEM_PROMPT, user_prompt, max_tokens=2000)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        data = {
            "findings": [{
                "defect_type":      "未知",
                "region":           "未知",
                "description":      "AI 解析失败",
                "severity":         "medium",
                "suggested_action": "hold_for_qc",
                "confidence":       "低",
            }],
            "overall_decision": "hold_for_qc",
            "cite_sop": [],
        }

    findings = []
    for f in data.get("findings", []):
        desc = soften_advice(f.get("description", ""))
        if detect_strong_advice(desc):
            f["confidence"] = "低"  # 检测到强建议 · 降置信度
        findings.append(QCDefectFinding(
            defect_type=f.get("defect_type", "未知"),
            region=f.get("region", ""),
            description=desc,
            severity=f.get("severity", "medium"),
            suggested_action=f.get("suggested_action", "hold_for_qc"),
            confidence=f.get("confidence", "低"),
        ))

    return QCInspectionResponse(
        findings=findings,
        overall_decision=data.get("overall_decision", "hold_for_qc"),
        must_qc_engineer=True,
        cite_sop=data.get("cite_sop", []),
        disclaimer=ai_disclaimer(
            "质检 AI 仅提示 · 最终判定以 QC 检验报告盖章为准"
        ),
        pii_summary=pii,
    )
