"""教育行业 PII 脱敏 · 比成人 PII 更严

未成年人保护法 + PIPL · 14 岁以下需父母同意才能收集
"""

import re
from app.config import settings


PATTERNS = {
    "ID_CARD":   re.compile(r"\b\d{17}[\dXx]\b|\b\d{15}\b"),
    "PHONE":     re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "EMAIL":     re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "STUDENT_ID": re.compile(r"(?<![A-Za-z\d])\d{8,12}(?![A-Za-z\d])"),  # 学号(简化)
    # 中文姓名(在原 / 被 / 学生 等上下文)
    "NAME": re.compile(
        r"(?<=[学生孩子同学班主任老师家长母亲父亲妈妈爸爸:、,])\s*[一-龥]{2,4}(?=[,。;、\s])"
    ),
    # 学校名(简化:含"学校"/"中学"/"小学")
    "SCHOOL": re.compile(r"[一-龥]{2,15}(中学|小学|学校|大学|学院)"),
    # 班级
    "CLASS":  re.compile(r"[一-龥0-9]+年级[一-龥0-9]+班"),
    # 家庭住址(简化)
    "ADDRESS": re.compile(
        r"[一-龥]{2,8}(市|省|区|县)[一-龥]{2,30}(路|街|道|号|楼|室)"
    ),
}


# 学龄相关词触发"未成年标记"
MINOR_INDICATORS = ["学生", "孩子", "同学", "小学", "中学", "初中", "高中", "K-12"]


def redact(text: str) -> tuple[str, list[dict], bool]:
    """脱敏 + 检测是否含未成年人数据。

    返回:
      - redacted_text: 脱敏后文本
      - entities: 实体清单
      - minor_data_detected: 是否含未成年人迹象
    """
    if not settings.pii_redact_enabled:
        return text, [], False

    redacted = text
    entities = []
    counter = {k: 0 for k in PATTERNS}

    for pii_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            counter[pii_type] += 1
            entities.append({
                "type": pii_type,
                "original": match.group(),
                "placeholder": f"[{pii_type}_{counter[pii_type]}]",
                "position": match.span(),
            })

    for e in sorted(entities, key=lambda x: -x["position"][0]):
        s, t = e["position"]
        redacted = redacted[:s] + e["placeholder"] + redacted[t:]

    # 检测未成年迹象
    minor_detected = any(ind in text for ind in MINOR_INDICATORS) \
                     or any(e["type"] in ("STUDENT_ID", "CLASS", "SCHOOL") for e in entities)

    return redacted, entities, minor_detected


if __name__ == "__main__":
    sample = """
    三年级二班学生张三, 学号 20210301001, 家长王芳(手机 13800138000),
    住在北京市朝阳区幸福路 8 号 3 单元 101 室。在示例小学就读。
    """
    r, e, minor = redact(sample)
    print("脱敏:", r)
    print(f"\n未成年数据:{minor}")
    print(f"实体数量:{len(e)}")
    for x in e:
        print(f"  {x['type']}: {x['original']} → {x['placeholder']}")
