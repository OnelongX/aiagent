"""章节起草 · POST /api/section · 留占位"""

import re
from fastapi import APIRouter
from app.models.schemas import SectionRequest, SectionResponse
from app.services.llm import chat

router = APIRouter(prefix="/api", tags=["section"])


SYSTEM_PROMPT = """你是论文写作辅导老师。为指定章节起草框架文本。

关键纪律:
- 提供论证框架,但具体数据 / 实验结果用 [作者填入: ...] 占位
- 学术术语保留英文缩写
- 段落之间逻辑连接清晰
- 不要"综上所述"这种 LLM 八股
- 不要假装这是用户做的实验
- 草稿开头自动加 [本节由 AI 协助起草,核心论证由作者完成] 标签

例如(草稿示例):
[本节由 AI 协助起草,核心论证由作者完成]

本节系统介绍 X 方法的基本原理。
... 框架内容 ...
本研究采用 [作者填入: 实验设置 · 仪器型号 · 样本数量] 进行验证。
表 2.1 显示了 [作者填入: 实验数据] ..."""


@router.post("/section", response_model=SectionResponse)
async def draft_section(req: SectionRequest):
    user = f"""章节:{req.chapter}
论文类型:{req.paper_type}
关键论点:{', '.join(req.key_points)}
目标字数:{req.target_words}

请起草此章节框架,保留 [作者填入: ...] 占位符。"""

    draft = chat(SYSTEM_PROMPT, user, max_tokens=4000)

    # 提取占位符
    placeholders = re.findall(r"\[作者填入[^\]]*\]", draft)

    return SectionResponse(
        draft=draft,
        placeholders=placeholders,
    )
