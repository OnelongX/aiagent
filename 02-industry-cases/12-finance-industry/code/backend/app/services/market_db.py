"""市场 / 产品风险等级 mock · 适当性匹配关键

生产环境替换为:
- Wind / 同花顺 / 东方财富 · 实时行情
- 中证 / 中国基金业协会 · 产品风险评级
- 银登 / 上清所 · 信贷资产登记
- 个人征信:央行征信中心 + 百行征信 / 朴道征信

本 mock 含 12 个典型产品 + 5 级风险标准 · 直接 docker 跑通。
"""

# 5 级产品风险标准(资管新规)
PRODUCT_RISK_LEVELS = {
    "R1": "谨慎型 · 货基 / 国债 / 大额存单",
    "R2": "稳健型 · 高等级债基 / 固收+",
    "R3": "平衡型 · 偏债混合 / 中等级债",
    "R4": "进取型 · 偏股混合 / 股票基金",
    "R5": "激进型 · 私募 / 衍生品 / 高杠杆 / 单一行业",
}

# 5 级客户风险承受能力(C1-C5)
CUSTOMER_RISK_LEVELS = {
    "C1": "保守型 · 不能承受本金亏损",
    "C2": "稳健型 · 可承受 5% 以内回撤",
    "C3": "平衡型 · 可承受 10-20% 回撤",
    "C4": "积极型 · 可承受 20-40% 回撤",
    "C5": "激进型 · 可承受 40%+ 回撤",
}

# 产品 mock(通用代号 · 不指名实际基金)
PRODUCTS = {
    "MMF-001":  {"name": "示例货币基金 A",        "risk": "R1", "type": "货基"},
    "BOND-001": {"name": "示例利率债基金 A",      "risk": "R2", "type": "纯债"},
    "BOND-002": {"name": "示例信用债基金 B",      "risk": "R3", "type": "信用债"},
    "MIX-001":  {"name": "示例偏债混合 A",        "risk": "R3", "type": "混合"},
    "MIX-002":  {"name": "示例偏股混合 B",        "risk": "R4", "type": "混合"},
    "STK-001":  {"name": "示例宽基指数 A",        "risk": "R4", "type": "指数"},
    "STK-002":  {"name": "示例行业主题基金 B",    "risk": "R4", "type": "主题"},
    "STK-003":  {"name": "示例小盘成长基金",       "risk": "R5", "type": "小盘"},
    "QDII-001": {"name": "示例 QDII 全球",        "risk": "R4", "type": "QDII"},
    "PRIV-001": {"name": "示例私募 · 量化",       "risk": "R5", "type": "私募"},
    "FUT-001":  {"name": "示例商品期货 CTA",      "risk": "R5", "type": "衍生品"},
    "STR-001":  {"name": "示例结构化产品 · 雪球",  "risk": "R5", "type": "结构化"},
}


# 适当性矩阵 · 客户等级 → 可购买的产品风险等级上限
# 监管原则:不能向 C1 客户销售 R2 及以上 · 必须风险等级匹配
SUITABILITY_MATRIX = {
    "C1": {"R1"},
    "C2": {"R1", "R2"},
    "C3": {"R1", "R2", "R3"},
    "C4": {"R1", "R2", "R3", "R4"},
    "C5": {"R1", "R2", "R3", "R4", "R5"},
}


def lookup_product(code: str) -> dict | None:
    return PRODUCTS.get(code)


def is_suitable(customer_level: str, product_risk: str) -> tuple[bool, str]:
    """判断适当性 · 返回 (是否匹配, 原因)"""
    allowed = SUITABILITY_MATRIX.get(customer_level, set())
    if product_risk in allowed:
        return (True, f"客户 {customer_level} 可购买 {product_risk}")
    return (False, f"客户 {customer_level} 不可购买 {product_risk} · 违反适当性匹配")


# ============ AML 可疑交易规则 ============
# 央行《金融机构大额交易和可疑交易报告管理办法》节选简化
def aml_suspicious_score(transaction: dict) -> tuple[int, list[str]]:
    """简化 AML 评分 · 返回 (0-100, 命中规则)"""
    score = 0
    rules = []
    amount = transaction.get("amount_rmb", 0)
    count_24h = transaction.get("count_24h", 0)
    cross_border = transaction.get("cross_border", False)
    counterparty_risky = transaction.get("counterparty_risky", False)
    night_time = transaction.get("night_time", False)
    cash_intensive = transaction.get("cash_intensive", False)
    new_account = transaction.get("new_account_days", 999) <= 7

    # 大额
    if amount >= 50000:
        score += 25
        rules.append(f"大额交易 ¥{amount:,}(≥5万触发申报)")

    # 高频
    if count_24h >= 5:
        score += 20
        rules.append(f"24h 内 {count_24h} 笔(≥5 笔高频)")

    # 跨境
    if cross_border and amount >= 70000:
        score += 20
        rules.append("跨境大额(等值≥1万美元)")

    # 高风险对手方
    if counterparty_risky:
        score += 30
        rules.append("对手方位于反洗钱重点关注名单")

    # 夜间 + 大额
    if night_time and amount >= 30000:
        score += 10
        rules.append("非交易时间大额(夜间)")

    # 现金密集
    if cash_intensive:
        score += 15
        rules.append("现金密集型(短期内多笔大额现金)")

    # 新户冲量
    if new_account and amount >= 30000:
        score += 25
        rules.append("新开户 7 天内大额(可能账户出租)")

    score = min(score, 100)
    return score, rules


def aml_level(score: int) -> str:
    if score >= 70:
        return "high"     # 上报 + 限制
    if score >= 40:
        return "medium"   # 人工复核
    if score >= 20:
        return "low"      # 留痕
    return "none"
