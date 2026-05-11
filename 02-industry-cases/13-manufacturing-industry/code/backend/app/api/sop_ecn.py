"""SOP / ECN 知识问答 · 引用必须带版本号 + 生效日期"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import SOPRequest, SOPResponse
from app.services.mes_mock import search_sop, get_ecn
from app.services.process_guard import (
    soften_advice, ai_disclaimer
)
from app.services.llm import chat

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sop", tags=["sop_ecn"])


def classify_intent(question: str) -> str:
    if any(k in question for k in ["ECN", "变更", "ECO", "升级", "改图"]):
        return "ecn_query"
    if any(k in question for k in ["SOP", "怎么开机", "操作规程", "怎么调"]):
        return "sop_query"
    return "general"


SYSTEM_PROMPT = """你是 SOP / ECN 知识问答 AI 辅助。

**硬规则**:
1. **必须引用具体文档 ID + 版本号 + 生效日期** —— 不带版本号不许答
2. 不替代工艺评审 · 涉及变更必须走 ECN 流程
3. 涉及在制品(WIP)/ 已交付 · 必须说明影响范围
4. 不写"必须""一定" · 用"按 SOP""按 ECN"
5. 答案不超 300 字 · 简明 · 引导查原文

回答末尾固定标:**(版本可能滚动 · 以工艺工程师确认的最新版为准)**"""


@router.post("/qa", response_model=SOPResponse)
async def qa(req: SOPRequest) -> SOPResponse:
    intent = classify_intent(req.question)

    cite_docs = []
    # 1. ECN 直接引用 ID
    if "ECN-" in req.question.upper():
        for token in req.question.split():
            ecn = get_ecn(token.strip(",.;:"))
            if ecn:
                cite_docs.append({"doc_id": token, **ecn})

    # 2. 关键词检索 SOP
    if not cite_docs:
        if "涂层" in req.question or "L-A1" in req.question:
            cite_docs.extend(search_sop("涂层"))
        if "SMT" in req.question or "L-B1" in req.question or "回流" in req.question:
            cite_docs.extend(search_sop("SMT"))

    # 3. LLM 合成回答(引用必须带版本)
    cite_str = "\n".join(
        f"· {c['doc_id']}({c.get('title','')} · 版本 {c.get('version','?')} · "
        f"生效 {c.get('effective_date','?')})"
        for c in cite_docs
    ) or "(未命中本地 SOP / ECN 库 · 请查 PLM 系统)"

    user_prompt = (
        f"操作工提问:{req.question}\n"
        f"相关产线:{req.line_code or '未指定'}\n"
        f"命中文档:\n{cite_str}"
    )
    try:
        answer = chat(SYSTEM_PROMPT, user_prompt, max_tokens=900)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    answer = soften_advice(answer)

    # 检测 ECN 影响范围(若是 ECN 查询)
    if intent == "ecn_query" and cite_docs:
        for c in cite_docs:
            if "impact" in c:
                answer += "\n\n📌 影响范围(摘自 ECN):\n" + "\n".join(
                    f"  · {item}" for item in c["impact"]
                )

    return SOPResponse(
        intent=intent,
        answer=answer,
        cite_docs=cite_docs,
        must_engineer_review=True,
        disclaimer=ai_disclaimer("引用版本可能滚动 · 以工艺工程师确认的最新版为准"),
    )
