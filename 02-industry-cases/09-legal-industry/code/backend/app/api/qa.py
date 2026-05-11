"""法律咨询 · POST /api/qa

边界最严的场景:
- 不能直接给"法律建议"
- 应急情况立即拦截 → 推 110/12348
- 个案咨询 → 改写为科普 + 强烈推荐律师
- 普法 → 正常回答 + 强制免责声明
"""

from fastapi import APIRouter
from app.models.schemas import LegalQARequest, LegalQAResponse, LegalArticle
from app.services.llm import chat
from app.services.legal_db import search_articles
from app.services.lawyer_block import (
    qa_disclaimer, is_emergency, EMERGENCY_RESPONSE,
    detect_legal_advice, soften_advice,
)
from app.services.pii_redact import redact

router = APIRouter(prefix="/api/qa", tags=["qa"])


SYSTEM_PROMPT = """你是法律知识科普助手(不是律师)。回答用户法律问题时:

✅ 可以做的:
- 解释相关法律法规含义
- 列出常见处理流程
- 提示需要注意的事项
- 推荐咨询执业律师

❌ 绝对不能做:
- 直接告诉用户"你应该怎么做"
- 评估"你这案子胜算多少"
- 给出"建议起诉"等具体行动建议
- 假装自己是律师

回答应:
- 用中文
- 先科普相关法律
- 再列出一般处理步骤(不是给用户的具体方案)
- 最后强烈建议咨询执业律师"""


# === 意图识别 ===
INDIVIDUAL_CASE_MARKERS = ["我", "我的", "我应该", "我能不能", "我该", "我们公司"]
CRIMINAL_MARKERS = ["刑事", "拘留", "判刑", "看守所", "嫌疑人", "犯罪", "起诉"]


def classify_intent(question: str) -> str:
    if is_emergency(question):
        return "应急情况"
    if any(k in question for k in CRIMINAL_MARKERS):
        return "刑事相关"
    if any(k in question for k in INDIVIDUAL_CASE_MARKERS):
        return "个案咨询"
    return "普法"


@router.post("", response_model=LegalQAResponse)
async def qa(req: LegalQARequest):
    # 1. PII 拦截(用户描述具体案件细节,先脱敏)
    redacted_q, entities = redact(req.question)

    # 2. 应急情况立即拦截 · 不进 LLM
    if is_emergency(req.question):
        return LegalQAResponse(
            intent="应急情况",
            answer=EMERGENCY_RESPONSE,
            emergency_contacts=[
                "110(报警)",
                "12348(法律援助热线)",
                "12338(妇女维权)",
                "400-161-9995(心理危机)",
            ],
        )

    # 3. 意图分类
    intent = classify_intent(req.question)

    # 4. 个案咨询 → 不直接答 · 改科普 + 强推律师
    if intent == "个案咨询":
        answer = await _redirect_individual_case(redacted_q, req.jurisdiction)
        return LegalQAResponse(
            intent="个案咨询",
            answer=answer,
            disclaimer=qa_disclaimer(),
        )

    # 5. 刑事相关 → 直接推律师 · 不分析案情
    if intent == "刑事相关":
        return LegalQAResponse(
            intent="刑事相关",
            answer=(
                "刑事案件涉及人身自由,法律风险极高。\n\n"
                "强烈建议:\n"
                "1. **立即联系刑事辩护律师**(可委托或申请法律援助)\n"
                "2. 法律援助热线:12348\n"
                "3. 涉嫌违法的当事人,**有沉默权和获得辩护权**\n\n"
                "AI 工具无法替代刑事辩护律师的执业判断。"
            ),
            disclaimer=qa_disclaimer(),
        )

    # 6. 普法问题 → 正常 LLM 回答
    user = f"问题:{redacted_q}\n\n用户法域:{req.jurisdiction}"
    raw_answer = chat(SYSTEM_PROMPT, user, max_tokens=2000)

    # 7. 软化建议性语言
    if detect_legal_advice(raw_answer):
        raw_answer = soften_advice(raw_answer)

    # 8. 接相关法条(可选 · 增强答案)
    referenced_laws = []
    try:
        referenced_laws = await search_articles([req.question[:50]], req.jurisdiction)
    except Exception:
        pass

    return LegalQAResponse(
        intent="普法",
        answer=raw_answer + qa_disclaimer(),
        referenced_laws=referenced_laws,
        disclaimer=qa_disclaimer(),
    )


async def _redirect_individual_case(question: str, jurisdiction: str) -> str:
    """个案咨询 → 改写为科普 + 一般步骤 + 推律师"""
    system = """用户在咨询具体的个案。但你不是律师,不能给个案建议。

请这样回答:
1. 简要科普相关法律(2-3 句)
2. 列出**一般处理步骤**(注意:是"一般",不是"你应该")
3. **强烈建议咨询执业律师**
4. 提供法律援助渠道(12348)

不要分析"你能不能赢" / "你应不应该 X"。"""
    return chat(system, question, max_tokens=1500)
