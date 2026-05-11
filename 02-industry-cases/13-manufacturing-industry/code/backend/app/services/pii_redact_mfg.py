"""制造行业 PII / 商业秘密脱敏 · 加 4 类工厂特化

工厂场景 PII 不像金融那么敏感 ·
但**配方 / 工艺参数 / 客户料号 / 在制品序列号**才是核心机密。
"""

import re

PATTERNS = {
    # 通用 4 类
    "ID_CARD":  re.compile(r"[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]"),
    "PHONE":    re.compile(r"1[3-9]\d{9}"),
    "EMAIL":    re.compile(r"[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,}"),
    "NAME":     re.compile(r"(?:操作工|班组长|工程师|工号)[::\s]*([一-龥]{2,4})"),

    # 制造特化 4 类
    "EMPLOYEE_ID": re.compile(r"工号[::\s]*[A-Z0-9]{4,12}"),
    "SN":          re.compile(r"SN[::\s]*[A-Z0-9\-]{6,32}|序列号[::\s]*[A-Z0-9\-]{6,32}"),
    "CUSTOMER_PN": re.compile(r"客户料号[::\s]*[A-Z0-9\-]{4,20}|Customer P/N[::\s]*[A-Z0-9\-]{4,20}"),
    "BATCH_NO":    re.compile(r"批次号[::\s]*[A-Z0-9\-]{4,20}|Lot[::\s]*[A-Z0-9\-]{4,20}"),
}

# 商业秘密级字段(C3 等价 · 决不能进公有云 LLM 明文)
SECRET_KEYS = {"CUSTOMER_PN", "BATCH_NO", "SN"}


def redact(text: str) -> tuple[str, dict]:
    redacted = text
    counts = {}
    secret_detected = False

    for key, pattern in PATTERNS.items():
        matches = pattern.findall(redacted)
        if matches:
            counts[key] = len(matches)
            for i, _ in enumerate(matches, 1):
                redacted = pattern.sub(f"[{key}_{i}]", redacted, count=1)
            if key in SECRET_KEYS:
                secret_detected = True

    return redacted, {
        "counts": counts,
        "trade_secret_detected": secret_detected,
        "total_pii_items": sum(counts.values()),
    }
