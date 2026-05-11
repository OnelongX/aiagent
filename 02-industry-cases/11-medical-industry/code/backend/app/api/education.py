"""患者科普 + 复诊咨询 · 应急熔断 + 首诊转线下"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import PatientQARequest, PatientQAResponse
from app.services.pii_redact_med import redact
from app.services.doctor_block import (
    is_emergency, EMERGENCY_RESPONSE, soften_advice,
    has_commercial_content, ai_disclaimer
)
from app.services.llm import chat
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/education", tags=["patient_education"])


# 自伤 / 心理危机关键词
PSYCH_CRISIS = ["自杀", "想结束生命", "活不下去", "想自残", "想跳楼", "割腕"]

# 首诊倾向关键词(应转线下)
FIRST_VISIT_MARKERS = [
    "新出现", "最近", "突然", "第一次", "没看过医生",
    "诊断", "确诊", "是什么病", "什么病",
]


def classify_intent(question: str) -> str:
    if any(p in question for p in PSYCH_CRISIS):
        return "心理危机"
    is_em, _ = is_emergency(question)
    if is_em:
        return "急救"
    if any(m in question for m in FIRST_VISIT_MARKERS):
        return "首诊倾向"
    if "复查" in question or "复诊" in question or "上次" in question:
        return "复诊咨询"
    return "科普"


SYSTEM_PROMPT = """你是患者健康科普 AI · 不诊断 · 不开方。

**硬规则**:
1. 不下诊断结论 · 不说"你患了 X 病"
2. 不开具具体处方 · 用通用名指代 · 不写品牌
3. 用通俗语言科普 · 不用过多医学术语
4. 涉及具体病情 → 引导线下就诊
5. 涉及急救 → 立即拨打 120
6. 不推荐医院 / 私立机构 / 付费课程
7. 末尾固定附:**本回复为健康科普 · 不构成诊疗建议**

风格:简明 · 安抚 · 引导就医。每答不超 300 字。"""


@router.post("/qa", response_model=PatientQAResponse)
async def qa(req: PatientQARequest) -> PatientQAResponse:
    intent = classify_intent(req.question)

    # 1. 心理危机 / 急救 → 不进 LLM
    if intent == "心理危机":
        return PatientQAResponse(
            intent="心理危机",
            answer=(
                "您现在的感受很重要 · 请立即拨打:\n\n"
                f"· 全国心理援助热线 **{settings.mental_hotline}**\n"
                "· 北京心理危机研究与干预中心 **010-82951332**\n"
                f"· 紧急情况拨打 **{settings.emergency_phone}**\n\n"
                "如果身边有家人或朋友,请告诉他们您的感受。\n"
                "您不是一个人在面对。"
            ),
            refer_to_clinic=True,
            emergency_contacts=[
                {"name": "全国心理援助热线", "number": settings.mental_hotline},
                {"name": "急救", "number": settings.emergency_phone},
            ],
            disclaimer="心理危机响应 · 不经 LLM",
        )

    if intent == "急救":
        return PatientQAResponse(
            intent="急救",
            answer=EMERGENCY_RESPONSE,
            refer_to_clinic=True,
            emergency_contacts=[
                {"name": "急救", "number": settings.emergency_phone},
                {"name": "中毒", "number": settings.poison_hotline},
            ],
            disclaimer="急救响应 · 不经 LLM",
        )

    # 2. 首诊倾向 → LLM 给科普 + 强制建议线下
    if intent == "首诊倾向" and not req.is_followup:
        redacted, _ = redact(req.question)
        sci = chat(
            SYSTEM_PROMPT,
            f"科普向回答(不诊断):{redacted}\n年龄:{req.patient_age}",
            max_tokens=600,
        )
        sci = soften_advice(sci)
        answer = (
            sci
            + "\n\n📍 **建议尽快线下就诊** · 互联网医院仅限复诊"
              " · 首诊请到对应科室面诊。"
        )
        return PatientQAResponse(
            intent="首诊倾向",
            answer=answer,
            refer_to_clinic=True,
            disclaimer=ai_disclaimer("AI 不诊断 · 首诊请线下"),
        )

    # 3. 复诊 / 普通科普
    redacted, _ = redact(req.question)
    try:
        answer = chat(
            SYSTEM_PROMPT,
            f"患者问题:{redacted}\n年龄:{req.patient_age}\n是否复诊:{req.is_followup}",
            max_tokens=800,
        )
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    answer = soften_advice(answer)
    if has_commercial_content(answer):
        logger.warning("科普回复检测到推广性内容 · 已标记")
        answer = "[检测到推广性内容已过滤]\n" + answer

    return PatientQAResponse(
        intent=intent,
        answer=answer,
        refer_to_clinic=(intent == "复诊咨询" and "进展" in req.question),
        disclaimer=ai_disclaimer("健康科普 · 不构成诊疗"),
    )
