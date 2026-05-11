"""医疗 PII 脱敏 · 比通用版多 4 类(住院号 / 病历号 / 医保号 / 床位号)

进 LLM 前 + 进向量库前 · 双重脱敏
"""

import re

PATTERNS = {
    # 通用 6 类
    "ID_CARD":   re.compile(r"[1-9]\d{5}(?:18|19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])\d{3}[\dXx]"),
    "PHONE":     re.compile(r"1[3-9]\d{9}"),
    "EMAIL":     re.compile(r"[\w\.\-]+@[\w\.\-]+\.[a-zA-Z]{2,}"),
    "BANK_CARD": re.compile(r"\b\d{16,19}\b"),
    "ADDRESS":   re.compile(r"[一-龥]{2,}(省|市|区|县|镇)[一-龥A-Za-z0-9]{4,}"),

    # 医疗特化 4 类
    "INPATIENT_NO":  re.compile(r"住院号[::\s]*\d{6,12}"),
    "MEDICAL_NO":    re.compile(r"病历号[::\s]*\d{6,12}|门诊号[::\s]*\d{6,12}"),
    "INSURANCE_NO":  re.compile(r"医保号[::\s]*\d{8,18}|社保号[::\s]*\d{8,18}"),
    "BED_NO":        re.compile(r"床号[::\s]*\d{1,4}|\d{1,3}床"),

    # 中文姓名(2-4 字 · 患者 / 家属)
    "NAME":      re.compile(r"(?:患者|病人|姓名)[::\s]*([一-龥]{2,4})"),
}


def redact(text: str) -> tuple[str, dict]:
    """脱敏文本 · 返回 (脱敏后, 命中统计)"""
    redacted = text
    counts = {}
    minor_or_sensitive = False

    for key, pattern in PATTERNS.items():
        matches = pattern.findall(redacted)
        if matches:
            counts[key] = len(matches)
            for i, _ in enumerate(matches, 1):
                redacted = pattern.sub(f"[{key}_{i}]", redacted, count=1)
            # 任意医疗 ID 命中即触发敏感标记
            if key in ("INPATIENT_NO", "MEDICAL_NO", "INSURANCE_NO", "ID_CARD"):
                minor_or_sensitive = True

    return redacted, {
        "counts": counts,
        "sensitive_data_detected": minor_or_sensitive,
        "total_pii_items": sum(counts.values()),
    }
