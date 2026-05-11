"""合规签字栏 + 投教语言 + 反诈熔断 + 反歧视 + 反荐股

金融行业核心工程纪律 · 全部场景共用 · 跟证监会 / 银保监 / 央行规范对齐
"""

import re
from app.config import settings


# ============ 反诈 / 反洗钱熔断(最高优先级 · 不进 LLM)============
FRAUD_KEYWORDS = [
    # 反诈高频
    "刷单", "返利", "杀猪盘", "高息理财", "稳赚不赔",
    "内幕消息", "保证收益", "无风险高收益",
    "私募群", "导师带单", "稳定盈利",
    # 钓鱼 / 诈骗
    "客服来电", "公检法账户", "安全账户", "解冻账户",
    "billing.gov", "phishing",
    # 洗钱信号
    "代收代付", "对公转私", "拆分转账", "频繁过水",
    # 高风险贷款
    "套路贷", "714 高炮", "强制下款", "AB 贷",
]


def is_fraud_signal(text: str) -> tuple[bool, list[str]]:
    hits = [k for k in FRAUD_KEYWORDS if k in text]
    return (len(hits) > 0, hits)


FRAUD_RESPONSE = f"""⚠️ **疑似涉诈 / 高风险场景 · 请立即停止操作**

**任何"稳赚""保本""内幕"都是诈骗。**

请**立即**采取:

1️⃣ 不要再转账 · 不要再扫码 · 不要再泄露任何验证码
2️⃣ 反诈预警:**{settings.fraud_hotline}**(可咨询当地反诈中心)
3️⃣ 国家反诈中心 App / "96110"全国反诈专线
4️⃣ 涉及证券类:**{settings.investor_protect_hotline}**(证监会投资者保护)
5️⃣ 涉及银行 / 保险:**{settings.bank_complaint_hotline}**(银保监投诉)

📌 如已转账,**立即拨打 110 + 联系银行 / 第三方支付冻结**。

🚫 本 AI 工具不参与任何"高息""保本""内幕"类对话,
我们的回复永远是:**远离 + 报警 + 找持牌机构**。"""


# ============ 投教语言软化(不能荐股 / 不能预测)============
ADVISORY_SOFTENING = {
    # AI 不能荐股 · 不能预测涨跌
    "建议买入":             "您可以了解此类资产的特征",
    "推荐买入":             "投资决策请结合自身风险承受能力",
    "立即买入":             "决策前请阅读募集说明书",
    "建议卖出":             "可结合个人持仓 / 风险考量",
    "保证收益":             "本金及收益不被保证",
    "稳赚":                 "投资有风险",
    "稳定盈利":             "市场存在波动 · 收益不被保证",
    "无风险":               "任何投资均存在风险",
    "肯定涨":               "市场表现取决于多种因素",
    "肯定跌":               "市场存在波动",
    "翻倍":                 "收益与风险并存",
    "暴涨":                 "市场存在剧烈波动",
    "牛股":                 "标的具体表现请参考公开信息",
    "操作建议:":           "投资者教育内容:",
    "建议加仓":             "仓位管理请结合自身配置",
    "建议清仓":             "请结合再平衡需要审慎决策",
}


def soften_advisory(text: str) -> str:
    result = text
    for k, v in ADVISORY_SOFTENING.items():
        result = result.replace(k, v)
    return result


# 强建议性禁词检测(检测但不替换 · 给 reviewer 标黄)
STRONG_ADVISORY_PATTERNS = [
    re.compile(r"必须(买|卖|加仓|清仓)"),
    re.compile(r"绝对(赚|亏|不会|会)"),
    re.compile(r"\d+%\s*(收益|回报)"),
    re.compile(r"(包|保)赚|包赔|包回本"),
    re.compile(r"年化\s*\d{2,}\s*%"),  # 异常高年化
]


def detect_strong_advisory(text: str) -> list[str]:
    hits = []
    for p in STRONG_ADVISORY_PATTERNS:
        hits.extend(p.findall(text))
    return hits


# ============ 个股 / 具体产品检测(投教不能指名)============
def detect_specific_stock(text: str) -> list[str]:
    """检测六位股票代码 · A 股"""
    return re.findall(r"\b(?:6\d{5}|0\d{5}|3\d{5})\b", text)


# ============ 反歧视(信贷场景)============
DISCRIMINATION_FIELDS = {
    "age":       ["太老", "年纪大", "高龄不批", "年轻不批"],
    "gender":    ["女性不批", "男性不批", "孕妇不批"],
    "ethnicity": ["少数民族不批", "汉族优先", "民族歧视"],
    "region":    ["河南不批", "东北不批", "新疆不批"],   # 任何地域黑
    "marital":   ["未婚不批", "离异不批", "单身不批"],
}


def detect_discrimination(decision_reason: str) -> list[dict]:
    hits = []
    for field, patterns in DISCRIMINATION_FIELDS.items():
        for p in patterns:
            if p in decision_reason:
                hits.append({"field": field, "matched": p})
    return hits


# ============ 合规签字栏(强制)============
def compliance_sign_block(scenario: str = "金融服务") -> str:
    return f"""════════════════════════════════════════
本{scenario}由 AI 工具辅助生成,**不构成投资
建议 / 信贷决定 / 合规结论**。最终决策以
持牌机构合规专员签字为准。

机构:{settings.institution_name}
许可证号:{settings.institution_license}
合规专员:____________  执业编号:________
签字日期:______________________________

依据《商业银行互联网贷款管理暂行办法》
《证券期货投资者适当性管理办法》《反洗钱法》
《个人金融信息保护技术规范》(JR/T 0171),
持牌机构对最终金融决策承担全部责任。
════════════════════════════════════════

"""


# ============ AI 协助声明 ============
def ai_disclaimer(context: str = "") -> str:
    return f"""

────────────────────────────────────────
🏦 **重要声明**

本内容由 AI 辅助生成 · **不构成投资建议**。
{context}

· 反诈热线 {settings.fraud_hotline} / 96110 全国反诈
· 证券投保 {settings.investor_protect_hotline}(证监会)
· 银保监投诉 {settings.bank_complaint_hotline}
· 投资有风险 · 入市需谨慎 · 历史业绩不预示未来

本 AI 不荐股 · 不授信 · 不替代合规审查
────────────────────────────────────────
"""


# ============ 营销 / 推广禁词 ============
COMMERCIAL_BLOCKLIST = [
    "推荐购买", "限时优惠", "扫码下单",
    "我们的产品", "私募群", "稳赚团",
    "VIP 通道", "内部价", "保本理财",
]


def has_commercial_content(text: str) -> bool:
    return any(c in text for c in COMMERCIAL_BLOCKLIST)
