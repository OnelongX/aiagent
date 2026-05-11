"""大纲生成 · POST /api/outline"""

import json
from fastapi import APIRouter
from app.models.schemas import OutlineRequest, OutlineResponse, OutlineChapter
from app.services.llm import chat_json

router = APIRouter(prefix="/api", tags=["outline"])


SYSTEM_PROMPT = """你是论文写作辅导老师。生成大纲时:

1. 严格按学科常规结构(实验型 / 综述型 / 工程型 / 理论型)
2. 子章节标题要具体,不要"分析 X"这种空泛标题
3. 每章注明建议字数
4. 输出 N 套不同思路,让用户对比

绝不:
- 假装这是用户的研究成果
- 给出具体研究数据或结论(用户自己做实验)
- 写"综上所述"这种 LLM 八股

输出严格 JSON:
{
  "versions": [
    [
      {"chapter": "摘要", "words": 300, "subsections": []},
      {"chapter": "1. 绪论", "words": 1500, "subsections": ["1.1 研究背景", "1.2 ..."]}
    ],
    [...第 2 套...]
  ]
}"""


@router.post("/outline", response_model=OutlineResponse)
async def generate_outline(req: OutlineRequest):
    user = f"""论文题目:{req.topic}
学科:{req.discipline}
论文类型:{req.paper_type}
目标字数:{req.target_words}
关键论点:{', '.join(req.key_points) if req.key_points else '(未提供)'}

请生成 {req.n_versions} 套不同思路的大纲结构,严格 JSON。"""

    data = chat_json(SYSTEM_PROMPT, user, max_tokens=4000)

    versions = []
    for v in data.get("versions", []):
        chapters = []
        for c in v:
            chapters.append(OutlineChapter(
                chapter=c.get("chapter", ""),
                words=c.get("words", 0),
                subsections=c.get("subsections", []),
            ))
        versions.append(chapters)

    return OutlineResponse(versions=versions)
