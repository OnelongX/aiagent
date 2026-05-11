"""法律文书起草 · POST /api/drafting/generate

关键纪律:
- 顶部强制注入律师签字栏
- 留 [作者填入: ...] 占位
- 法律依据必须接真实法条数据库验真
- 末尾强制 AI 协助声明
"""

import re
from fastapi import APIRouter
from app.models.schemas import (
    DraftDocumentRequest, DraftDocumentResponse, LegalArticle
)
from app.services.llm import chat
from app.services.legal_db import search_articles, verify_article
from app.services.lawyer_block import sign_block, ai_disclaimer
from app.services.pii_redact import redact

router = APIRouter(prefix="/api/drafting", tags=["drafting"])


# === 6 种文书的提示词模板 ===
DOC_TEMPLATES = {
    "民事起诉状": """起草一份民事起诉状框架,包含:
- 当事人信息(留占位)
- 诉讼请求(基于 case_info)
- 事实和理由
- 证据清单(留 [作者填入] 占位)
- 法律依据(占位 · 由系统补)
- 此致 / 起诉人 / 日期""",

    "答辩状": """起草答辩状框架,包含:
- 答辩意见
- 事实陈述
- 法律分析
- 反驳证据 [作者填入] 占位""",

    "代理词": """起草代理词框架,庭审用,包含:
- 案件总述
- 事实部分
- 法律部分
- 总结""",

    "法律意见书": """起草法律意见书框架,包含:
- 客户问题
- 法律分析(基础 / 风险 / 处理路径)
- 结论(留占位 · 律师审核后填)
- 风险提示""",

    "仲裁申请书": """起草仲裁申请书框架,包含:
- 仲裁请求
- 事实和理由
- 仲裁条款
- 仲裁地 / 适用规则(占位)""",

    "律师函": """起草律师函框架,包含:
- 收件人
- 事实陈述
- 法律分析
- 函件目的与要求
- 限期""",
}


SYSTEM_BASE = """你是资深法律文书起草助理。

关键纪律:
- 提供文书框架,但具体事实 / 金额 / 证据用 [作者填入: ...] 占位
- 不要写"必胜"/"建议起诉"等绝对建议性语言
- 不要假装这是律师签字的最终文书
- 法律依据可以提及法条名,但**不要凭空编条文内容**(由系统验真后补)
- 严格输出文书正文 · 不要输出 JSON 或 markdown 标记"""


@router.post("/generate", response_model=DraftDocumentResponse)
async def draft(req: DraftDocumentRequest):
    if req.document_type not in DOC_TEMPLATES:
        from fastapi import HTTPException
        raise HTTPException(400, f"unsupported document_type: {req.document_type}")

    # 1. PII 脱敏 case_info
    case_info_str = str(req.case_info)
    redacted_case, _ = redact(case_info_str)

    # 2. 生成正文
    system = SYSTEM_BASE + "\n\n" + DOC_TEMPLATES[req.document_type]
    user = f"""文书类型:{req.document_type}
法域:{req.jurisdiction}

案件信息(已脱敏):
{redacted_case}

请起草框架,保留 [作者填入: ...] 占位符。"""

    body = chat(system, user, max_tokens=3000)

    # 3. 提取占位符
    placeholders = re.findall(r"\[作者填入[^\]]*\]", body)

    # 4. 法律依据 · 接真实数据库验真
    keywords = [req.document_type, *req.case_info.get("案由", "").split()]
    legal_basis = await search_articles(keywords, req.jurisdiction)

    # 5. 强制组合 · 顶部签字栏 + 正文 + 末尾免责
    final_doc = sign_block() + body + ai_disclaimer()

    return DraftDocumentResponse(
        document=final_doc,
        placeholders=placeholders,
        legal_basis=legal_basis,
        lawyer_sign_block=sign_block(),
        ai_assist_disclaimer=ai_disclaimer(),
    )
