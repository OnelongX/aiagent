# -*- coding: utf-8 -*-
"""5 images for 全栈 AI 工作台 · 行业落地 #6 · 集大成压轴"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\全栈AI工作台"
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
AMBER_LIGHT = "#fcd34d"
RED = "#ef4444"
GREEN = "#22c55e"
GREEN_LIGHT = "#4ade80"
EMERALD = "#10b981"
EMERALD_LIGHT = "#34d399"
PURPLE = "#a855f7"
BLUE = "#3b82f6"
BLUE_LIGHT = "#60a5fa"
CYAN = "#06b6d4"
ORANGE = "#fb923c"
PINK = "#ec4899"
TEAL = "#14b8a6"
INDIGO = "#6366f1"

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
    rrect(d, [256, 50, 560, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地 #6 · 集大成压轴", font=font(16, bold=True), fill=AMBER_LIGHT)

    d.text((60, 128), "全栈 AI 工作台", font=font(40, bold=True), fill=AMBER)
    d.text((60, 184), "从工具调度 到产品级", font=font(26, bold=True), fill=WHITE)
    d.text((60, 220), "Agent 的工程账本", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("Vue + FastAPI",     EMERALD_LIGHT, "全栈分离"),
        ("Chroma + SQLite",   BLUE_LIGHT,    "向量 + 元数据"),
        ("Docker 一键起",     PURPLE,        "可交付客户"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(20, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=EMERALD, width=2)
    d.text((80, 442), "工具调度 3 周 · 产品工作台 3 个月", font=font(20, bold=True), fill=EMERALD_LIGHT)
    d.text((80, 478), "工程量 10 倍 · 但能卖给 N 个客户", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 工具调度 vs 产品工作台 ============
def img_02():
    img, d = base()
    d.text((60, 40), "工具调度 vs 产品工作台", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "前 5 篇 vs 本篇 · 工程量差一个数量级", font=font(15), fill=LIGHT)

    rows = [
        ("形态",       "CLI / Notebook",          "Web App + 后端服务",       BLUE),
        ("持久化",     "Redis 临时",              "SQLite + Chroma + uploads", CYAN),
        ("用户",       "开发者自己",              "业务用户(非技术)",        PINK),
        ("多能力",     "单流程",                  "8 个页面共享 Chat 链路",    EMERALD),
        ("部署",       "本地脚本",                "Docker compose 一键",       PURPLE),
        ("商业化",     "给自己用",                "可交付客户私有部署",        ORANGE),
        ("起步周期",   "3 周 MVP",                "3 个月起",                  RED),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 34], 8, fill=BOX)
    d.text((80, y0 + 8), "维度", font=font(14, bold=True), fill=AMBER)
    d.text((260, y0 + 8), "工具调度 (#1-#5)", font=font(14, bold=True), fill=LIGHT)
    d.text((620, y0 + 8), "产品工作台 (本篇)", font=font(14, bold=True), fill=EMERALD_LIGHT)

    for i, (dim, a, b, c) in enumerate(rows):
        y = y0 + 44 + i * 50
        rrect(d, [60, y, 1020, y + 42], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 42], fill=c)
        d.text((80, y + 13), dim, font=font(15, bold=True), fill=WHITE)
        d.text((260, y + 13), a, font=font(13), fill=LIGHT)
        d.text((620, y + 13), b, font=font(14, bold=True), fill=EMERALD_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "02_diff.png"))
    print("[OK] 02_diff")


# ============ 03: 整体架构 ============
def img_03():
    img, d = base()
    d.text((60, 40), "整体架构 · 4 层全栈", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "Vue 前端 → FastAPI 后端 → 数据层 → Docker 部署", font=font(15), fill=LIGHT)

    layers = [
        ("前端", "Vue 3 + Vite + Pinia · Sidebar 聚合 8 个页面",     EMERALD,  108),
        ("API",  "FastAPI · /api/chat /knowledge /tools /settings", BLUE,     200),
        ("数据", "Chroma 向量 + SQLite 元数据 + uploads/ 原始文件",  PURPLE,   292),
        ("部署", "Docker Compose · backend:8001 + frontend:80",     ORANGE,   384),
    ]
    for name, desc, c, y in layers:
        rrect(d, [60, y, 1020, y + 76], 12, fill=BOX, outline=c, width=2)
        rrect(d, [60, y, 180, y + 76], 12, fill=c)
        d.text((78, y + 16), name, font=font(22, bold=True), fill=BG)
        d.text((78, y + 46), "Layer", font=font(12, bold=True), fill=BG)
        d.text((208, y + 26), desc, font=font(15), fill=SUB)
        # arrow
        if y < 380:
            ay = y + 78
            d.line([(540, ay), (540, ay + 8)], fill=LINE, width=2)
            d.polygon([(540, ay + 14), (534, ay + 6), (546, ay + 6)], fill=LINE)

    # bottom data flow
    rrect(d, [60, 472, 1020, 510], 8, fill=DEEP, outline=EMERALD, width=1)
    d.text((80, 482), "所有页面共享 Chat 链路 · Script/Rewrite/Topic 都是前端拼 prompt 调 chat", font=font(13, bold=True), fill=EMERALD_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_architecture.png"))
    print("[OK] 03_architecture")


# ============ 04: 多检索源融合 + 触发词路由 ============
def img_04():
    img, d = base()
    d.text((60, 40), "3 源并发检索 · 触发词路由", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "确定性逻辑放工具层 · 不让 LLM 决定路由", font=font(15), fill=LIGHT)

    # user query box
    rrect(d, [60, 116, 460, 168], 12, fill=BOX, outline=BLUE, width=2)
    d.text((80, 128), "用户问题", font=font(15, bold=True), fill=BLUE)
    d.text((80, 148), "「6500W 三相阳光电源对比华为」", font=mono(13), fill=SUB)

    # arrow
    d.line([(478, 142), (510, 142)], fill=AMBER, width=2)
    d.polygon([(518, 142), (508, 136), (508, 148)], fill=AMBER)

    # 3 sources
    rrect(d, [528, 116, 1020, 168], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((548, 128), "3 源并发检索", font=font(15, bold=True), fill=AMBER_LIGHT)
    d.text((548, 148), "RAG + 产品库 + 历史 · 拼接喂 LLM", font=font(13), fill=SUB)

    # detail boxes
    sources = [
        ("① RAG 检索",      "始终跑",           "文档片段 + 引用",    EMERALD),
        ("② 产品库",        "触发词命中",       "结构化对比表",       PINK),
        ("③ 历史压缩",      "始终带",           "最近 20 轮",         BLUE),
    ]
    y0 = 192
    for i, (name, when, output, c) in enumerate(sources):
        x = 60 + i * 326
        rrect(d, [x, y0, x + 312, y0 + 132], 12, fill=BOX, outline=c, width=2)
        d.text((x + 16, y0 + 14), name, font=font(18, bold=True), fill=c)
        d.text((x + 16, y0 + 50), "触发", font=font(12), fill=DIM)
        d.text((x + 16, y0 + 68), when, font=font(14, bold=True), fill=WHITE)
        d.text((x + 16, y0 + 92), "输出", font=font(12), fill=DIM)
        d.text((x + 16, y0 + 110), output, font=font(14, bold=True), fill=SUB)

    # trigger words box
    rrect(d, [60, 348, 1020, 460], 12, fill=DEEP, outline=PINK, width=2)
    d.text((80, 360), "产品库触发词 · 4 类混排(意图 + 行业 + 品牌 + 技术)", font=font(15, bold=True), fill=PINK)
    words = [
        ("意图",  "推荐 / 选型 / 哪款 / 对比 / 型号",  AMBER),
        ("行业",  "逆变器 / 电池 / 储能 / 光伏 / 组件", BLUE_LIGHT),
        ("品牌",  "华为 / 阳光电源 / 宁德 / 比亚迪",   ORANGE),
        ("技术",  "LFP / TOPCon / HJT / PERC",         GREEN_LIGHT),
    ]
    for i, (k, v, c) in enumerate(words):
        col = i % 2
        row = i // 2
        x = 80 + col * 470
        y = 388 + row * 28
        d.text((x, y), k, font=font(12, bold=True), fill=c)
        d.text((x + 50, y), v, font=mono(12), fill=SUB)

    # bottom callout
    rrect(d, [60, 472, 1020, 510], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 482), "为什么不全交给 LLM 判断?成本 + 延迟 + 稳定性 · 触发词不漂移不付费", font=font(13, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "04_routing.png"))
    print("[OK] 04_routing")


# ============ 05: 三大数据一致性坑 ============
def img_05():
    img, d = base()
    d.text((60, 40), "三大数据一致性坑(踩过的)", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "真实生产里 90% 的 bug 都在数据一致性,不在 LLM", font=font(15), fill=LIGHT)

    pits = [
        ("坑 1", "前后端字段契约",  "后端 time vs 前端 timestamp", "Schema 同源生成", RED),
        ("坑 2", "文档 ID 路径耦合", "移分类 → 文档身份漂移",     "UUID + registry", ORANGE),
        ("坑 3", "中文检索拆词差",  "q.split() 召回为 0",          "归一化 + 别名",   PINK),
    ]
    y0 = 124
    for i, (n, title, problem, fix, c) in enumerate(pits):
        y = y0 + i * 100
        rrect(d, [60, y, 1020, y + 88], 12, fill=BOX, outline=c, width=2)
        # number circle
        d.ellipse([76, y + 22, 124, y + 70], fill=c)
        d.text((92, y + 28), n, font=font(16, bold=True), fill=BG)
        # title
        d.text((148, y + 12), title, font=font(20, bold=True), fill=c)
        # problem
        d.text((148, y + 42), "症状", font=font(12), fill=DIM)
        d.text((200, y + 42), problem, font=mono(13), fill=SUB)
        # fix
        d.text((148, y + 62), "纪律", font=font(12), fill=DIM)
        d.text((200, y + 62), fix, font=font(14, bold=True), fill=GREEN_LIGHT)

    rrect(d, [60, 436, 1020, 510], 12, fill=DEEP, outline=EMERALD, width=2)
    d.text((80, 452), "真正决定成败的 3 件事", font=font(17, bold=True), fill=EMERALD_LIGHT)
    d.text((80, 480), "数据主键稳定 · 前后端契约 · 触发词路由", font=font(14), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "05_pitfalls.png"))
    print("[OK] 05_pitfalls")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
