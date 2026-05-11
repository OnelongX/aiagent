# -*- coding: utf-8 -*-
"""5 images for 学生论文助手 · 行业落地 #8"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\学生论文助手"
W, H = 1080, 600

BG = "#0f172a"
BOX = "#1e293b"
DEEP = "#0b1220"
LINE = "#334155"
WHITE = "#ffffff"
SUB = "#cbd5e1"
LIGHT = "#94a3b8"
DIM = "#64748b"
AMBER = "#fbbf24"
AMBER_LIGHT = "#fde047"
RED = "#ef4444"
RED_LIGHT = "#fca5a5"
GREEN = "#22c55e"
GREEN_LIGHT = "#4ade80"
PURPLE = "#a855f7"
BLUE = "#3b82f6"
BLUE_LIGHT = "#60a5fa"
NAVY = "#1e3a8a"
NAVY_LIGHT = "#3b82f6"
STEEL = "#475569"
STEEL_LIGHT = "#94a3b8"
CYAN = "#06b6d4"
CYAN_LIGHT = "#22d3ee"
TEAL = "#14b8a6"
ORANGE = "#fb923c"
PINK = "#ec4899"
INDIGO = "#6366f1"
ROSE = "#f43f5e"

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

    rrect(d, [60, 50, 240, 88], 19, fill=NAVY_LIGHT)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地 #8", font=font(17, bold=True), fill=AMBER_LIGHT)

    d.text((60, 128), "学生论文助手", font=font(46, bold=True), fill=AMBER)
    d.text((60, 188), "写作 / 润色 / 查重 / 答辩", font=font(26, bold=True), fill=WHITE)
    d.text((60, 224), "的 AI 工程方案", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("AI 是助理",     GREEN_LIGHT,  "不是代笔"),
        ("引用必校验",     CYAN,         "DOI 真实性"),
        ("披露 AI 协助",   AMBER,        "学术诚信"),
    ]
    y = 296
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 514], 14, fill=DEEP, outline=NAVY_LIGHT, width=2)
    d.text((80, 448), "AI 能做的事 · 不等于 AI 应该做的事", font=font(20, bold=True), fill=NAVY_LIGHT)
    d.text((80, 482), "好工具只是放大原本的能力", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: AI 辅助 vs 代笔 边界 ============
def img_02():
    img, d = base()
    d.text((60, 40), "AI 辅助 vs AI 代笔", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "学术诚信红线 · 这是这一篇跟前 7 篇的本质区别", font=font(15), fill=LIGHT)

    rows = [
        ("选题",          "推荐方向",       "替代决定",        "推荐 · 用户挑"),
        ("大纲",          "生成多版本",     "AI 决定结构",     "AI 出多版本 · 用户选"),
        ("文献检索",      "真实 API",       "AI 编文献",       "DOI 校验 · 必须真实"),
        ("章节起草",      "提供框架",       "AI 写整章",       "占位 + 用户填实质"),
        ("润色",          "改语言",         "改观点",          "diff 输出 · 用户审"),
        ("引用格式",      "GB7714 / APA",   "自动加引用",      "格式化 · 不编内容"),
        ("查重",          "本地相似度",     "伪装原创",        "提示加引用 · 不包装"),
        ("答辩",          "Q&A 模拟",       "AI 答辩",         "提前准备 · 现场自答"),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80, y0 + 8), "环节", font=font(13, bold=True), fill=AMBER)
    d.text((250, y0 + 8), "可以做", font=font(13, bold=True), fill=GREEN_LIGHT)
    d.text((460, y0 + 8), "不能做", font=font(13, bold=True), fill=RED_LIGHT)
    d.text((670, y0 + 8), "工程边界", font=font(13, bold=True), fill=CYAN)

    for i, (env, can, cant, edge) in enumerate(rows):
        y = y0 + 42 + i * 40
        rrect(d, [60, y, 1020, y + 32], 6, fill=DEEP)
        d.text((80, y + 8), env, font=font(13, bold=True), fill=WHITE)
        d.text((250, y + 8), "✓ " + can, font=font(12), fill=GREEN_LIGHT)
        d.text((460, y + 8), "✗ " + cant, font=font(12), fill=RED_LIGHT)
        d.text((670, y + 8), edge, font=font(12), fill=SUB)

    rrect(d, [60, 478, 1020, 510], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 488), "AI 写工具 · 不写观点 · 这是学术辅助的核心边界", font=font(13, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "02_scope.png"))
    print("[OK] 02_scope")


# ============ 03: 8 能力模块架构 ============
def img_03():
    img, d = base()
    d.text((60, 40), "8 能力模块架构", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "FastAPI 后端 + 8 个 router + 外部学术 API", font=font(15), fill=LIGHT)

    abilities = [
        ("/outline",    "大纲生成",     "Claude · 多版本",      CYAN),
        ("/section",    "章节起草",     "Claude · 留占位",      BLUE),
        ("/polish",     "学术润色",     "Claude · diff 输出",   GREEN),
        ("/cite",       "文献检索",     "arXiv + Crossref",    AMBER),
        ("/bib",        "引用格式",     "GB7714 / APA / IEEE", PURPLE),
        ("/dedupe",     "相似度检测",   "embedding · 本地",     ORANGE),
        ("/defense",    "答辩 Q&A",     "Claude 多 persona",    PINK),
        ("/export",     "Word/LaTeX",   "+ AI 协助报告",        TEAL),
    ]
    y0 = 120
    bw = 490
    bh = 60
    for i, (path, name, tech, c) in enumerate(abilities):
        col = i % 2
        row = i // 2
        x = 60 + col * (bw + 10)
        y = y0 + row * (bh + 12)
        rrect(d, [x, y, x + bw, y + bh], 10, fill=BOX, outline=c, width=2)
        d.rectangle([x, y, x + 4, y + bh], fill=c)
        d.text((x + 16, y + 10), path, font=mono(14), fill=c)
        d.text((x + 16, y + 32), name, font=font(15, bold=True), fill=WHITE)
        d.text((x + 200, y + 14), tech, font=font(12), fill=SUB)
        d.text((x + 200, y + 32), "└─ tech", font=font(10), fill=DIM)

    rrect(d, [60, 472, 1020, 510], 8, fill=DEEP, outline=RED, width=1)
    d.text((80, 482), "外部学术 API 不能省 · LLM 编文献是这场景最大事故源", font=font(13, bold=True), fill=RED_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_architecture.png"))
    print("[OK] 03_architecture")


# ============ 04: 写作流水线 ============
def img_04():
    img, d = base()
    d.text((60, 40), "写论文完整流水线", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "从选题到答辩 · 8 步全程 AI 辅助 · 但作者亲笔", font=font(15), fill=LIGHT)

    steps = [
        ("1", "选题",        "推荐方向",     CYAN),
        ("2", "大纲",        "多版本",       BLUE),
        ("3", "文献",        "DOI 校验",     AMBER),
        ("4", "起草",        "留占位",       GREEN),
        ("5", "润色",        "diff 改",      PURPLE),
        ("6", "引用",        "格式化",       PINK),
        ("7", "查重",        "改写自己",     ORANGE),
        ("8", "答辩",        "Q&A 模拟",     TEAL),
    ]
    y0 = 140
    bw = 122
    for i, (n, name, desc, c) in enumerate(steps):
        x = 60 + i * (bw + 4)
        rrect(d, [x, y0, x + bw, y0 + 130], 12, fill=BOX, outline=c, width=2)
        # number circle
        d.ellipse([x + 12, y0 + 14, x + 48, y0 + 50], fill=c)
        d.text((x + 23, y0 + 19), n, font=font(18, bold=True), fill=BG)
        # name
        d.text((x + 14, y0 + 64), name, font=font(17, bold=True), fill=WHITE)
        # desc
        d.text((x + 14, y0 + 94), desc, font=font(11), fill=SUB)
        # arrow
        if i < len(steps) - 1:
            ax = x + bw - 1
            d.line([(ax, y0 + 65), (ax + 4, y0 + 65)], fill=LINE, width=2)
            d.polygon([(ax + 6, y0 + 65), (ax, y0 + 61), (ax, y0 + 69)], fill=LINE)

    # bottom: AI 协助报告
    rrect(d, [60, 296, 1020, 380], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 308), "最终导出的论文 → 自动附 AI 协助报告", font=font(15, bold=True), fill=AMBER_LIGHT)
    d.text((80, 336), "· 哪些章节使用了 AI 辅助", font=font(13), fill=SUB)
    d.text((80, 354), "· 使用的具体工具(润色 / 大纲 / Q&A)", font=font(13), fill=SUB)

    rrect(d, [60, 400, 1020, 470], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((80, 412), "对齐 Nature / Science / IEEE 期刊 AI 政策", font=font(15, bold=True), fill=GREEN_LIGHT)
    d.text((80, 440), "已强制要求披露 AI 使用 · 本工具天然合规", font=font(13), fill=SUB)

    rrect(d, [60, 478, 1020, 510], 8, fill=DEEP, outline=NAVY_LIGHT, width=1)
    d.text((80, 488), "AI 辅助 · 作者亲笔 · 披露使用 · 三件套缺一不可", font=font(13, bold=True), fill=NAVY_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "04_pipeline.png"))
    print("[OK] 04_pipeline")


# ============ 05: 5 条反作弊红线 ============
def img_05():
    img, d = base()
    d.text((60, 40), "5 条反作弊工程红线", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "Hooks 写死规则 · 不让 LLM 自由发挥", font=font(15), fill=LIGHT)

    redlines = [
        ("1", "引用必须 DOI 校验",
              "Crossref API 验真 · 编造文献立即阻断",       RED),
        ("2", "章节自动加 [AI 辅助] 标签",
              "起草草稿头部注入标记 · 提醒作者补实质",      ORANGE),
        ("3", "降重禁止包装抄袭",
              "禁词:伪装原创 / 改写后无法识别 · 拦改",     PINK),
        ("4", "导出附 AI 协助清单",
              "全文哪些章节用了 AI · 用了哪些工具",        AMBER),
        ("5", "AI 内容比例监控",
              "超 80% → 警告 · 学术诚信提醒",              PURPLE),
    ]
    y0 = 116
    for i, (n, title, desc, c) in enumerate(redlines):
        y = y0 + i * 70
        rrect(d, [60, y, 1020, y + 60], 12, fill=BOX, outline=c, width=2)
        # number
        d.ellipse([76, y + 14, 124, y + 50], fill=c)
        d.text((90, y + 19), n, font=font(20, bold=True), fill=BG)
        # title
        d.text((148, y + 10), title, font=font(18, bold=True), fill=c)
        # desc
        d.text((148, y + 36), desc, font=font(13), fill=SUB)

    rrect(d, [60, 478, 1020, 510], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 488), "规则之内自由 · 规则之外硬拦 · 跟前几篇 Hooks 一脉相承", font=font(13, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_redlines.png"))
    print("[OK] 05_redlines")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
