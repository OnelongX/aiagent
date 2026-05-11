# -*- coding: utf-8 -*-
"""5 images for 金融行业 AI 落地 · 行业落地 #12"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# 金融主题 · 深蓝 + 金色
BG       = "#0c1729"
BOX      = "#1a2a44"
DEEP     = "#060f1c"
LINE     = "#2a3d5d"
WHITE    = "#ffffff"
SUB      = "#cfdcef"
LIGHT    = "#94a8c4"
DIM      = "#5e7595"
GOLD     = "#fbbf24"
GOLD_L   = "#fde047"
INFO     = "#38bdf8"
INFO_L   = "#7dd3fc"
SAFE     = "#10b981"
SAFE_L   = "#34d399"
WARN     = "#f97316"
WARN_L   = "#fdba74"
DANGER   = "#ef4444"
DANGER_L = "#fca5a5"
PURPLE   = "#a855f7"

REG  = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def tw(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[2] - b[0]


def rrect(d, xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def base():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def watermark(d):
    d.text((W - 180, H - 32), "实战复盘", font=font(14), fill=DIM)


# ============ 01 HERO ============
def img_01():
    img, d = base()
    rrect(d, [60, 50, 240, 88], 19, fill=GOLD)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地 #12", font=font(17, bold=True), fill=GOLD_L)

    d.text((60, 128), "金融行业 AI 落地", font=font(42, bold=True), fill=GOLD_L)
    d.text((60, 188), "KYC / 风控 / 投顾 ·", font=font(26, bold=True), fill=WHITE)
    d.text((60, 222), "6 大场景 + 反诈熔断", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("不荐股",         GOLD_L,    "AI 投教 · 非投顾"),
        ("不授信",         INFO_L,    "辅助评分 · 信贷员决"),
        ("反诈熔断",       DANGER_L,  "不进 LLM · 报警"),
    ]
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, 296, x + 310, 388], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, 310), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, 348), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 514], 14, fill=DEEP, outline=GOLD, width=2)
    d.text((80, 448), "金融行业 AI · 监管比业务严 · 输错一句话 = 行政处罚", font=font(20, bold=True), fill=GOLD_L)
    d.text((80, 482), "AI 是合规辅助 · 决策权永远在持牌机构 / 合规专员手里", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 SCOPE ============
def img_02():
    img, d = base()
    d.text((60, 40), "6 大场景闭环", font=font(26, bold=True), fill=GOLD_L)
    d.text((60, 78), "进件 → 反洗钱 → 风控 → 投教 → 适当性 → 留存", font=font(15), fill=LIGHT)

    scenarios = [
        ("🪪", "KYC 智能审核",     "辅助清单 · 不替代真人",         "合规专员",  INFO),
        ("🛡️", "AML 反洗钱",      "规则评分 · ≥70 强制上报",        "反洗钱",    DANGER),
        ("💳", "信贷风控",         "评分 + 反欺诈 + 反歧视审计",     "信贷员",    GOLD),
        ("📊", "投资陪伴",         "投教 · 不荐股 · 反诈拦截",       "投顾",      WARN),
        ("⚖️", "适当性匹配",      "C1-C5 × R1-R5 · 不匹配阻断",     "客户经理",  SAFE),
        ("👥", "客户分析",         "画像 + 流失 · 给 RM 用",         "私行/零售", PURPLE),
    ]
    y0 = 110
    for i, (icon, name, desc, target, c) in enumerate(scenarios):
        y = y0 + i * 72
        rrect(d, [60, y, 1020, y + 62], 12, fill=BOX, outline=c, width=2)
        d.text((78, y + 14), icon, font=font(28), fill=c)
        d.text((140, y + 10), name, font=font(20, bold=True), fill=c)
        d.text((140, y + 38), desc, font=font(13), fill=SUB)
        bw = tw(d, target, font(12, bold=True)) + 16
        rrect(d, [1020 - bw - 14, y + 20, 1020 - 14, y + 42], 10, fill=DEEP)
        d.text((1020 - bw - 8, y + 22), target, font=font(12, bold=True), fill=c)
    watermark(d)
    img.save(os.path.join(OUT, "02_scope.png"))
    print("[OK] 02_scope")


# ============ 03 CHALLENGES ============
def img_03():
    img, d = base()
    d.text((60, 40), "金融行业 AI · 8 个独特挑战", font=font(26, bold=True), fill=GOLD_L)
    d.text((60, 78), "其他行业没有的硬约束 · 触红线 = 行政处罚 / 牌照风险", font=font(15), fill=LIGHT)

    challenges = [
        ("AI 不能荐股",        "★★★★★", "证监会硬红线 · 必须无具体标的",          DANGER),
        ("AI 不能授信",        "★★★★★", "持牌机构才能放贷 · AI 只能辅助",          DANGER),
        ("反诈关键词",         "★★★★★", "稳赚/保本/内幕 → 不进 LLM",              WARN),
        ("反洗钱时限",         "★★★★★", "可疑交易 5 天内报 · AI 评分不能等",       WARN),
        ("个人金融信息 C3 级", "★★★★★", "JR/T 0171 标准 · 比通用 PII 严",          GOLD),
        ("算法反歧视",         "★★★★",  "年龄/性别/民族/地域不能成拒绝理由",        INFO),
        ("适当性匹配",         "★★★★",  "C1-C5 × R1-R5 · 不能错配",                SAFE),
        ("互联网借贷规范",     "★★★★",  "穿透式监管 · 不能联合放贷绕开",            PURPLE),
    ]
    y0 = 110
    for i, (name, stars, desc, c) in enumerate(challenges):
        y = y0 + i * 54
        rrect(d, [60, y, 1020, y + 46], 10, fill=BOX, outline=c, width=2)
        d.rectangle([60, y, 64, y + 46], fill=c)
        d.text((80, y + 6), name, font=font(15, bold=True), fill=WHITE)
        d.text((80, y + 26), desc, font=font(12), fill=SUB)
        d.text((1020 - 100, y + 14), stars, font=font(13, bold=True), fill=c)
    watermark(d)
    img.save(os.path.join(OUT, "03_challenges.png"))
    print("[OK] 03_challenges")


# ============ 04 RULES ============
def img_04():
    img, d = base()
    d.text((60, 40), "7 条金融工程纪律", font=font(26, bold=True), fill=GOLD_L)
    d.text((60, 78), "全场景共通 · 跟证监会 / 银保监 / 央行 / 反洗钱规范对齐", font=font(15), fill=LIGHT)

    rules = [
        ("1", "反诈熔断",        "命中关键词 → 不进 LLM · 推 110",            DANGER),
        ("2", "合规签字栏",      "KYC / 信贷 / 投教 强制注入",                WARN),
        ("3", "投教非投顾",      "16 个荐股禁词 → 软化",                       GOLD),
        ("4", "适当性硬匹配",    "C1-C5 × R1-R5 · 不匹配阻断",                SAFE),
        ("5", "PII 11 类双重",   "C3 级敏感 · 加银行卡/CVV/账号/客户号",       INFO),
        ("6", "反歧视审计",      "地域/性别/民族剔除",                         PURPLE),
        ("7", "AML 强制上报",    "评分≥70 → STR · 不告知客户",                 INFO_L),
    ]
    y0 = 110
    for i, (n, name, desc, c) in enumerate(rules):
        y = y0 + i * 64
        rrect(d, [60, y, 1020, y + 54], 10, fill=BOX, outline=c, width=2)
        d.ellipse([76, y + 10, 114, y + 46], fill=c)
        d.text((87, y + 14), n, font=font(17, bold=True), fill=BG)
        d.text((132, y + 8), name, font=font(17, bold=True), fill=c)
        d.text((132, y + 32), desc, font=font(13), fill=SUB)
    watermark(d)
    img.save(os.path.join(OUT, "04_rules.png"))
    print("[OK] 04_rules")


# ============ 05 SUITABILITY MATRIX ============
def img_05():
    img, d = base()
    d.text((60, 40), "适当性匹配矩阵 C × R", font=font(24, bold=True), fill=GOLD_L)
    d.text((60, 76), "客户风险等级 (C1-C5) × 产品风险等级 (R1-R5) · 不匹配阻断", font=font(14), fill=LIGHT)

    # 矩阵
    cell_w = 130
    cell_h = 52
    x0 = 240
    y0 = 130

    # header
    d.text((85, y0 + 16), "客户 \\ 产品", font=font(14, bold=True), fill=SUB)
    for j, r in enumerate(["R1\n货基", "R2\n债券", "R3\n平衡", "R4\n股基", "R5\n衍生"]):
        x = x0 + j * cell_w
        rrect(d, [x, y0, x + cell_w - 6, y0 + cell_h], 8, fill=BOX, outline=LINE, width=1)
        for li, line in enumerate(r.split("\n")):
            d.text((x + 20, y0 + 6 + li * 18), line, font=font(13, bold=True), fill=GOLD_L)

    # rows
    custs = ["C1 保守", "C2 稳健", "C3 平衡", "C4 积极", "C5 激进"]
    # 矩阵规则(✓ 可购买 · ✗ 阻断)
    matrix = [
        [1,0,0,0,0],
        [1,1,0,0,0],
        [1,1,1,0,0],
        [1,1,1,1,0],
        [1,1,1,1,1],
    ]
    for i, name in enumerate(custs):
        y = y0 + (i + 1) * cell_h + 6
        rrect(d, [60, y, 230, y + cell_h - 6], 8, fill=BOX, outline=LINE, width=1)
        d.text((78, y + 14), name, font=font(13, bold=True), fill=SUB)
        for j in range(5):
            x = x0 + j * cell_w
            ok = matrix[i][j]
            color = SAFE if ok else DANGER
            sym = "✓" if ok else "✗"
            rrect(d, [x, y, x + cell_w - 6, y + cell_h - 6], 8, fill=DEEP, outline=color, width=2)
            d.text((x + cell_w // 2 - 14, y + 8), sym, font=font(22, bold=True), fill=color)

    rrect(d, [60, 540, 1020, 580], 8, fill=DEEP, outline=GOLD, width=1)
    d.text((80, 552), "对角线下方均可买 · 上方阻断 · 客户坚持购买需签《风险揭示书》+ 合规审批",
           font=font(12, bold=True), fill=GOLD_L)

    watermark(d)
    img.save(os.path.join(OUT, "05_matrix.png"))
    print("[OK] 05_matrix")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
