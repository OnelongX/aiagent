"""临床决策支持(CDSS)· 给提示 · 不下医嘱"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import CDSSRequest, CDSSResponse, CDSSSuggestion
from app.services.pii_redact_med import redact
from app.services.doctor_block import (
    soften_advice, detect_strong_advice, ai_disclaimer
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/cdss", tags=["cdss"])


SYSTEM_PROMPT = """你是临床决策支持 AI · 仅给医师参考提示。

**硬规则**:
1. 不下诊断结论 · 用"考虑评估""建议鉴别"等语言
2. 不开具处方 · 用药 / 检查仅作为"可考虑的"建议
3. 必须列 red_flag(危险信号)· 帮医师不漏诊
4. 建议至少有 1 个 differential(鉴别诊断)
5. references 引用指南名 · 不杜撰文献
6. 输出严格 JSON

输出格式:
{
  "suggestions": [
    {
      "category": "diagnostic_workup",
      "suggestion": "建议完善 ECG / 心肌酶 / 胸片",
      "rationale": "鉴别 ACS / 主动脉夹层 / 肺栓塞",
      "references": ["AHA 2020 胸痛评估指南"]
    },
    {
      "category": "differential",
      "suggestion": "考虑鉴别:急性冠脉综合征 / 反流性食管炎 / 肌肉骨骼痛",
      "rationale": "中年男性胸痛 + 大汗"
    },
    {
      "category": "red_flag",
      "suggestion": "持续胸痛 > 20min + 大汗 + 放射至左肩 → 立即心电图 + 启动 STEMI 通道",
      "rationale": "时间窗对 ACS 预后关键"
    }
  ]
}"""


@router.post("/", response_model=CDSSResponse)
async def cdss(req: CDSSRequest) -> CDSSResponse:
    redacted, pii = redact(f"{req.chief_complaint}\n{req.history}\n{req.current_dx}")
    labs_str = ""
    if req.labs:
        labs_str = "化验:" + " | ".join(f"{k}={v}" for k, v in req.labs.items())

    user_prompt = (
        f"患者:{req.age} 岁 {req.sex}\n"
        f"主诉 / 病史:{redacted}\n"
        f"{labs_str}\n"
        f"当前诊断(若有):{req.current_dx}\n\n"
        "请给出诊疗提示。"
    )
    try:
        data = chat_json(SYSTEM_PROMPT, user_prompt, max_tokens=2500)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    suggestions = []
    for s in data.get("suggestions", []):
        text = soften_advice(s.get("suggestion", ""))
        if detect_strong_advice(text):
            text = "[已软化强建议性语言] " + text
        suggestions.append(CDSSSuggestion(
            category=s.get("category", "diagnostic_workup"),
            suggestion=text,
            rationale=s.get("rationale", ""),
            references=s.get("references", []),
        ))

    return CDSSResponse(
        suggestions=suggestions,
        disclaimer=ai_disclaimer(
            "CDSS 仅提示 · 诊断 / 处方 / 处置以执业医师为准 · 严禁直接转患者"
        ),
        pii_summary=pii,
    )
