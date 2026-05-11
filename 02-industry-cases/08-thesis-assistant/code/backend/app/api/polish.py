"""学术润色 · POST /api/polish · diff 输出"""

import json
from fastapi import APIRouter
from app.models.schemas import PolishRequest, PolishResponse, PolishDiff
from app.services.llm import chat_json

router = APIRouter(prefix="/api", tags=["polish"])


SYSTEM_PROMPT_ZH = """你是中文学术编辑。润色用户提供的段落,要求:
- 保持原意,不增不减观点
- 改正口语化表达(比如"特别多"→"显著")
- 修复术语不一致(同一术语全文用同一个译法)
- 标点符号规范(中文标点)
- 句式过长拆开
- 不要改专业术语
- 输出每处修改的 diff,作者可以审阅每处

严格 JSON 输出:
{
  "diffs": [
    {"original": "原文片段", "polished": "改后版本", "reason": "改的理由"}
  ],
  "summary": "整段润色摘要(50 字内)"
}

如果某段不需要改,不要硬改 —— 让 diffs 为空。"""


SYSTEM_PROMPT_EN = """You are an English academic editor. Polish the given paragraph:
- Preserve original meaning
- Fix awkward phrasing
- Use formal academic register
- Keep technical terms unchanged
- Output a diff per change

Strict JSON output:
{
  "diffs": [{"original": "...", "polished": "...", "reason": "..."}],
  "summary": "..."
}"""


@router.post("/polish", response_model=PolishResponse)
async def polish(req: PolishRequest):
    system = SYSTEM_PROMPT_ZH if req.style == "academic_zh" else SYSTEM_PROMPT_EN
    data = chat_json(system, req.text, max_tokens=3000)

    diffs = []
    for d in data.get("diffs", []):
        diffs.append(PolishDiff(
            original=d.get("original", ""),
            polished=d.get("polished", ""),
            reason=d.get("reason", ""),
        ))

    return PolishResponse(
        diffs=diffs,
        summary=data.get("summary", ""),
    )
