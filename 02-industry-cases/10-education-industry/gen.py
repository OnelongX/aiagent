# -*- coding: utf-8 -*-
"""5 images for 教育行业 AI 落地 · 行业落地 #10"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\教育行业Agent"
W, H = 1080, 600

# 教育主题 · 翠绿 / 温暖
BG = "#0d2818"           # 深墨绿 (温和有底蕴)
BOX = "#1a3a2a"
DEEP = "#08160e"
LINE = "#2d4d3d"
WHITE = "#ffffff"
SUB = "#c8e0d5"
LIGHT = "#8eb5a0"
DIM = "#5f7d6e"
EMERALD = "#10b981"
EMERALD_LIGHT = "#34d399"
LIME = "#84cc16"
LIME_LIGHT = "#a3e635"
AMBER = "#fbbf24"
AMBER_LIGHT = "#fde047"
SKY = "#0ea5e9"
SKY_LIGHT = "#38bdf8"
RED = "#ef4444"
RED_LIGHT = "#fca5a5"
PINK = "#ec4899"
PURPLE = "#a855f7"

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

    rrect(d, [60, 50, 240, 88], 19, fill=EMERALD)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地 #10", font=font(17, bold=True), fill=EMERALD_LIGHT)

    d.text((60, 128), "教育行业 AI 落地", font=font(42, bold=True), fill=AMBER_LIGHT)
    d.text((60, 188), "学情 / 批改 / 家校", font=font(26, bold=True), fill=WHITE)
    d.text((60, 222), "辅导 4 大场景", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("温和评价",       LIME_LIGHT,    "不贴标签"),
        ("未成年保护",     SKY_LIGHT,     "PII 双重"),
        ("不替代教师",     AMBER_LIGHT,   "教师签字"),
    ]
    y = 296
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 514], 14, fill=DEEP, outline=EMERALD, width=2)
    d.text((80, 448), "教育行业的 AI · 关键不是会教 · 是懂得克制", font=font(20, bold=True), fill=EMERALD_LIGHT)
    d.text((80, 482), "最终评价权在老师 · 关心权在家长 · 工具消化重复劳动", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 4 大场景 ============
def img_02():
    img, d = base()
    d.text((60, 40), "4 大场景闭环", font=font(26, bold=True), fill=AMBER_LIGHT)
    d.text((60, 78), "批改→学情→推荐→反哺 · 同步家校", font=font(15), fill=LIGHT)

    scenarios = [
        ("📝", "作业批改",     "客观题自动 + 主观题二审",      "教师核心",   SKY),
        ("📊", "学情分析",     "错题归类 + 知识点掌握",         "教师/家长",  EMERALD),
        ("📨", "家校沟通",     "周报草稿 + 答疑分流 + 焦虑监控", "敏感场景",   AMBER),
        ("🎯", "个性化辅导",   "知识点 + 难度梯度 + 减负",     "学生主用",   PURPLE),
    ]
    y0 = 124
    for i, (icon, name, desc, target, c) in enumerate(scenarios):
        y = y0 + i * 80
        rrect(d, [60, y, 1020, y + 70], 12, fill=BOX, outline=c, width=2)
        d.text((78, y + 16), icon, font=font(32), fill=c)
        d.text((148, y + 12), name, font=font(22, bold=True), fill=c)
        d.text((148, y + 44), desc, font=font(14), fill=SUB)
        bw = tw(d, target, font(12, bold=True)) + 16
        rrect(d, [1020 - bw - 14, y + 22, 1020 - 14, y + 44], 10, fill=DEEP)
        d.text((1020 - bw - 8, y + 24), target, font=font(12, bold=True), fill=c)

    watermark(d)
    img.save(os.path.join(OUT, "02_scope.png"))
    print("[OK] 02_scope")


# ============ 03: 7 个独特挑战 ============
def img_03():
    img, d = base()
    d.text((60, 40), "教育行业 AI · 7 个独特挑战", font=font(26, bold=True), fill=AMBER_LIGHT)
    d.text((60, 78), "其他行业没有的硬约束", font=font(15), fill=LIGHT)

    challenges = [
        ("未成年人 PII",      "★★★★★", "姓名/学校/家长 比成人 PII 更敏感",   RED),
        ("教育公平",          "★★★★★", "不能强化差生标签 / 不能过度比较",   RED),
        ("不制造家长焦虑",     "★★★★★", "周报错一句话 · 家长群炸锅",          PINK),
        ("批改可解释",        "★★★★",  "错在哪 / 为什么 / 怎么改",            AMBER),
        ("不替代教师评价",    "★★★★",  "主观题最终打分必须老师二审",          AMBER),
        ("课标 / 学段差异",   "★★★",   "小学 vs 初中 vs 高中 标准不同",       SKY),
        ("融入教师工作流",     "★★★",   "不破坏老师原本流程才会被用",          EMERALD),
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


# ============ 04: 7 条工程纪律 ============
def img_04():
    img, d = base()
    d.text((60, 40), "7 条教育行业工程纪律", font=font(26, bold=True), fill=AMBER_LIGHT)
    d.text((60, 78), "全场景共通 · 跟未成年保护 / 双减 / 教育部规范对齐", font=font(15), fill=LIGHT)

    rules = [
        ("1", "未成年人 PII 严格脱敏",  "姓名/学号/班级/学校/家长全脱敏", RED),
        ("2", "标签温和",              "待提升 ≠ 差生 · 关键词替换",     PINK),
        ("3", "不公开个人评价",        "班级周报无个人 · 私聊家长",       AMBER),
        ("4", "主观题教师二审",        "作文/解答 LLM 初评 → 老师终评",   SKY),
        ("5", "焦虑监控",              "检测焦虑信号 → 引导不强化",       EMERALD),
        ("6", "情绪敏感话题人审",      "亲情/死亡/伤害 → 标 [需教师阅读]", PURPLE),
        ("7", "不推付费课程",          "建议报班 / 推荐补课 → 禁词",      LIME),
    ]
    y0 = 110
    for i, (n, name, desc, c) in enumerate(rules):
        y = y0 + i * 54
        rrect(d, [60, y, 1020, y + 46], 10, fill=BOX, outline=c, width=2)
        d.ellipse([76, y + 8, 110, y + 38], fill=c)
        d.text((85, y + 11), n, font=font(15, bold=True), fill=BG)
        d.text((130, y + 6), name, font=font(15, bold=True), fill=c)
        d.text((130, y + 26), desc, font=font(12), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_rules.png"))
    print("[OK] 04_rules")


# ============ 05: 学情→批改→家校 闭环 ============
def img_05():
    img, d = base()
    d.text((60, 40), "4 场景闭环工作流", font=font(26, bold=True), fill=AMBER_LIGHT)
    d.text((60, 78), "数据从批改流出 · 反哺学情 · 推动家校 · 形成增强回路", font=font(15), fill=LIGHT)

    # 中心:学情数据库
    center_x, center_y = W // 2, 290
    rrect(d, [center_x - 90, center_y - 50, center_x + 90, center_y + 50], 14, fill=BOX, outline=AMBER, width=2)
    d.text((center_x - 70, center_y - 35), "📊", font=font(28), fill=AMBER)
    d.text((center_x - 55, center_y - 2), "学情数据库", font=font(15, bold=True), fill=AMBER_LIGHT)
    d.text((center_x - 50, center_y + 22), "知识点 + 掌握度", font=font(11), fill=SUB)

    # 4 个场景(上左/上右/下左/下右)
    nodes = [
        ("📝 作业批改",      "全班数据流入",  SKY,        130, 130),
        ("📨 家校沟通",      "周报 + 答疑",   AMBER,      W - 280, 130),
        ("🎯 个性化辅导",    "推荐题目",      PURPLE,     W - 280, 420),
        ("📊 学情分析",      "薄弱 TOP 5",    EMERALD,    130, 420),
    ]
    for name, desc, c, x, y in nodes:
        rrect(d, [x, y, x + 160, y + 80], 12, fill=BOX, outline=c, width=2)
        d.text((x + 14, y + 12), name, font=font(15, bold=True), fill=c)
        d.text((x + 14, y + 42), desc, font=font(12), fill=SUB)

        # arrows to center(简化箭头)
        if y < center_y:
            d.line([(x + 80, y + 80), (center_x, center_y - 50)], fill=LINE, width=2)
        else:
            d.line([(x + 80, y), (center_x, center_y + 50)], fill=LINE, width=2)

    # 顶部说明
    rrect(d, [60, 90, 1020, 116], 6, fill=DEEP, outline=EMERALD, width=1)
    d.text((80, 96), "数据流向:批改 → 学情 → 推荐(+反哺学情)+ 周报(同步家长)", font=font(13, bold=True), fill=EMERALD_LIGHT)

    # 底部核心
    rrect(d, [60, 520, 1020, 562], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 532), "数据闭环:批改产生学情 · 学情驱动推荐 · 推荐反哺学情 · 家校同步进度", font=font(13, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_workflow.png"))
    print("[OK] 05_workflow")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
