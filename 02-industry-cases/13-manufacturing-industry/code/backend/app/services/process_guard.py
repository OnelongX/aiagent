"""工艺签字栏 + 物理边界 + 安全熔断 + 配方机密保护

制造行业核心工程纪律 · 全部场景共用
"""

import re
from app.config import settings


# ============ 安全熔断(最高优先级 · 不进 LLM)============
SAFETY_KEYWORDS = [
    # 危化品 / 燃爆
    "氢气泄漏", "氨气泄漏", "VOC 超标", "可燃气体报警", "硫化氢",
    "明火", "起火", "燃爆", "化学品溅出",
    # 高温 / 高压
    "炉温失控", "压力超限", "PTC 报警", "急停按钮按下",
    # 人身
    "人员受伤", "夹伤", "电击", "灼伤", "化学伤",
    # 大停机
    "全线停机", "断电", "联锁失效", "DCS 失联",
]


def is_safety_incident(text: str) -> tuple[bool, list[str]]:
    hits = [k for k in SAFETY_KEYWORDS if k in text]
    return (len(hits) > 0, hits)


SAFETY_RESPONSE = f"""🚨 **疑似安全事故 / 工艺联锁触发 · 立即按 SOP 应急**

**禁止任何 AI 推理介入** —— 这是安全红线。

请**立即**采取:

1️⃣ 立即按下急停 · 人员撤离至上风向集合点
2️⃣ 拨打厂内 EHS / 安委办分机:**{settings.eshs_hotline}**
3️⃣ 火灾 / 化学品事故 · 拨打 **{settings.safety_hotline}**
4️⃣ 触发 MES 异常工单 + 通知值班工程师 + 班组长
5️⃣ 不要尝试自行复位联锁 · 等待安全工程师现场确认

📌 复产前必须完成:**安全确认 + 工艺确认 + 设备确认** 三联签字。

🚫 本 AI 工具不进行任何应急处置建议 ·
请以现场 SOP / 工艺值班工程师为准。"""


# ============ 工艺参数物理边界 ============
# (温度 / 压力 / 时间 / 转速 等) · 不能超物理极限
# 这是工艺安全 + 设备保护的最后一道防线
PROCESS_BOUNDARIES = {
    # 烧结炉
    "sinter_temp_c":     {"min": 200,  "max": 850,  "unit": "°C"},
    "sinter_time_min":   {"min": 5,    "max": 180,  "unit": "min"},
    # 涂层
    "coating_speed_mms": {"min": 5,    "max": 200,  "unit": "mm/s"},
    "coating_thick_um":  {"min": 1,    "max": 50,   "unit": "μm"},
    # SMT 回流焊
    "reflow_peak_c":     {"min": 215,  "max": 260,  "unit": "°C"},
    "reflow_tal_s":      {"min": 30,   "max": 90,   "unit": "s"},   # 液相时间
    # 注塑
    "injection_temp_c":  {"min": 150,  "max": 300,  "unit": "°C"},
    "injection_press_mpa": {"min": 30, "max": 200,  "unit": "MPa"},
    "cooling_time_s":    {"min": 5,    "max": 120,  "unit": "s"},
    # CVD
    "cvd_temp_c":        {"min": 300,  "max": 1100, "unit": "°C"},
    "cvd_press_pa":      {"min": 1,    "max": 100000, "unit": "Pa"},
    # 通用
    "line_speed_pcs_h":  {"min": 1,    "max": 5000, "unit": "pcs/h"},
}


def check_boundary(param_key: str, value: float) -> tuple[bool, str]:
    """检查参数是否在物理边界内 · 返回 (是否合规, 说明)"""
    bd = PROCESS_BOUNDARIES.get(param_key)
    if bd is None:
        return True, f"{param_key} 未配置边界 · 跳过"
    if value < bd["min"]:
        return False, f"{param_key} = {value}{bd['unit']} · 低于物理下限 {bd['min']}{bd['unit']}"
    if value > bd["max"]:
        return False, f"{param_key} = {value}{bd['unit']} · 超过物理上限 {bd['max']}{bd['unit']} · 烧设备 / 安全风险"
    return True, f"{param_key} = {value}{bd['unit']} · 在 [{bd['min']}, {bd['max']}] 范围内"


