"""PII 脱敏 · 法律行业双重保护(GDPR + PIPL)。

进 LLM 前必须脱敏:
- 客户机密
- 当事人 PII(姓名 / 身份证 / 手机 / 地址 / 邮箱)
- 案件标识(案号 · 在某些场景需脱敏)
"""

import re
from app.config import settings


# === 正则模式 ===
PATTERNS = {
    # 身份证(15 或 18 位)
    "ID_CARD": re.compile(r"\b\d{17}[\dXx]\b|\b\d{15}\b"),
    # 手机号(11 位)
    "PHONE": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    # 邮箱
    "EMAIL": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    # 银行卡(13-19 位连续数字)
    "BANK_CARD": re.compile(r"(?<!\d)\d{13,19}(?!\d)"),
    # 中文姓名(2-4 个中文字符 · 简化版 · 误报多 · 实际生产用 NER)
    "NAME": re.compile(r"(?<=[原被告诉申请人方:、,])\s*[一-龥]{2,4}(?=[,。;、\s])"),
    # 详细地址(省市 + 具体街道)
    "ADDRESS": re.compile(
        r"[北上广深杭成重武天津南西哈福苏][一-龥]{2,8}(市|省|区|县)"
        r"[一-龥]{2,30}(路|街|道|号|楼|室)"
    ),
    # 案号(脱敏可选 · 看场景)
    # "CASE_NUMBER": re.compile(r"\([\d]{4}\)[一-龥\d]+号"),
}


def redact(text: str) -> tuple[str, list[dict]]:
    """脱敏处理 · 返回 (脱敏后文本, 实体清单)。"""
    if not settings.pii_redact_enabled:
        return text, []

    redacted = text
    entities = []
    counter = {k: 0 for k in PATTERNS}

    for pii_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            counter[pii_type] += 1
            original = match.group()
            placeholder = f"[{pii_type}_{counter[pii_type]}]"
            entities.append({
                "type": pii_type,
                "original": original,
                "placeholder": placeholder,
                "position": match.span(),
            })

    # 应用替换(从后往前 · 不影响 position)
    entities_sorted = sorted(entities, key=lambda e: -e["position"][0])
    for e in entities_sorted:
        start, end = e["position"]
        redacted = redacted[:start] + e["placeholder"] + redacted[end:]

    return redacted, entities


def restore(text: str, entities: list[dict]) -> str:
    """恢复脱敏 · 用于内部展示给律师(不对外)。"""
    result = text
    for e in entities:
        result = result.replace(e["placeholder"], e["original"])
    return result


if __name__ == "__main__":
    # 自测
    sample = """
    原告:张三, 身份证号 110101199001011234, 手机 13800138000,
    住北京市朝阳区建国路 88 号 101 室, 邮箱 zhangsan@example.com。
    被告:李四, 身份证号 320105198506157890。
    """
    r, e = redact(sample)
    print("脱敏后:", r)
    print("\n实体清单:")
    for x in e:
        print(f"  {x['type']}: {x['original']} → {x['placeholder']}")
