"""学情分析 · 班级薄弱点 + 教学建议"""

from fastapi import APIRouter
from collections import defaultdict
from app.models.schemas import (
    ClassAnalyticsRequest, ClassAnalyticsResponse, WeakPoint,
)
from app.services.llm import chat
from app.services.teacher_block import soften_labels

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/class", response_model=ClassAnalyticsResponse)
async def class_analytics(req: ClassAnalyticsRequest):
    """班级薄弱知识点分析 · 不输出个人成绩"""
    # 1. 按知识点聚合
    kp_stats = defaultdict(lambda: {"total": 0, "wrong": 0, "wrong_students": set()})
    total_questions = 0
    total_correct = 0

    for r in req.results:
        total_questions += 1
        kp_stats[r.knowledge_point]["total"] += 1
        if r.correct:
            total_correct += 1
        else:
            kp_stats[r.knowledge_point]["wrong"] += 1
            kp_stats[r.knowledge_point]["wrong_students"].add(r.student_id)

    overall_rate = round(total_correct / total_questions, 3) if total_questions else 0.0

    # 2. 排序 · 取 TOP 5 薄弱
    weak_list = []
    for kp, stats in kp_stats.items():
        rate = (stats["total"] - stats["wrong"]) / stats["total"] if stats["total"] else 1.0
        weak_list.append(WeakPoint(
            knowledge_point=kp,
            correct_rate=round(rate, 3),
            students_need_support=len(stats["wrong_students"]),
        ))
    weak_list.sort(key=lambda x: x.correct_rate)
    top_5 = weak_list[:5]

    # 3. LLM 生成教学建议(温和)
    suggestions = await _gen_teaching_suggestions(top_5)

    return ClassAnalyticsResponse(
        overall_correct_rate=overall_rate,
        weak_points=top_5,
        teaching_suggestions=suggestions,
    )


async def _gen_teaching_suggestions(weak_points: list[WeakPoint]) -> list[str]:
    """让 LLM 给教学建议"""
    if not weak_points:
        return []

    user = "本周班级薄弱知识点(按正确率排序):\n\n"
    for i, wp in enumerate(weak_points, 1):
        user += f"{i}. {wp.knowledge_point}(正确率 {wp.correct_rate * 100:.0f}%,{wp.students_need_support} 人需要支持)\n"

    system = """你是教研组长。根据班级薄弱知识点,给老师 3-5 条具体可执行的教学建议。

要求:
- 每条建议简短具体(20-50 字)
- 不要用"差生 / 学渣"等负面词
- 温和措辞 · 不挖苦不批评
- 不推任何付费课程
- 输出每行一条建议"""

    raw = chat(system, user, max_tokens=800)
    suggestions = [soften_labels(line.strip().lstrip("·-•").strip())
                   for line in raw.split("\n")
                   if line.strip() and len(line.strip()) > 5]
    return suggestions[:5]
