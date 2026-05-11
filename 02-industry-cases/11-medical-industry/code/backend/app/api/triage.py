"""智能分诊 · ESI 5 级 · 红色直推 120"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import TriageRequest, TriageResponse
from app.services.pii_redact_med import redact
from app.services.doctor_block import (
    is_emergency, EMERGENCY_RESPONSE, soften_advice, ai_disclaimer
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/triage", tags=["triage"])


LEVEL_NAMES = {
    1: "红色 · 立即抢救",
    2: "橙色 · 10 分钟内处理",
    3: "黄色 · 30 分钟内处理",
    4: "绿色 · 60 分钟内处理",
    5: "蓝色 · 非急诊",
}


SYSTEM_PROMPT = """你是急诊分诊 AI 辅助。

**ESI 5 级标准**:
- Level 1 红色:即刻威胁生命(心跳骤停 / 大出血休克 / 意识丧失)
- Level 2 橙色:高危(胸痛伴大汗 / 剧烈头痛 / 严重呼吸困难)
- Level 3 黄色:需多项资源(腹痛 + 化验 + 影像)
- Level 4 绿色:单一资源(轻度外伤 / 单项化验)
- Level 5 蓝色:无资源(配药 / 复诊)

**硬规则**:
1. **疑似急救 → 1 级红色 · 不解释**
2. 输出 JSON · 包含 esi_level / suggested_department / suggested_workup / red_flags
3. 不下诊断结论 · 只给分流建议
4. red_flags 列出 3-5 个需要立即注意的危险信号
5. 用通用名指明检查 · 不指定品牌

输出格式:
{
  "esi_level": 3,
  "suggested_department": "急诊内科",
  "suggested_workup": ["血常规", "心电图"],
  "red_flags": ["持续胸痛", "冷汗", "晕厥"]
}"""


@router.post("/", response_model=TriageResponse)
async def triage(req: TriageRequest) -> TriageResponse:
    # 1. 急救熔断(最高优先级)
    is_em, hits = is_emergency(req.chief_complaint + " " + req.history)
    if is_em:
        return TriageResponse(
            esi_level=1,
            level_name=LEVEL_NAMES[1],
            is_emergency=True,
            emergency_action=EMERGENCY_RESPONSE,
            suggested_department="急诊抢救室",
            suggested_workup=["立即就地抢救 · 不再走分诊流程"],
            red_flags=hits,
            pii_summary={"emergency_triggered": True, "hits": hits},
            disclaimer="本响应不经 LLM · 关键词熔断结果",
        )

    # 2. PII 脱敏 + LLM 评级
    redacted, pii = redact(f"{req.chief_complaint}\n{req.history}\n{req.duration}")
    vital_str = ""
    if req.vital_signs:
        vital_str = "生命体征:" + " | ".join(f"{k}={v}" for k, v in req.vital_signs.items())

    user_prompt = (
        f"年龄:{req.age} 岁 · 性别:{req.sex}\n"
        f"主诉:{redacted}\n"
        f"{vital_str}\n"
        "请按 ESI 5 级标准给出分流建议。"
    )
    try:
        data = chat_json(SYSTEM_PROMPT, user_prompt, max_tokens=1200)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        # fallback:保守一档(黄色)
        data = {
            "esi_level": 3,
            "suggested_department": "全科门诊",
            "suggested_workup": ["建议人工分诊"],
            "red_flags": ["AI 解析失败 · 请护士人工复核"],
        }

    level = int(data.get("esi_level", 3))
    if level not in (1, 2, 3, 4, 5):
        level = 3

    return TriageResponse(
        esi_level=level,
        level_name=LEVEL_NAMES[level],
        is_emergency=(level <= 2),
        suggested_department=soften_advice(data.get("suggested_department", "全科门诊")),
        suggested_workup=data.get("suggested_workup", []),
        red_flags=data.get("red_flags", []),
        pii_summary=pii,
        disclaimer=ai_disclaimer("分诊 AI 不替代分诊护士专业判断"),
    )
