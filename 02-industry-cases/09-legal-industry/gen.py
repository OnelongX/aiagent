# -*- coding: utf-8 -*-
"""5 images for 法律行业 AI 落地 · 行业落地 #9"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\法律行业Agent"
W, H = 1080, 600

BG = "#1a1a2e"
BOX = "#252544"
DEEP = "#0f0f1f"
LINE = "#3f3f5f"
WHITE = "#ffffff"
SUB = "#c8c8d8"
LIGHT = "#8888a8"
DIM = "#5a5a78"
AMBER = "#d4af37"        # 法律金 · 庄重
AMBER_LIGHT = "#f4d56b"
RED = "#c0392b"
RED_LIGHT = "#e74c3c"
GREEN = "#27ae60"
GREEN_LIGHT = "#2ecc71"
BLUE = "#2980b9"
BLUE_LIGHT = "#3498db"
PURPLE = "#8e44ad"
PURPLE_LIGHT = "#9b59b6"
NAVY = "#1e3a5f"
STEEL = "#34495e"

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def mono(size):
    try:
        return ImageFont.truetype(MONO, size)
    except Exception:
        return font(size)


def tw(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[2] - b[0]


def rrect(d, xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def base():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    return img, d


def watermark(d):
    d.text((W - 180, H - 32), "实战复盘", font=font(14), fill=DIM)


# ============ 01: HERO ============
def img_01():
    img, d = base()

    rrect(d, [60, 50, 240, 88], 19, fill=AMBER)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地 #9", font=font(17, bold=True), fill=AMBER_LIGHT)

    d.text((60, 128), "法律行业 AI 落地", font=font(42, bold=True), fill=AMBER)
    d.text((60, 188), "合同 / 类案 / 文书", font=font(26, bold=True), fill=WHITE)
    d.text((60, 222), "咨询 / 法规 5 大场景", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("AI 不是律师",   RED_LIGHT,      "辅助 · 不替代"),
        ("法条不能编",     AMBER_LIGHT,    "必接真实数据库"),
        ("律师签字担责",   GREEN_LIGHT,    "人在环"),
    ]
    y = 296
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(20, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 514], 14, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 448), "AI 能做的事 · 不等于律师能做的事", font=font(20, bold=True), fill=AMBER_LIGHT)
    d.text((80, 482), "执业责任不可转移 · 这是法律行业 AI 的硬边界", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 5 大场景全景 ============
def img_02():
    img, d = base()
    d.text((60, 40), "5 大场景全景图", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "覆盖律师 / 法务 / 合规 / 自由律师的核心工作流", font=font(15), fill=LIGHT)

    scenarios = [
        ("📋", "合同审查",  "条款提取 + 红线 + 修订",     "律师 / 法务",  BLUE),
        ("⚖️", "类案检索",  "事实匹配 + 审级权威 + 跨地区",  "诉讼律师",     PURPLE),
        ("📝", "文书起草",  "6 种模板 + 真实法条 + 签字栏",   "全场景",        AMBER),
        ("💬", "法律咨询",  "普法 + 免责 + 应急拦截",        "To C / 律师助理", GREEN),
        ("📰", "法规追踪",  "多源订阅 + 影响分析 + 客户预警", "律所 / 大企业",  RED_LIGHT),
    ]
    y0 = 124
    for i, (icon, name, desc, target, c) in enumerate(scenarios):
        y = y0 + i * 70
        rrect(d, [60, y, 1020, y + 60], 12, fill=BOX, outline=c, width=2)
        # icon
        d.text((78, y + 12), icon, font=font(28), fill=c)
        # name
        d.text((138, y + 10), name, font=font(20, bold=True), fill=c)
        # desc
        d.text((138, y + 38), desc, font=font(14), fill=SUB)
        # target
        bw = tw(d, target, font(12, bold=True)) + 16
        rrect(d, [1020 - bw - 14, y + 18, 1020 - 14, y + 38], 10, fill=DEEP)
        d.text((1020 - bw - 8, y + 20), target, font=font(12, bold=True), fill=c)

    watermark(d)
    img.save(os.path.join(OUT, "02_scope.png"))
    print("[OK] 02_scope")


# ============ 03: 6 大独特挑战 ============
def img_03():
    img, d = base()
    d.text((60, 40), "法律行业 AI 落地 · 6 个独特挑战", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "其他行业没有的硬约束 · 工程纪律比技术更重要", font=font(15), fill=LIGHT)

    challenges = [
        ("法条不能编",        "★★★★★", "LLM 编出来 = 客户拿去打官司是事故",  RED),
        ("判例不能编",        "★★★★★", "案号 / 审级 / 主文必须可查",         RED),
        ("不能直接给建议",    "★★★★",  "给了 = 无证律师执业 · 法律风险",      AMBER),
        ("PII 双重保护",      "★★★★",  "客户机密 + 当事人 PII (GDPR+PIPL)",  PURPLE),
        ("法律语言极精确",    "★★★",   "可以/应当 差别决定胜负",              BLUE),
        ("律师责任不可转",    "★★★★★", "出事必须有律师人审最后一道关",        RED),
    ]
    y0 = 116
    for i, (name, stars, desc, c) in enumerate(challenges):
        y = y0 + i * 64
        rrect(d, [60, y, 1020, y + 56], 12, fill=BOX, outline=c, width=2)
        d.rectangle([60, y, 64, y + 56], fill=c)
        d.text((80, y + 10), name, font=font(17, bold=True), fill=WHITE)
        d.text((80, y + 34), desc, font=font(13), fill=SUB)
        # 难度星
        d.text((1020 - 100, y + 18), stars, font=font(15, bold=True), fill=c)

    watermark(d)
    img.save(os.path.join(OUT, "03_challenges.png"))
    print("[OK] 03_challenges")


# ============ 04: 工程纪律 6 条 ============
def img_04():
    img, d = base()
    d.text((60, 40), "跨场景的 6 条工程纪律", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "所有 5 大场景共通 · 律师不签字 · AI 输出无效", font=font(15), fill=LIGHT)

    rules = [
        ("1", "法条 / 判例必须真实可查", "接国家法律法规数据库 + 北大法宝", RED),
        ("2", "律师签字栏(强制)", "顶部含律师证号 + 日期 + 事务所", AMBER),
        ("3", "免责声明(强制)", "末尾必有「不构成法律建议」", BLUE),
        ("4", "应急情况优先级最高", "暴力/自杀立即推 110 / 12348", RED_LIGHT),
        ("5", "PII 双重脱敏", "进 LLM 前 + 进向量库前", PURPLE),
        ("6", "律师在环 (HITL)", "对外输出必须执业律师签字", GREEN),
    ]
    y0 = 116
    for i, (n, name, desc, c) in enumerate(rules):
        y = y0 + i * 64
        rrect(d, [60, y, 1020, y + 56], 12, fill=BOX, outline=c, width=2)
        # number circle
        d.ellipse([76, y + 12, 120, y + 50], fill=c)
        d.text((90, y + 16), n, font=font(20, bold=True), fill=BG)
        # name + desc
        d.text((140, y + 8), name, font=font(17, bold=True), fill=c)
        d.text((140, y + 34), desc, font=font(13), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_rules.png"))
    print("[OK] 04_rules")


# ============ 05: 3 种部署形态对照 ============
def img_05():
    img, d = base()
    d.text((60, 40), "3 种部署形态对照", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "律所内用 / 企业法务 / To C 律师助手 · 边界严苛度不同", font=font(15), fill=LIGHT)

    forms = [
        ("A 律所内部",       "律师 + 实习生",     "高 · 律师执业责任",     "私有部署 · 不上公有云", "全栈 5-10 人月", BLUE, 60),
        ("B 企业法务",       "法务 + 合规 + 业务", "中 · 合规风险",          "私有 / 混合",            "中型 3-5 人月",  GREEN, 388),
        ("C To C 律师助手", "普通用户",          "最高 · 不能给建议",      "公有云 + 强合规",        "中型 + 重合规审", RED, 716),
    ]
    y0 = 118
    bw = 314
    for name, user, redline, deploy, invest, c, x in forms:
        rrect(d, [x, y0, x + bw, y0 + 360], 14, fill=BOX, outline=c, width=2)
        rrect(d, [x, y0, x + bw, y0 + 50], 14, fill=c)
        d.text((x + 16, y0 + 14), name, font=font(20, bold=True), fill=BG)

        y = y0 + 70
        for label, value in [("用户", user), ("红线", redline), ("部署", deploy), ("投入", invest)]:
            d.text((x + 16, y), label, font=font(11), fill=DIM)
            d.text((x + 16, y + 18), value, font=font(13, bold=True), fill=WHITE)
            y += 48

    rrect(d, [60, 502, 1020, 514], 4, fill=RED)
    d.text((400, 488), "形态 C 监管 + 责任 + 体验 三重难", font=font(13, bold=True), fill=RED_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_deployment.png"))
    print("[OK] 05_deployment")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
