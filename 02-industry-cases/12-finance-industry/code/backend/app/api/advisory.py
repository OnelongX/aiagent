"""投资陪伴 · 不荐股 · 仅投教 + 反诈拦截"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import AdvisoryRequest, AdvisoryResponse
from app.services.pii_redact_fin import redact
from app.services.compliance_block import (
    is_fraud_signal, FRAUD_RESPONSE,
    soften_advisory, detect_strong_advisory, detect_specific_stock,
    ai_disclaimer, has_commercial_content,
)
from app.services.llm import chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/advisory", tags=["advisory"])


STOCK_RECOMMEND_MARKERS = [
    "推荐", "买什么股", "哪只股能买", "推荐基金", "推荐买入",
    "我应该买", "我现在买什么", "下周看什么",
    "代码", "持仓建议",
]


def classify_intent(question: str) -> str:
    is_fr, _ = is_fraud_signal(question)
    if is_fr:
        return "反诈拦截"
    if any(m in question for m in STOCK_RECOMMEND_MARKERS) or detect_specific_stock(question):
        return "拒答荐股"
    if "适当性" in question or "风险等级" in question or "C 类" in question:
        return "适当性提示"
    if "为什么跌" in question or "为什么涨" in question or "什么原因" in question:
        return "复盘解释"
    return "投教"


SYSTEM_PROMPT = """你是持牌机构的投资者教育 AI · 不是投顾。

**硬规则(违反即作废)**:
1. **绝对不能荐股 / 荐基金 / 推荐具体产品** —— 监管硬红线
2. 不预测未来涨跌 / 不给点位 / 不给目标价
3. 不出现具体股票代码 / 基金代号 · 例子用"R3 偏债混合"这种类别名
4. 不写"保证收益""稳赚""无风险"
5. 涉及"高息""稳赚""内幕"等关键词 → 反诈话术
6. 投教内容只解释概念 / 风险 / 大类资产关系
7. 末尾固定:**本回复为投资者教育 · 不构成投资建议 · 投资有风险**

风格:克制 · 中性 · 引导找持牌投顾。每答不超 350 字。"""


@router.post("/qa", response_model=AdvisoryResponse)
async def qa(req: AdvisoryRequest) -> AdvisoryResponse:
    intent = classify_intent(req.question)

    # 1. 反诈拦截 → 不进 LLM
    if intent == "反诈拦截":
        return AdvisoryResponse(
            intent="反诈拦截",
            answer=FRAUD_RESPONSE,
            refer_to_advisor=True,
            disclaimer="反诈拦截 · 不经 LLM",
        )

    # 2. 拒答荐股 · 改写为投教
    if intent == "拒答荐股":
        return AdvisoryResponse(
            intent="拒答荐股",
            answer=(
                "我们不提供具体的股票 / 基金推荐 —— 这是监管硬性规定。\n\n"
                "建议方向:\n"
                "1. 先做风险测评(C1-C5)→ 明确自己的承受能力\n"
                "2. 资产配置层面思考(债 / 股 / 现金 / 另类)· 而不是单只标的\n"
                "3. 找持牌投资顾问 · 签订投顾协议后再获取个性化建议\n\n"
                "📌 任何号称'保本 / 稳赚 / 推荐买入'的渠道,大概率违规或诈骗。"
            ),
            refer_to_advisor=True,
            disclaimer=ai_disclaimer("AI 不荐股 · 监管硬红线"),
        )

    # 3. 适当性 / 复盘 / 投教 → 走 LLM(严格软化)
    redacted, _ = redact(req.question)
    try:
        answer = chat(
            SYSTEM_PROMPT,
            f"客户级别:{req.customer_level or '未提供'}\n问题:{redacted}",
            max_tokens=900,
        )
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    answer = soften_advisory(answer)

    # 后置审计
    stocks = detect_specific_stock(answer)
    strong = detect_strong_advisory(answer)
    if stocks:
        answer = "[检测到具体股票代码已剔除]\n" + answer
        for s in stocks:
            answer = answer.replace(s, "[STOCK_CODE]")
    if strong:
        answer = "[检测到强建议语言已软化]\n" + answer
    if has_commercial_content(answer):
        answer = "[检测到推广内容已过滤]\n" + answer

    return AdvisoryResponse(
        intent=intent,
        answer=answer,
        refer_to_advisor=True,
        disclaimer=ai_disclaimer("投教内容 · 不构成投资建议"),
    )
