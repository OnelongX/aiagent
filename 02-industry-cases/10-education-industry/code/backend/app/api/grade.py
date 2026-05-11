"""作业批改 · 客观题自动 + 主观题二审"""

from fastapi import APIRouter
from app.models.schemas import (
    GradeObjectiveRequest, GradeObjectiveResponse, GradeObjectiveResult,
    GradeEssayRequest, GradeEssayResponse, EssayDimension, EssayImprovement,
)
from app.services.llm import chat_json
from app.services.pii_redact_edu import redact
from app.services.teacher_block import (
    soften_labels, detect_sensitive_topic, AI_ASSIST_NOTICE,
)

router = APIRouter(prefix="/api/grade", tags=["grade"])


# ============ 客观题(规则自动判)============
@router.post("/objective", response_model=GradeObjectiveResponse)
async def grade_objective(req: GradeObjectiveRequest):
    """选择 / 填空 / 判断 · 规则匹配 · 不走 LLM"""
    results = []
    correct_count = 0

    for q in req.questions:
        is_correct = _normalize(q.student_answer) == _normalize(q.correct_answer)
        if is_correct:
            correct_count += 1
        results.append(GradeObjectiveResult(
            question_id=q.question_id,
            correct=is_correct,
            student_answer=q.student_answer,
            correct_answer=q.correct_answer,
        ))

    total = len(req.questions)
    return GradeObjectiveResponse(
        results=results,
        score_summary={
            "total": total,
            "correct": correct_count,
            "wrong": total - correct_count,
            "rate": round(correct_count / total, 3) if total else 0.0,
        },
    )


def _normalize(s: str) -> str:
    """简单规范化:去空格、忽略大小写、忽略全角/半角"""
    return s.strip().lower().replace(" ", "").replace(",", ",").replace(".", "。")


# ============ 主观题:作文批改(LLM + 教师二审)============
ESSAY_SYSTEM_PROMPT = """你是中学语文老师。批改这篇作文,从 4 个维度给反馈:

1. 立意(20 分):是否切题、立意是否新颖
2. 结构(20 分):是否有清晰结构、过渡是否自然
3. 语言(40 分):用词准确性、句式多样性
4. 细节(20 分):错别字 / 标点 / 病句

输出严格 JSON:
{
  "dimensions": [
    {"name": "立意", "score": 16, "max_score": 20, "comment": "..."},
    {"name": "结构", "score": 17, "max_score": 20, "comment": "..."},
    {"name": "语言", "score": 32, "max_score": 40, "comment": "..."},
    {"name": "细节", "score": 17, "max_score": 20, "comment": "..."}
  ],
  "highlights": ["亮点 1", "亮点 2"],
  "improvements": [
    {"location": "第 2 段", "original": "原句", "suggestion": "改进建议", "reason": "为什么"}
  ],
  "overall_comment": "200 字内的整体评语 · 鼓励为主"
}

纪律:
- 鼓励为主,不挖苦
- 改进建议要具体到句 · 不要笼统
- 不要打满分(留改进空间)
- 不评论思想 / 价值观相关内容
- 输出语气温和 · 不要让学生觉得被否定
- 不用「差」「烂」「笨」等否定词"""


@router.post("/essay", response_model=GradeEssayResponse)
async def grade_essay(req: GradeEssayRequest):
    """作文 LLM 初评 · 必须教师二审"""
    # 1. PII 脱敏(进 LLM 前)
    redacted_essay, _, _ = redact(req.student_answer)

    # 2. 情绪敏感话题预扫描
    sensitive = detect_sensitive_topic(req.student_answer)
    if sensitive:
        # 不进 LLM 评分 · 立即标记需教师阅读
        return GradeEssayResponse(
            dimensions=[],
            highlights=[],
            improvements=[],
            overall_comment=(
                "本作文检测到情绪敏感话题(类型:"
                + sensitive
                + "),AI 不予自动评分。"
                "请教师亲自阅读 · 必要时联系学生 / 家长 / 心理老师。"
            ),
            initial_total=0,
            requires_teacher_review=True,
            sensitive_flag=sensitive,
        )

    # 3. LLM 评分
    user = f"题目:{req.prompt}\n\n学生作文(已脱敏):\n{redacted_essay}"
    data = chat_json(ESSAY_SYSTEM_PROMPT, user, max_tokens=3000)

    # 4. 解析 + 软化标签
    dimensions = []
    for dim in data.get("dimensions", []):
        comment = soften_labels(dim.get("comment", ""))
        dimensions.append(EssayDimension(
            name=dim.get("name", ""),
            score=dim.get("score", 0),
            max_score=dim.get("max_score", 20),
            comment=comment,
        ))

    improvements = []
    for imp in data.get("improvements", []):
        improvements.append(EssayImprovement(
            location=imp.get("location", ""),
            original=imp.get("original", ""),
            suggestion=imp.get("suggestion", ""),
            reason=imp.get("reason", ""),
        ))

    overall = soften_labels(data.get("overall_comment", ""))
    initial_total = sum(d.score for d in dimensions)

    return GradeEssayResponse(
        dimensions=dimensions,
        highlights=data.get("highlights", []),
        improvements=improvements,
        overall_comment=overall + "\n\n" + AI_ASSIST_NOTICE,
        initial_total=initial_total,
        requires_teacher_review=True,   # 永远 True
    )
