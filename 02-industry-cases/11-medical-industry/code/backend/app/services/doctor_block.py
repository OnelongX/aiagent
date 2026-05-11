"""医师签字栏 + 急救熔断 + 建议性语言软化 + 临床免责

医疗行业核心工程纪律 · 全部场景共用
"""

import re
from datetime import date
from app.config import settings


# ============ 急救熔断(最高优先级 · 不进 LLM)============
EMERGENCY_KEYWORDS = [
    # 心血管
    "胸痛", "胸闷剧烈", "心绞痛", "心梗", "心脏骤停",
    # 神经
    "意识丧失", "昏迷", "中风", "脑出血", "脑梗", "癫痫大发作", "抽搐不止",
    # 呼吸
    "呼吸困难", "窒息", "喉头水肿", "无法呼吸",
    # 创伤 / 出血
    "大出血", "动脉出血", "刀伤", "枪伤", "车祸", "高空坠落",
    # 中毒
    "中毒", "吞药", "误服", "服毒", "煤气中毒", "一氧化碳",
    # 精神
    "自杀", "想结束生命", "正在割腕", "跳楼",
    # 严重过敏
    "过敏性休克", "全身水肿", "喉咙发紧",
    # 产科
    "羊水破", "见红", "临产", "早产",
]


def is_emergency(text: str) -> tuple[bool, list[str]]:
    """急救场景检测 · 返回 (是否, 命中的关键词)"""
    hits = [k for k in EMERGENCY_KEYWORDS if k in text]
    return (len(hits) > 0, hits)


EMERGENCY_RESPONSE = f"""⚠️ **疑似急救场景 · 请立即联系专业医疗人员**

请**立即**采取以下措施(不要等待 AI 回复):

1️⃣ **拨打急救电话 {settings.emergency_phone}**(全国通用)
2️⃣ 中毒情况:**{settings.poison_hotline}**(国家中毒控制中心)
3️⃣ 精神 / 自伤危机:**{settings.mental_hotline}**(全国心理援助)

在急救人员到达前:
· 保持患者气道通畅
· 不要随意搬动疑似脊柱 / 头部受伤者
· 大出血压迫止血(干净布料)
· 中毒者不要自行催吐(强酸 / 强碱 / 石油类禁催吐)

🚫 本 AI 工具不进行任何在线诊断或处置建议,
请以现场医师 / 急救中心指令为准。"""


# ============ 建议性语言软化(不能下医嘱)============
ADVICE_SOFTENING = {
    # AI 不能下医嘱 · 不能给定性诊断
    "你患有":             "影像 / 症状提示可能存在",
    "你得了":             "需要进一步评估是否为",
    "你应该立即服用":     "如医师评估同意,可考虑使用",
    "建议你服用":         "请医师评估后决定是否使用",
    "推荐剂量":           "常见参考剂量(以医师处方为准)",
    "需要手术":           "可能需要外科评估",
    "不需要看医生":       "建议由医师评估必要性",
    "可以自己用药":       "请在医师 / 药师指导下用药",
    "肯定是":             "影像 / 症状提示可能为",
    "确诊":               "提示需进一步检查确认",
    "排除了":             "本次检查未见明确",
}


def soften_advice(text: str) -> str:
    result = text
    for k, v in ADVICE_SOFTENING.items():
        result = result.replace(k, v)
    return result


# 强建议性禁词(检测但不替换 · 给 reviewer 标黄)
STRONG_ADVICE_PATTERNS = [
    re.compile(r"必须立即|一定要|绝对不能|只能"),
    re.compile(r"100% (是|不是|确定)"),
    re.compile(r"包治|根治|彻底治愈|永不复发"),
]


def detect_strong_advice(text: str) -> list[str]:
    hits = []
    for p in STRONG_ADVICE_PATTERNS:
        hits.extend(p.findall(text))
    return hits


# ============ 商品名 → 通用名(防带货)============
# AI 输出禁出现商品名 · 必须用国际非专利名(INN)
COMMERCIAL_DRUG_BLOCKLIST = [
    "立普妥", "波立维", "拜阿司匹林", "络活喜", "代文",
    "诺和灵", "格华止", "拜糖平", "倍他乐克", "雅施达",
    "泰诺", "白加黑", "感康", "新康泰克",
]


def detect_commercial_drug(text: str) -> list[str]:
    return [d for d in COMMERCIAL_DRUG_BLOCKLIST if d in text]


# ============ 特殊人群标注 ============
SPECIAL_POPULATIONS = {
    "pregnancy":  ["孕", "怀孕", "妊娠", "孕妇"],
    "lactation":  ["哺乳", "母乳", "喂奶"],
    "pediatric":  ["儿童", "小儿", "婴儿", "新生儿", "小孩"],
    "geriatric":  ["老年", "高龄", "80岁", "90岁"],
    "renal":      ["肾功能不全", "尿毒症", "透析", "肾衰"],
    "hepatic":    ["肝功能不全", "肝硬化", "肝衰"],
}


def detect_special_population(text: str) -> list[str]:
    hits = []
    for pop, keywords in SPECIAL_POPULATIONS.items():
        if any(k in text for k in keywords):
            hits.append(pop)
    return hits


# ============ 医师签字栏(强制)============
def doctor_sign_block(scenario: str = "诊疗辅助") -> str:
    return f"""════════════════════════════════════════
本{scenario}由 AI 工具辅助生成,**不构成诊断
或处方**。最终诊断 / 用药 / 处置以执业医师
签字为准。

医疗机构:{settings.hospital_name}
科室:{settings.department}
执业医师:______________
执业证号:______________
签字日期:______________

依据《医师法》《处方管理办法》及国家卫健委
《医疗机构应用人工智能技术管理规范》,
医师对最终医疗决策承担全部责任。
════════════════════════════════════════

"""


# ============ AI 协助声明 ============
def ai_disclaimer(context: str = "") -> str:
    return f"""

────────────────────────────────────────
⚕️ **重要声明**

本内容由 AI 辅助生成,**不替代医师面诊**。
{context}

· 急救拨打 {settings.emergency_phone}
· 中毒拨打 {settings.poison_hotline}
· 心理援助拨打 {settings.mental_hotline}
· 互联网医院仅限复诊,首诊请到线下医疗机构

本 AI 不诊断 · 不开方 · 不替代医师
────────────────────────────────────────
"""


# ============ 医保 / 商品名 / 推广限制 ============
COMMERCIAL_BLOCKLIST = [
    "推荐购买", "建议购买", "我们的药",
    "限时优惠", "买一送一", "扫码下单",
    "私立医院", "高端套餐", "VIP 医疗",
]


def has_commercial_content(text: str) -> bool:
    return any(c in text for c in COMMERCIAL_BLOCKLIST)
