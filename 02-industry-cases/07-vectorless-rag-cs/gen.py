# -*- coding: utf-8 -*-
"""5 images for Vectorless RAG · 行业落地 #7"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
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
GREEN = "#22c55e"
GREEN_LIGHT = "#4ade80"
PURPLE = "#a855f7"
PURPLE_LIGHT = "#c084fc"
BLUE = "#3b82f6"
BLUE_LIGHT = "#60a5fa"
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

    rrect(d, [60, 50, 240, 88], 19, fill=ROSE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地 #7", font=font(17, bold=True), fill=AMBER_LIGHT)

    d.text((60, 128), "Vectorless RAG", font=font(46, bold=True), fill=AMBER)
    d.text((60, 188), "智能客服 · PageIndex", font=font(26, bold=True), fill=WHITE)
    d.text((60, 224), "中文实战 + 完整可跑代码", font=font(24, bold=True), fill=WHITE)

    chips = [
        ("不切块",   GREEN_LIGHT,  "按章节"),
        ("不向量",   ROSE,         "LLM 推理"),
        ("可解释",   CYAN,         "审计友好"),
    ]
    y = 296
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 514], 14, fill=DEEP, outline=ROSE, width=2)
    d.text((80, 448), "#6 用 Chroma · 这一篇换条路", font=font(20, bold=True), fill="#fb7185")
    d.text((80, 482), "PDF → 章节树 → LLM 推理选章节 → 读原文", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "images", "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 向量 RAG vs Vectorless ============
def img_02():
    img, d = base()
    d.text((60, 40), "向量 RAG vs Vectorless RAG", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "不是替代关系 · 是互补 · 选对场景才高效", font=font(15), fill=LIGHT)

    rows = [
        ("切块",      "固定 size + overlap",  "按文档结构(章节)",        BLUE),
        ("检索",      "embedding + cosine",   "LLM 推理选章节",           GREEN),
        ("依赖",      "向量库 + embedding",   "不要向量库",               PURPLE),
        ("长文档",    "切块易失语义",         "保留章节完整",              PINK),
        ("中文",      "看 embedding 质量",    "不依赖 embedding",          ORANGE),
        ("速度",      "毫秒级",               "秒级",                      AMBER),
        ("可解释",    "黑盒",                 "LLM 输出选章节理由",        CYAN),
    ]
    y0 = 116
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80, y0 + 8), "维度", font=font(14, bold=True), fill=AMBER)
    d.text((250, y0 + 8), "#6 向量 RAG", font=font(14, bold=True), fill=LIGHT)
    d.text((620, y0 + 8), "#7 Vectorless(本篇)", font=font(14, bold=True), fill=ROSE)

    for i, (dim, a, b, c) in enumerate(rows):
        y = y0 + 42 + i * 50
        rrect(d, [60, y, 1020, y + 42], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 42], fill=c)
        d.text((80, y + 13), dim, font=font(15, bold=True), fill=WHITE)
        d.text((250, y + 13), a, font=font(13), fill=LIGHT)
        d.text((620, y + 13), b, font=font(14, bold=True), fill=ROSE)

    watermark(d)
    img.save(os.path.join(OUT, "images", "02_compare.png"))
    print("[OK] 02_compare")


# ============ 03: 整体架构 ============
def img_03():
    img, d = base()
    d.text((60, 40), "整体架构 · 4 层", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "纯静态前端 → FastAPI → 任务队列 + PageIndex → SQLite + 文件", font=font(15), fill=LIGHT)

    layers = [
        ("前端",      "纯 HTML + JS(无框架) · Chat/KB/Settings",    ROSE,     108),
        ("API",       "FastAPI · upload/tasks/chat/documents",       BLUE,     200),
        ("核心",      "task_queue + PageIndex Tree + LLM 推理",      GREEN,    292),
        ("数据",      "SQLite + knowledge/*.pdf + indexes/*.json",   PURPLE,   384),
    ]
    for name, desc, c, y in layers:
        rrect(d, [60, y, 1020, y + 76], 12, fill=BOX, outline=c, width=2)
        rrect(d, [60, y, 180, y + 76], 12, fill=c)
        d.text((78, y + 16), name, font=font(22, bold=True), fill=BG)
        d.text((78, y + 46), "Layer", font=font(12, bold=True), fill=BG)
        d.text((208, y + 26), desc, font=font(15), fill=SUB)
        if y < 380:
            ay = y + 78
            d.line([(540, ay), (540, ay + 8)], fill=LINE, width=2)
            d.polygon([(540, ay + 14), (534, ay + 6), (546, ay + 6)], fill=LINE)

    rrect(d, [60, 472, 1020, 510], 8, fill=DEEP, outline=ROSE, width=1)
    d.text((80, 482), "LLM 既是生成器,也是检索器 · 这是 Vectorless 范式的核心", font=font(13, bold=True), fill="#fb7185")

    watermark(d)
    img.save(os.path.join(OUT, "images", "03_architecture.png"))
    print("[OK] 03_architecture")


# ============ 04: PageIndex 工作流 ============
def img_04():
    img, d = base()
    d.text((60, 40), "PageIndex 工作流", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "PDF → 树状结构 → LLM 选章节 → 读原文 → 生成", font=font(15), fill=LIGHT)

    # 5 步流程
    steps = [
        ("1", "PDF 抽文本",     "PyMuPDF / RapidOCR",      BLUE,    60),
        ("2", "切章节",          "PageIndex 按目录",         GREEN,   258),
        ("3", "生成描述",        "LLM 写 章节 desc + kw",   PURPLE,  456),
        ("4", "查询 → 看树",     "LLM 推理选章节",          ROSE,    60),
        ("5", "读章节 → 生成",   "PyMuPDF 按 page_range",   AMBER,   258),
    ]
    # 第 1 行 3 个
    for i in range(3):
        n, title, desc, c, x = steps[i]
        y = 120
        rrect(d, [x, y, x + 188, y + 100], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x + 12, y + 12, x + 56, y + 56], 14, fill=c)
        d.text((x + 27, y + 22), n, font=font(20, bold=True), fill=BG)
        d.text((x + 70, y + 22), title, font=font(15, bold=True), fill=c)
        d.text((x + 12, y + 64), desc, font=mono(11), fill=SUB)
        if i < 2:
            ax = x + 188
            d.line([(ax, y + 50), (ax + 8, y + 50)], fill=LINE, width=2)
            d.polygon([(ax + 10, y + 50), (ax + 4, y + 46), (ax + 4, y + 54)], fill=LINE)

    # 中间转向标记
    d.text((650, 230), "完成索引", font=font(14, bold=True), fill=AMBER_LIGHT)
    d.text((650, 250), "↓", font=font(20), fill=AMBER_LIGHT)
    d.text((650, 270), "查询时", font=font(14, bold=True), fill=ROSE)

    # 第 2 行 2 个
    for i in range(3, 5):
        n, title, desc, c, x = steps[i]
        y = 308
        rrect(d, [x, y, x + 188, y + 100], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x + 12, y + 12, x + 56, y + 56], 14, fill=c)
        d.text((x + 27, y + 22), n, font=font(20, bold=True), fill=BG)
        d.text((x + 70, y + 22), title, font=font(15, bold=True), fill=c)
        d.text((x + 12, y + 64), desc, font=mono(11), fill=SUB)
        if i < 4:
            ax = x + 188
            d.line([(ax, y + 50), (ax + 8, y + 50)], fill=LINE, width=2)
            d.polygon([(ax + 10, y + 50), (ax + 4, y + 46), (ax + 4, y + 54)], fill=LINE)

    # 树状示例
    rrect(d, [60, 432, 1020, 510], 12, fill=DEEP, outline=GREEN_LIGHT, width=2)
    d.text((80, 446), "示例 structure.json", font=font(13, bold=True), fill=GREEN_LIGHT)
    d.text((80, 470), "├─ 1. Product Overview (page 1-2)", font=mono(11), fill=SUB)
    d.text((80, 484), "├─ 2. Electrical Performance (page 3-5)", font=mono(11), fill=SUB)
    d.text((400, 470), "│  ├─ 2.1 STC Conditions (page 3)", font=mono(11), fill=SUB)
    d.text((400, 484), "│  └─ 2.2 NOCT Conditions (page 4-5)", font=mono(11), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "images", "04_pageindex.png"))
    print("[OK] 04_pageindex")


# ============ 05: 选型决策矩阵 ============
def img_05():
    img, d = base()
    d.text((60, 40), "选型决策矩阵 · 什么时候用哪种 RAG", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "经验法则:文档数 × 长度 > 10 万页 用向量,反之 Vectorless", font=font(15), fill=LIGHT)

    rows = [
        ("短文档 / FAQ",          "#6 向量",          GREEN,    "Vectorless 不划算"),
        ("长结构化文档",          "#7 Vectorless",    ROSE,     "按章节最稳"),
        ("中文表达多变",          "#7 Vectorless",    ROSE,     "embedding 漂移"),
        ("需要引用页码",          "#7 Vectorless",    ROSE,     "天然支持"),
        ("文档数 > 1000",         "#6 向量",          GREEN,    "树喂不进 LLM"),
        ("文档数 < 100",          "#7 Vectorless",    ROSE,     "精度优先"),
        ("高并发实时(IM 客服)",  "#6 向量",          GREEN,    "毫秒级"),
        ("合规审计场景",          "#7 Vectorless",    ROSE,     "可解释"),
    ]
    y0 = 112
    # header
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80, y0 + 8), "场景", font=font(14, bold=True), fill=AMBER)
    d.text((400, y0 + 8), "推荐方案", font=font(14, bold=True), fill=AMBER)
    d.text((680, y0 + 8), "原因", font=font(14, bold=True), fill=AMBER)

    for i, (scenario, choice, c, reason) in enumerate(rows):
        y = y0 + 42 + i * 40
        rrect(d, [60, y, 1020, y + 32], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 32], fill=c)
        d.text((80, y + 8), scenario, font=font(14, bold=True), fill=WHITE)
        d.text((400, y + 8), choice, font=mono(14), fill=c)
        d.text((680, y + 8), reason, font=font(13), fill=SUB)

    rrect(d, [60, 472, 1020, 510], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 482), "两种方案本仓库都有完整可跑代码(#6 Chroma + #7 PageIndex) · 选适合的", font=font(13, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "images", "05_decision.png"))
    print("[OK] 05_decision")


if __name__ == "__main__":
    os.makedirs(os.path.join(OUT, "images"), exist_ok=True)
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", os.path.join(OUT, "images"))
