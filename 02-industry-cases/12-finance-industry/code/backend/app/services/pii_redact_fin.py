"""金融 PII 脱敏 · 比通用版多 5 类(银行卡 / CVV / 账号 / 客户号 / 交易号)

按《个人金融信息保护技术规范》(JR/T 0171-2020)C3 级数据从严处理。
进 LLM 前 + 进向量库前 · 双重脱敏。
"""

import re

PATTERNS = {
    # 通用 6 类
    "ID_CARD":   re.compile(r"[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]"),
    "PHONE":     re.compile(r"1[3-9]\d{9}"),
    "EMAIL":     re.compile(r"[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,}"),
    "ADDRESS":   re.compile(r"[一-龥]{2,}(省|市|区|县|镇)[一-龥A-Za-z0-9]{4,}"),

    # 金融特化 5 类(C3 级敏感)
    "BANK_CARD":    re.compile(r"\b\d{16,19}\b"),
    "CVV":          re.compile(r"(?:CVV|cvv|安全码)[::\s]*\d{3,4}"),
    "ACCOUNT_NO":   re.compile(r"账号[::\s]*\d{8,20}"),
    "CUSTOMER_NO":  re.compile(r"客户号[::\s]*\d{6,12}|客户编号[::\s]*\d{6,12}"),
    "TRADE_NO":     re.compile(r"交易号[::\s]*[A-Za-z0-9]{8,32}|流水号[::\s]*[A-Za-z0-9]{8,32}"),

    # 中文姓名(可与身份证联合识别)
    "NAME":      re.compile(r"(?:客户|开户人|持有人|姓名|账户名)[::\s]*([一-龥]{2,4})"),
}


# C3 级字段(最敏感 · 任一命中即标 sensitive)
C3_KEYS = {"ID_CARD", "BANK_CARD", "CVV", "ACCOUNT_NO", "CUSTOMER_NO"}


def redact(text: str) -> tuple[str, dict]:
    """脱敏文本 · 返回 (脱敏后, 命中统计 + 敏感标记)"""
    redacted = text
    counts = {}
    sensitive = False

    for key, pattern in PATTERNS.items():
        matches = pattern.findall(redacted)
        if matches:
            counts[key] = len(matches)
            for i, _ in enumerate(matches, 1):
                redacted = pattern.sub(f"[{key}_{i}]", redacted, count=1)
            if key in C3_KEYS:
                sensitive = True

    return redacted, {
        "counts": counts,
        "c3_sensitive_data_detected": sensitive,
        "total_pii_items": sum(counts.values()),
    }
