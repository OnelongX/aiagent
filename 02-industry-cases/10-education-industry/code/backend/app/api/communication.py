"""家校沟通 · 周报草稿 + 家长答疑"""

from fastapi import APIRouter
from app.models.schemas import (
    WeeklyReportRequest, WeeklyReportResponse, CommunicationIssue,
    ParentQARequest, ParentQAResponse,
)
from app.services.llm import chat
from app.services.teacher_block import (
    soften_labels, check_communication_taboos,
    is_anxiety_signal, CALM_RESPONSE, has_commercial_content,
    teacher_sign_block, AI_ASSIST_NOTICE,
)

router = APIRouter(prefix="/api/communication", tags=["communication"])


# ============ 周报草稿 ============
WEEKLY_REPORT_PROMPT = """你是中小学班主任。根据班级周数据起草一份周报草稿,准备发家长群。

要求:
1. 整体情况 + 本周亮点(具体 · 不空泛)
2. 下周教学重点
3. 家校配合建议(可选)

严格纪律(很重要):
- 不写个人成绩 / 排名 / 比较
- 不用"差生 / 学渣 / 拖后腿"等标签
- 不用"再这样下去 / 考不上"等焦虑诱导语
- 不评论学生性格 / 心理
- 不推任何付费课程 / 课外班
- 用具体行为描述(如"完成 23/25 次作业")替代模糊评价
- 温和鼓励为主

输出周报正文(不要 JSON / markdown 标记)"""


@router.post("/weekly-report", response_model=WeeklyReportResponse)
async def weekly_report(req: WeeklyReportRequest):
    # 1. LLM 起草
    user = f"班级周数据:\n{req.learning_data}\n\n"
    if req.teacher_notes:
        user += f"教师备注:{req.teacher_notes}\n"
    user += "\n请起草本周周报。"

    draft = chat(WEEKLY_REPORT_PROMPT, user, max_tokens=2000)

    # 2. 软化标签
    draft = soften_labels(draft)

    # 3. 检查家校沟通禁忌
    raw_issues = check_communication_taboos(draft)
    issues = [
        CommunicationIssue(
            issue_type=i["issue_type"],
            matched_text=i["matched_text"],
            severity=i["severity"],
        )
        for i in raw_issues
    ]

    # 4. 商业内容检测
    if has_commercial_content(draft):
        issues.append(CommunicationIssue(
            issue_type="经济压力",
            matched_text="(检测到付费推荐内容)",
            severity="block",
        ))

    # 5. 加教师签字栏 + AI 协助声明
    final = teacher_sign_block() + draft + "\n\n──\n" + AI_ASSIST_NOTICE

    return WeeklyReportResponse(
        draft=final,
        issues=issues,
        requires_teacher_approval=True,
    )


# ============ 家长答疑 ============
INTENT_KEYWORDS = {
    "课程安排": ["几点", "时间", "课程", "周几", "几号", "考试时间", "放假"],
    "作业要求": ["作业", "明天交", "下周交", "怎么做", "写哪", "格式"],
    "孩子表现": ["我家孩子", "孩子的", "我儿子", "我女儿", "成绩", "排名", "进步"],
    "经济咨询": ["补课", "报班", "买什么", "推荐课", "多少钱", "费用"],
}


def classify_parent_intent(question: str) -> str:
    if is_anxiety_signal(question):
        return "教育焦虑"
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in question for kw in keywords):
            return intent
    return "其他"


@router.post("/parent-qa", response_model=ParentQAResponse)
async def parent_qa(req: ParentQARequest):
    intent = classify_parent_intent(req.question)

    # 1. 教育焦虑 → 引导性回复(不强化)
    if intent == "教育焦虑":
        return ParentQAResponse(
            intent="教育焦虑",
            answer=CALM_RESPONSE,
            redirect_to_teacher=True,
        )

    # 2. 孩子表现 → 不给 AI 直答(避免 AI 编评价)
    if intent == "孩子表现":
        return ParentQAResponse(
            intent="孩子表现",
            answer=(
                "您好,关于孩子的具体表现,建议向班主任了解。\n\n"
                "班主任在工作时间(早 8 点 - 晚 6 点)回复消息会更及时。\n\n"
                "如果想看进度数据,可以在「家长端 → 学情」查看具体作业完成情况。"
            ),
            redirect_to_teacher=True,
        )

    # 3. 经济咨询 → 不推任何付费(双减)
    if intent == "经济咨询":
        return ParentQAResponse(
            intent="经济咨询",
            answer=(
                "本系统不推荐任何付费课程 / 补习班。\n\n"
                "如果您觉得孩子需要额外辅导,建议:\n"
                "1. 先与班主任沟通学习进度\n"
                "2. 利用学校提供的免费辅导资源\n"
                "3. 关注义务教育阶段的「双减」政策"
            ),
            redirect_to_teacher=False,
        )

    # 4. 课程安排 / 作业要求 → 可以正常答(标准化信息)
    system = """你是中小学家长答疑助手。回答家长关于课程安排 / 作业要求的问题。

要求:
- 用礼貌、专业、温和的语气
- 不评论任何学生个人情况
- 不推荐任何付费课程
- 如果不知道,建议联系班主任
- 答案简洁明了"""

    answer = chat(system, req.question, max_tokens=800)

    # 后处理:商业内容检查
    if has_commercial_content(answer):
        answer = "您好,该问题建议直接询问班主任,以便获得准确信息。"

    return ParentQAResponse(
        intent=intent,
        answer=answer,
        redirect_to_teacher=(intent == "其他"),
    )
