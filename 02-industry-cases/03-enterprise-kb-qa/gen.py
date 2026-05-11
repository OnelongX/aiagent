# -*- coding: utf-8 -*-
"""5 images for 企业知识库+问答系统"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\企业知识库问答"
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
AMBER_DEEP = "#f59e0b"
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
TEAL_LIGHT = "#5eead4"
ORANGE = "#fb923c"
PINK = "#ec4899"
LIME = "#84cc16"

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


def tw(d, text, f):
    b = d.textbbox((0, 0), text, font=f)
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

    rrect(d, [60, 50, 240, 88], 19, fill=CYAN)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 506, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 · 行业落地", font=font(17, bold=True), fill=AMBER)

    d.text((60, 132), "企业级知识库 + 问答", font=font(38, bold=True), fill=AMBER)
    d.text((60, 188), "3 周落地的完整", font=font(26, bold=True), fill=WHITE)
    d.text((60, 224), "工程方案", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("权限隔离",  CYAN,        "ACL 三道闸门"),
        ("引用溯源",  GREEN,       "每句必引"),
        ("RAGAS 评测", PURPLE,      "4 指标自动跑"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=CYAN, width=2)
    d.text((80, 442), "80% 的工作量在 LLM 之外", font=font(22, bold=True), fill=CYAN_LIGHT)
    d.text((80, 478), "Chunking · 权限 · Rerank · 评测 · 审计", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 个人 vs 企业级 ============
def img_02():
    img, d = base()
    d.text((60, 40), "企业级 ≠ 个人 RAG", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "5 个非功能性要点 · 缺一不可", font=font(15), fill=LIGHT)

    rows = [
        ("数据",   "一次性上传",     "多源 + 增量同步",      CYAN),
        ("权限",   "全员可见",       "ACL 隔离 + 继承",       PURPLE),
        ("引用",   "可选",           "强制 · 每句必引",       GREEN),
        ("审计",   "无",             "谁问了什么 / 看了什么", AMBER),
        ("评测",   "凭感觉",         "RAGAS 自动跑",         PINK),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 38], 8, fill=BOX)
    d.text((80, y0 + 10), "维度", font=font(15, bold=True), fill=AMBER)
    d.text((260, y0 + 10), "个人 RAG", font=font(15, bold=True), fill=RED)
    d.text((620, y0 + 10), "企业级", font=font(15, bold=True), fill=GREEN_LIGHT)

    for i, (dim, p, e, c) in enumerate(rows):
        y = y0 + 52 + i * 74
        rrect(d, [60, y, 1020, y + 60], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 60], fill=c)
        d.text((80, y + 20), dim, font=font(17, bold=True), fill=WHITE)
        d.text((260, y + 20), p, font=font(14), fill=LIGHT)
        d.text((620, y + 20), e, font=font(15, bold=True), fill=GREEN_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "02_diff.png"))
    print("[OK] 02_diff")


# ============ 03: 三层架构 ============
def img_03():
    img, d = base()
    d.text((60, 40), "三层架构", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "数据层 · 索引层 · 查询层 · 自上而下打通", font=font(15), fill=LIGHT)

    # 3 layers
    layers = [
        ("数据层",  CYAN,    "Connectors(Confluence/Notion/SP/PDF/Slack/Jira/Git/Email)+ 增量同步"),
        ("索引层",  PURPLE,  "Chunking → Embedding → Vector DB · BM25 倒排 · ACL 元数据"),
        ("查询层",  GREEN,   "Claude Agent SDK · Hybrid Retrieval → Rerank → Cite · Audit Log"),
    ]
    y0 = 120
    for i, (name, c, desc) in enumerate(layers):
        y = y0 + i * 116
        rrect(d, [60, y, 1020, y + 96], 14, fill=BOX, outline=c, width=2)
        rrect(d, [60, y, 200, y + 96], 14, fill=c)
        d.text((78, y + 26), name, font=font(22, bold=True), fill=BG)
        d.text((78, y + 56), f"Layer {i+1}", font=font(13, bold=True), fill=BG)
        # wrap desc
        d.text((228, y + 24), desc[:38], font=font(15), fill=SUB)
        if len(desc) > 38:
            d.text((228, y + 52), desc[38:], font=font(15), fill=SUB)
        # arrow between
        if i < 2:
            ay = y + 100
            d.line([(540, ay), (540, ay + 14)], fill=LINE, width=2)
            d.polygon([(540, ay + 22), (534, ay + 14), (546, ay + 14)], fill=LINE)

    watermark(d)
    img.save(os.path.join(OUT, "03_architecture.png"))
    print("[OK] 03_architecture")


# ============ 04: 技术选型 ============
def img_04():
    img, d = base()
    d.text((60, 40), "技术选型 · 2026 推荐栈", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "不造轮子 · 全用现成组件", font=font(15), fill=LIGHT)

    stack = [
        ("Connectors", "Airbyte",            CYAN),
        ("Parser",     "Unstructured.io",    BLUE_LIGHT),
        ("Chunking",   "Late Chunking",      GREEN),
        ("Embedding",  "BGE-M3",             GREEN_LIGHT),
        ("Vector DB",  "Qdrant",             PURPLE),
        ("倒排索引",   "OpenSearch",         PURPLE_LIGHT),
        ("Reranker",   "Cohere rerank-3.5",  AMBER),
        ("评测",       "RAGAS",              PINK),
        ("Orchestrator","Claude Agent SDK",   ORANGE),
        ("LLM",        "Claude Sonnet 4.5",  ORANGE),
    ]
    y0 = 124
    for i, (mod, choice, c) in enumerate(stack):
        col = i % 2
        row = i // 2
        x = 60 + col * 490
        y = y0 + row * 78
        rrect(d, [x, y, x + 472, y + 64], 10, fill=BOX, outline=c, width=2)
        d.text((x + 16, y + 12), mod, font=font(13), fill=DIM)
        d.text((x + 16, y + 32), choice, font=mono(17), fill=c)

    watermark(d)
    img.save(os.path.join(OUT, "04_stack.png"))
    print("[OK] 04_stack")


# ============ 05: 3 周落地 ============
def img_05():
    img, d = base()
    d.text((60, 40), "3 周落地路线", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "MVP → 多源权限 → 评测上线", font=font(15), fill=LIGHT)

    weeks = [
        ("W1", "单源 MVP",      "Confluence + Qdrant + Claude\n内网 demo 跑通",                CYAN,    "5 天"),
        ("W2", "多源 + 权限",   "Notion/SP/Slack 接入\nACL 三道闸门 + 引用 + 审计",            PURPLE,  "5 天"),
        ("W3", "评测 + 上线",   "RAGAS 黄金集 + 反馈按钮\n灰度 10% 员工",                       GREEN,   "5 天"),
    ]
    y0 = 130
    bw = 320
    for i, (w, title, desc, c, days) in enumerate(weeks):
        x = 60 + i * (bw + 20)
        rrect(d, [x, y0, x + bw, y0 + 200], 14, fill=BOX, outline=c, width=2)
        # week badge
        rrect(d, [x + 16, y0 + 16, x + 80, y0 + 50], 16, fill=c)
        d.text((x + 30, y0 + 22), w, font=font(20, bold=True), fill=BG)
        # days badge
        rrect(d, [x + bw - 80, y0 + 16, x + bw - 16, y0 + 50], 16, fill=DEEP)
        d.text((x + bw - 68, y0 + 22), days, font=font(15, bold=True), fill=c)
        # title
        d.text((x + 16, y0 + 64), title, font=font(20, bold=True), fill=WHITE)
        # desc
        lines = desc.split("\n")
        for j, line in enumerate(lines):
            d.text((x + 16, y0 + 100 + j * 26), line, font=font(13), fill=SUB)
        # arrow
        if i < 2:
            ax = x + bw + 2
            d.line([(ax, y0 + 100), (ax + 14, y0 + 100)], fill=LINE, width=2)
            d.polygon([(ax + 18, y0 + 100), (ax + 10, y0 + 94), (ax + 10, y0 + 106)], fill=LINE)

    # bottom callout
    rrect(d, [60, 360, 1020, 510], 12, fill=DEEP, outline=CYAN, width=2)
    d.text((80, 374), "MVP 第一性原理", font=font(17, bold=True), fill=CYAN_LIGHT)
    d.text((80, 406), "· W1 别上 Reranker / Late Chunking", font=font(15), fill=SUB)
    d.text((80, 432), "· 先验证产品价值,再优化质量", font=font(15), fill=SUB)
    d.text((80, 458), "· 任一指标跌 5% → block 上线(W3 后的纪律)", font=font(15), fill=SUB)
    d.text((80, 484), "· LLM 是最后一公里,前 80% 才是壁垒", font=font(15, bold=True), fill=GREEN_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_timeline.png"))
    print("[OK] 05_timeline")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