# ============ 配方机密字段脱敏 ============
# 工艺配方是核心商业秘密 · 进 LLM 前必须脱敏关键比例
# (这里 mock · 生产环境对接 PLM / BOM 系统)
RECIPE_SECRET_PATTERNS = [
    re.compile(r"配方代号[::\s]*[A-Z0-9\-]+"),
    re.compile(r"专利号[::\s]*ZL[\d\.]+"),
    re.compile(r"催化剂\s*[A-Z]+\d+"),
    re.compile(r"添加剂\s*[A-Z]+\d+"),
    re.compile(r"BOM\s*[A-Z0-9\-]+"),
]


def mask_recipe_secrets(text: str) -> tuple[str, int]:
    masked = text
    count = 0
    for p in RECIPE_SECRET_PATTERNS:
        matches = p.findall(masked)
        count += len(matches)
        masked = p.sub("[RECIPE_SECRET]", masked)
    return masked, count


# ============ 建议性语言软化(质检 / PdM 不出最终结论)============
ADVICE_SOFTENING = {
    "确定是缺陷":         "影像提示可能存在",
    "判定为不良品":       "建议 QC 复核为",
    "必须报废":           "建议进入待 QC 判定",
    "马上停机":           "建议立即上报值班工程师停机评估",
    "肯定会坏":           "存在故障倾向 · 建议人工巡检",
    "100% 不良":          "AI 检测置信度高 · 请 QC 终判",
    "立即更换":           "建议维护组按 SOP 评估更换",
    "无需检查":           "建议保留例行检查节奏",
    "不会出问题":         "工艺窗口内运行 · 仍建议监控",
    "完全合规":           "AI 视角未发现异常 · 仍以 QC / SQE 终判为准",
}


def soften_advice(text: str) -> str:
    result = text
    for k, v in ADVICE_SOFTENING.items():
        result = result.replace(k, v)
    return result


STRONG_ADVICE_PATTERNS = [
    re.compile(r"必须|绝对|一定|肯定"),
    re.compile(r"100%\s*(合格|不良|损坏|正常)"),
    re.compile(r"包(良率|合格率)"),
]


def detect_strong_advice(text: str) -> list[str]:
    hits = []
    for p in STRONG_ADVICE_PATTERNS:
        hits.extend(p.findall(text))
    return hits


# ============ 工艺签字栏(强制)============
def process_sign_block(scenario: str = "工艺辅助") -> str:
    return f"""════════════════════════════════════════
本{scenario}由 AI 工具辅助生成,**不构成工艺
变更 / 质检判定 / 维修指令**。最终执行以
工艺工程师 / QC / 维修组签字为准。

工厂:{settings.factory_name}
车间:{settings.workshop} 产线:{settings.line_code}
工艺工程师:____________  工号:__________
质量工程师:____________  工号:__________
签字日期:______________________________

依据《质量管理体系 ISO 9001》《IATF 16949》
《生产安全事故应急条例》及工厂内部 SOP,
工艺 / QC / 维护对各自决策承担责任。
════════════════════════════════════════

"""


def ai_disclaimer(context: str = "") -> str:
    return f"""

────────────────────────────────────────
🏭 **重要声明**

本内容由 AI 辅助生成 · **不替代 SOP / 工艺评审 / QC 终判**。
{context}

· 安全事故立即 EHS / {settings.safety_hotline}
· 工艺变更走 ECN / ECO 流程
· 质检最终以 QC 检验报告盖章为准
· MES 写操作必须工艺工程师授权

本 AI 不下结论 · 不下指令 · 不替代签字
────────────────────────────────────────
"""
