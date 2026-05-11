"""教师签字栏 + 家校沟通禁忌 + 焦虑监控 + 标签温和

教育行业核心工程纪律 · 全部场景共用
"""

import re
from datetime import date
from app.config import settings


# ============ 标签温和 ============
LABEL_REPLACEMENTS = {
    "差生":     "待提升",
    "学渣":     "需要更多支持",
    "拖后腿":   "进度需要追赶",
    "粗心":     "有提升空间",
    "笨":       "学习方式可以调整",
    "懒":       "动力需要鼓励",
    "态度差":   "投入度可以提升",
    "不努力":   "学习方法可以调整",
}


def soften_labels(text: str) -> str:
    """把负面标签替换为温和措辞"""
    result = text
    for k, v in LABEL_REPLACEMENTS.items():
        result = result.replace(k, v)
    return result


# ============ 家校沟通 5 红线 ============
FORBIDDEN_PATTERNS = [
    # 1. 公开比较
    (re.compile(r"[一-龥]{2,4}比[一-龥]{2,4}强|比[一-龥]{2,4}落后|排名第\d+"),
     "公开比较"),
    # 2. 标签化
    (re.compile(r"差生|学渣|没救|不可救药|废柴"),
     "标签化"),
    # 3. 焦虑诱导
    (re.compile(r"再这样下去|考不上|前途堪忧|无法挽回|输在起跑线"),
     "焦虑诱导"),
    # 4. 越权评价(性格 / 心理)
    (re.compile(r"性格(有|存在)问题|心理(有|存在)问题|有心理疾病"),
     "越权评价"),
    # 5. 经济压力(双减)
    (re.compile(r"建议报班|建议补课|建议购买|需要买|应该花钱"),
     "经济压力"),
]


def check_communication_taboos(text: str) -> list[dict]:
    """检查家校沟通禁忌"""
    issues = []
    for pattern, issue_type in FORBIDDEN_PATTERNS:
        for match in pattern.finditer(text):
            issues.append({
                "issue_type": issue_type,
                "matched_text": match.group(),
                "severity": "block",
            })
    return issues


# ============ 焦虑监控 ============
ANXIETY_TRIGGERS = [
    "焦虑", "睡不着", "失眠",
    "孩子哭", "我崩溃", "压力大",
    "想放弃", "不想上学", "焦头烂额",
    "天天补", "卷不动",
]


def is_anxiety_signal(text: str) -> bool:
    """检测家长 / 学生焦虑信号"""
    return any(t in text for t in ANXIETY_TRIGGERS)


CALM_RESPONSE = """理解您的感受。学习节奏快确实让人焦虑,但请注意:

· 短期成绩不代表长期能力
· 孩子需要的是支持,不是更多压力
· 您可以跟班主任沟通,了解具体进度

如果情绪持续紧张,可以试试:
· 跟孩子做一件不跟学习相关的事(散步 / 看一部电影)
· 联系心理咨询(很多学校有免费心理辅导)
· 拨打青少年心理援助热线 12355

我们一起把节奏调整好。"""


# ============ 情绪敏感话题检测(作文用)============
SENSITIVE_TOPICS = {
    "self_harm": [
        "想离开这个世界", "活着没意思", "想消失",
        "自杀", "结束自己", "不想活了",
    ],
    "family_loss": [
        "亲人去世", "爷爷去世", "奶奶去世",
        "妈妈走了", "爸爸走了",
    ],
    "abuse": [
        "家暴", "被打", "毒打",
        "侵犯", "猥亵", "性骚扰",
    ],
    "depression": [
        "感到孤独", "没有朋友", "讨厌自己",
        "活着累", "什么都没意思",
    ],
    "family_change": [
        "父母离婚", "爸妈分开", "妈妈再婚", "爸爸再婚",
    ],
}


def detect_sensitive_topic(text: str) -> str | None:
    """检测情绪敏感话题 · 返回类型或 None"""
    for topic, keywords in SENSITIVE_TOPICS.items():
        if any(k in text for k in keywords):
            return topic
    return None


# ============ 教师签字栏(强制)============
def teacher_sign_block() -> str:
    return f"""────────────────────────────────────────
本批改 / 周报由 AI 工具辅助生成,具体评分
和评语需经教师审核签字后方可发给学生 / 家长。

学校:{settings.school_name}
教师:____________  日期:____________

依据《教育法》《未成年人保护法》及教育部
AI 进校园指引,教师对最终评价承担责任。
────────────────────────────────────────

"""


# ============ AI 协助声明 ============
AI_ASSIST_NOTICE = (
    "本内容由 AI 工具辅助生成 · 仅供教学参考 · 最终评价以教师签字为准 · "
    "本工具不替代教师专业判断"
)


# ============ 不推付费课程 ============
COMMERCIAL_BLOCKLIST = [
    "建议报班", "推荐补课", "建议购买课程",
    "我们的课程", "充值会员", "扫码报名",
    "限时优惠", "立即购买",
]


def has_commercial_content(text: str) -> bool:
    return any(c in text for c in COMMERCIAL_BLOCKLIST)
