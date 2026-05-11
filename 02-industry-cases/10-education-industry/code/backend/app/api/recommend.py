"""个性化辅导 · 题目推荐(双减对齐)"""

from fastapi import APIRouter
from app.models.schemas import RecommendRequest, RecommendResponse, Exercise
from app.config import settings

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


# 双减对齐:每天作业建议时长(分钟)
DAILY_LOAD_CAP = {
    "primary":     60,    # 小学:不超 60 分钟
    "junior_high": 90,    # 初中:不超 90 分钟
    "senior_high": 120,   # 高中:120 分钟
}


# Mock 题库(生产环境:接学校题库 / 教研院题库)
MOCK_EXERCISES = {
    "一元一次方程": [
        {"id": "MQ001", "difficulty": 0.4, "content": "解方程 2x + 3 = 11"},
        {"id": "MQ002", "difficulty": 0.5, "content": "应用题:小明买文具花了 ..."},
        {"id": "MQ003", "difficulty": 0.6, "content": "..."},
    ],
    "一次函数": [
        {"id": "FQ001", "difficulty": 0.5, "content": "y = 2x + 1 经过哪些点"},
        {"id": "FQ002", "difficulty": 0.6, "content": "求函数 y = 3x - 2 的斜率"},
    ],
    # ...
}


@router.post("", response_model=RecommendResponse)
async def recommend(req: RecommendRequest):
    """基于薄弱知识点 + 掌握度推荐题目"""
    candidates = []

    for kp in req.weak_points:
        mastery = req.current_mastery.get(kp, 0.5)
        # 难度梯度:略高于当前掌握度(防挫败)
        target_range = (mastery + 0.1, min(mastery + 0.3, 1.0))

        for q in MOCK_EXERCISES.get(kp, []):
            if target_range[0] <= q["difficulty"] <= target_range[1]:
                priority = (1 - mastery)  # 越弱越优先
                candidates.append(Exercise(
                    exercise_id=q["id"],
                    knowledge_point=kp,
                    difficulty=q["difficulty"],
                    priority=round(priority, 3),
                    content_preview=q["content"][:60],
                ))

    # 多样性 rerank:同一知识点不要堆太多
    candidates = _diversify(candidates, max_per_kp=3)

    # 取 top N
    candidates.sort(key=lambda x: -x.priority)
    selected = candidates[: req.target_count]

    # 学习计划(简化)
    plan = _generate_study_plan(selected, req.subject)

    # 双减:每天上限
    cap = DAILY_LOAD_CAP.get(settings.grade_stage, 90)

    return RecommendResponse(
        exercises=selected,
        study_plan_summary=plan,
        daily_load_cap_minutes=cap,
    )


def _diversify(exercises: list[Exercise], max_per_kp: int = 3) -> list[Exercise]:
    """同一知识点不超过 max_per_kp 题"""
    count_by_kp: dict[str, int] = {}
    result = []
    for ex in exercises:
        if count_by_kp.get(ex.knowledge_point, 0) < max_per_kp:
            result.append(ex)
            count_by_kp[ex.knowledge_point] = count_by_kp.get(ex.knowledge_point, 0) + 1
    return result


def _generate_study_plan(exercises: list[Exercise], subject: str) -> str:
    if not exercises:
        return "暂无推荐题目"
    kps = list(set(e.knowledge_point for e in exercises))
    return (
        f"本次推荐覆盖 {len(kps)} 个薄弱知识点:{', '.join(kps[:3])}"
        f"{'...' if len(kps) > 3 else ''}\n\n"
        f"建议:按推荐顺序完成,遇到不会的先看课本对应章节。\n\n"
        f"⚠️ 不要超过每日建议时长(双减政策)· 学习以理解为主、刷题为辅。"
    )
