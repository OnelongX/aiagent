# -*- coding: utf-8 -*-
"""5 images for 医疗行业 AI 落地 · 行业落地 #11"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# 医疗主题 · 蓝白 + 微红(急救)
BG       = "#0a1929"
BOX      = "#102a43"
DEEP     = "#061322"
LINE     = "#1e3a5f"
WHITE    = "#ffffff"
SUB      = "#cfe2f3"
LIGHT    = "#8aa9c9"
DIM      = "#5e7791"
SKY      = "#0ea5e9"
SKY_L    = "#38bdf8"
SAFE     = "#10b981"
SAFE_L   = "#34d399"
WARN     = "#fbbf24"
WARN_L   = "#fde047"
DANGER   = "#ef4444"
DANGER_L = "#fca5a5"
PURPLE   = "#a855f7"
PINK     = "#ec4899"

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
    rrect(d, [60, 50, 240, 88], 19, fill=SKY)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地 #11", font=font(17, bold=True), fill=SKY_L)

    d.text((60, 128), "医疗行业 AI 落地", font=font(42, bold=True), fill=WARN_L)
    d.text((60, 188), "影像 / 分诊 / 用药 ·", font=font(26, bold=True), fill=WHITE)
    d.text((60, 222), "6 大场景 + 1 熔断", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("不诊断",      SKY_L,    "AI 给建议复核"),
        ("不开方",      SAFE_L,   "医师签字担责"),
        ("急救熔断",    DANGER_L, "不进 LLM · 推 120"),
    ]
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, 296, x + 310, 388], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, 310), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, 348), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 514], 14, fill=DEEP, outline=SKY, width=2)
    d.text((80, 448), "医疗行业 AI · 关键不在会写,在懂得不说什么", font=font(20, bold=True), fill=SKY_L)
    d.text((80, 482), "签字权在医师 · 处方权在医师 · AI 消化重复性文书 + 提示性辅助", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 SCOPE 6 场景 ============
def img_02():
    img, d = base()
    d.text((60, 40), "6 大场景闭环", font=font(26, bold=True), fill=WARN_L)
    d.text((60, 78), "影像→分诊→检查→诊断→用药→随访 · 每环都有签字栏", font=font(15), fill=LIGHT)

    scenarios = [
        ("📷", "影像辅助",   "AI 给建议复核 · 不出诊断",       "放射科",  SKY),
        ("🚑", "智能分诊",   "ESI 5 级 · 红色直推 120",        "急诊",    DANGER),
        ("💊", "用药审查",   "相互作用 + 剂量 + 特殊人群",     "药师",    SAFE),
        ("📋", "出院小结",   "AI 起草 + 主治签字担责",         "病案室",  WARN),
        ("🧠", "CDSS 提示",  "诊断思路 + 鉴别 + 危险信号",     "全科",    PURPLE),
        ("💬", "患者科普",   "不诊断 · 首诊转线下",            "互联网医院", PINK),
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


# ============ 03 8 独特挑战 ============
def img_03():
    img, d = base()
    d.text((60, 40), "医疗行业 AI · 8 个独特挑战", font=font(26, bold=True), fill=WARN_L)
    d.text((60, 78), "其他行业没有的硬约束 · 触红线 = 医疗事故 / 行政处罚", font=font(15), fill=LIGHT)

    challenges = [
        ("AI 不能下诊断",     "★★★★★", "执业医师法 · 必须医师签字",              DANGER),
        ("AI 不能开处方",     "★★★★★", "处方管理办法 · 必须执业医师签",          DANGER),
        ("急救不能等",        "★★★★★", "胸痛/出血/中毒 → 不进 LLM",              PINK),
        ("药品相互作用",      "★★★★★", "禁配伍 / 增减剂量 · 接真实药典",          DANGER),
        ("特殊人群",          "★★★★",  "孕 / 哺乳 / 儿 / 老 · 妊娠分级",          WARN),
        ("PII 极敏感",        "★★★★★", "住院号 / 病历号 / 医保号 · 加 4 类",      WARN),
        ("商品名禁出现",      "★★★★",  "AI 输出只用通用名 · 不带货",              SKY),
        ("互联网医院只复诊",   "★★★★",  "首诊违法 · AI 必须识别并转线下",          PURPLE),
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


# ============ 04 7 条工程纪律 ============
def img_04():
    img, d = base()
    d.text((60, 40), "7 条医疗工程纪律", font=font(26, bold=True), fill=WARN_L)
    d.text((60, 78), "全场景共通 · 跟医师法 / 处方管理 / 互联网诊疗规则对齐", font=font(15), fill=LIGHT)

    rules = [
        ("1", "急救熔断",         "关键词命中 → 不进 LLM · 直推 120",       DANGER),
        ("2", "医师签字栏",       "出院 / CDSS / 文书顶部强制签字",         PINK),
        ("3", "影像 100% 二审",   "AI 出建议复核 · 标 confidence",          SKY),
        ("4", "用药对真实库",     "查 INN 通用名 · 不查商品名",             SAFE),
        ("5", "PII 双重脱敏",     "进 LLM 前 + 进向量库前 · 10 类正则",     WARN),
        ("6", "首诊转线下",       "识别首诊词 → 互联网医院拒绝接单",         PURPLE),
        ("7", "建议性语言软化",   "11 个禁词 → 科普性表达",                 SKY_L),
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


# ============ 05 数据流 ============
def img_05():
    img, d = base()
    d.text((60, 40), "数据流:患者 → AI 辅助 → 医师签字 → 病历", font=font(24, bold=True), fill=WARN_L)
    d.text((60, 76), "全链 6 个签字栏 · 任一环节 AI 失效 · 医师可独立完成", font=font(14), fill=LIGHT)

    # 5 个节点 + 4 个箭头
    nodes = [
        ("📨\n患者主诉",      90,  170, SKY,    "急救熔断"),
        ("🤖\nAI 辅助",       290, 170, PURPLE, "脱敏 + 红线"),
        ("👨‍⚕️\n医师阅读",     490, 170, SAFE,   "100% 复核"),
        ("✍️\n医师签字",      690, 170, WARN,   "担责"),
        ("📋\n归档病历",      890, 170, PINK,   "可追溯"),
    ]
    for icon_name, x, y, c, note in nodes:
        rrect(d, [x, y, x + 140, y + 130], 14, fill=BOX, outline=c, width=2)
        lines = icon_name.split("\n")
        d.text((x + 50, y + 14), lines[0], font=font(28), fill=c)
        d.text((x + 20, y + 60), lines[1], font=font(15, bold=True), fill=c)
        d.text((x + 18, y + 92), note, font=font(11), fill=SUB)

    # 箭头
    for i in range(4):
        x1 = 90 + i * 200 + 140
        x2 = 90 + (i + 1) * 200
        d.line([(x1, 235), (x2 - 4, 235)], fill=LINE, width=3)
        d.polygon([(x2, 235), (x2 - 10, 230), (x2 - 10, 240)], fill=LINE)

    # 底部熔断带
    rrect(d, [60, 380, 1020, 450], 12, fill=DEEP, outline=DANGER, width=2)
    d.text((80, 396), "🚨 急救熔断旁路:任何节点检测到急救关键词 → 跳过 AI · 直接推 120",
           font=font(15, bold=True), fill=DANGER_L)
    d.text((80, 422), "(胸痛 / 大出血 / 意识丧失 / 中毒 / 自杀危机 / 临产)",
           font=font(13), fill=LIGHT)

    # 顶部说明
    rrect(d, [60, 488, 1020, 540], 10, fill=DEEP, outline=SKY, width=1)
    d.text((80, 500), "核心:AI 是流水线的 1 个工位 · 不是审判官 · 拔掉 AI 医师照样走完流程",
           font=font(14, bold=True), fill=SKY_L)
    d.text((80, 520), "这是医疗 AI 的唯一可上线姿势 · 否则 = 非法行医",
           font=font(12), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_flow.png"))
    print("[OK] 05_flow")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
