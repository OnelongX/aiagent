"""出院小结 · 强制医师签字栏 + AI 起草标记"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from app.models.schemas import DischargeSummaryRequest, DischargeSummaryResponse
from app.services.pii_redact_med import redact
from app.services.doctor_block import (
    doctor_sign_block, ai_disclaimer, soften_advice, detect_strong_advice
)
from app.services.llm import chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/discharge", tags=["discharge"])


SYSTEM_PROMPT = """你是医院病案室 AI · 协助起草出院小结。

**硬规则**:
1. 不下新诊断 · 严格依据输入 admission_dx / discharge_dx
2. 主治医师签字栏不能省 · 留 [作者填入] 占位
3. 用药用通用名 · 不写商品名
4. 出院医嘱用"建议复查""按时随访"等软性语言
5. 不写"完全治愈""根治"等绝对化表达
6. 输出严格的 5 段结构:
   一、入院情况
   二、入院诊断
   三、住院经过
   四、出院诊断
   五、出院医嘱
   每段不超 200 字"""


@router.post("/summary", response_model=DischargeSummaryResponse)
async def summary(req: DischargeSummaryRequest) -> DischargeSummaryResponse:
    # 1. PII 脱敏
    blob = f"""主诉:{req.chief_complaint}
入院诊断:{req.admission_dx}
出院诊断:{req.discharge_dx}
住院过程:{req.course}
出院带药:{', '.join(req.medications)}
随访建议:{req.follow_up}"""
    redacted, pii = redact(blob)

    # 2. LLM 起草
    user_prompt = (
        f"入院日期:{req.admission_date}\n"
        f"出院日期:{req.discharge_date}\n\n"
        f"{redacted}\n\n"
        f"请按 5 段结构起草出院小结。"
    )
    try:
        body = chat(SYSTEM_PROMPT, user_prompt, max_tokens=2500, temperature=0.2)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    body = soften_advice(body)
    if detect_strong_advice(body):
        logger.warning("出院小结检测到强建议性语言 · 已软化标记")

    # 3. 强制组装:签字栏 + 正文 + 免责声明
    full = doctor_sign_block("出院小结") + body + ai_disclaimer(
        "出院小结由 AI 辅助起草 · 需主治医师审核签字后归档"
    )

    return DischargeSummaryResponse(
        summary=full,
        drafted_at=datetime.now().isoformat(timespec="seconds"),
        doctor_block=doctor_sign_block("出院小结"),
        disclaimer="AI 起草 · 主治医师签字担责",
        pii_summary=pii,
    )
