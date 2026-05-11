"""Pydantic schemas · 教育行业字段契约"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# === 作业批改 ===
class ObjectiveQuestion(BaseModel):
    question_id: str
    type: Literal["multiple_choice", "fill_blank", "judge"]
    student_answer: str
    correct_answer: str


class SubjectiveQuestion(BaseModel):
    question_id: str
    type: Literal["essay", "explanation", "open_question"]
    prompt: str
    student_answer: str
    max_score: int = 100


class GradeObjectiveRequest(BaseModel):
    questions: list[ObjectiveQuestion]


class GradeObjectiveResult(BaseModel):
    question_id: str
    correct: bool
    student_answer: str
    correct_answer: str


class GradeObjectiveResponse(BaseModel):
    results: list[GradeObjectiveResult]
    score_summary: dict


class GradeEssayRequest(BaseModel):
    question_id: str
    prompt: str
    student_answer: str
    grade_stage: str = "junior_high"


class EssayDimension(BaseModel):
    name: str
    score: int
    max_score: int
    comment: str


class EssayImprovement(BaseModel):
    location: str       # 第 X 段 / 第 X 句
    original: str
    suggestion: str
    reason: str


class GradeEssayResponse(BaseModel):
    dimensions: list[EssayDimension]
    highlights: list[str]
    improvements: list[EssayImprovement]
    overall_comment: str
    initial_total: int
    requires_teacher_review: bool = True   # 永远 True
    sensitive_flag: Optional[str] = None   # 检测到敏感话题 → 教师必须人审


# === 学情分析 ===
class StudentResult(BaseModel):
    student_id: str
    knowledge_point: str
    correct: bool


class ClassAnalyticsRequest(BaseModel):
    class_id: str
    results: list[StudentResult]


class WeakPoint(BaseModel):
    knowledge_point: str
    correct_rate: float
    students_need_support: int


class ClassAnalyticsResponse(BaseModel):
    overall_correct_rate: float
    weak_points: list[WeakPoint]
    teaching_suggestions: list[str]
    notice: str = (
        "本分析仅供老师参考 · 不输出个人成绩排名 · 个人情况请走 1v1 私聊"
    )


# === 家校沟通 ===
class WeeklyReportRequest(BaseModel):
    class_id: str
    learning_data: dict       # 班级周数据
    teacher_notes: Optional[str] = None


class CommunicationIssue(BaseModel):
    issue_type: str    # 公开比较 / 标签化 / 焦虑诱导 / 越权评价 / 经济压力
    matched_text: str
    severity: Literal["block", "warn"]


class WeeklyReportResponse(BaseModel):
    draft: str
    issues: list[CommunicationIssue]
    requires_teacher_approval: bool = True
    notice: str = "周报草稿 · 教师审核签字后才能发家长群"


class ParentQARequest(BaseModel):
    question: str
    parent_id: Optional[str] = None
    child_id: Optional[str] = None


class ParentQAResponse(BaseModel):
    intent: Literal["课程安排", "作业要求", "孩子表现", "教育焦虑", "经济咨询", "其他"]
    answer: str
    redirect_to_teacher: bool = False


# === 个性化辅导 ===
class RecommendRequest(BaseModel):
    student_id: str
    subject: str
    target_count: int = 10
    weak_points: list[str] = Field(default_factory=list)
    current_mastery: dict[str, float] = Field(default_factory=dict)


class Exercise(BaseModel):
    exercise_id: str
    knowledge_point: str
    difficulty: float    # 0.0 ~ 1.0
    priority: float
    content_preview: str


class RecommendResponse(BaseModel):
    exercises: list[Exercise]
    study_plan_summary: str
    daily_load_cap_minutes: int   # 双减对齐 · 不超出年级建议时长
    notice: str = "推荐结果仅供参考 · 难度梯度受控 · 不制造刷题地狱"


# === PII 脱敏(教育版)===
class EduPIIRequest(BaseModel):
    text: str


class EduPIIResponse(BaseModel):
    redacted_text: str
    redacted_entities: list[dict]
    minor_data_detected: bool   # 是否含未成年人数据


# === Health ===
class HealthResponse(BaseModel):
    status: str
    components: dict[str, str]
