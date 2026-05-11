# -*- coding: utf-8 -*-
"""5 images for 自媒体写作+脚本 Agent · 跨行业平移第 2 篇"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\写作脚本Agent"
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
RED = "#ef4444"
GREEN = "#22c55e"
GREEN_LIGHT = "#4ade80"
PURPLE = "#a855f7"
PURPLE_LIGHT = "#c084fc"
BLUE = "#3b82f6"
BLUE_LIGHT = "#60a5fa"
CYAN = "#06b6d4"
ORANGE = "#fb923c"
ORANGE_LIGHT = "#fdba74"
PINK = "#ec4899"
ROSE = "#f43f5e"
TEAL = "#14b8a6"
INDIGO = "#6366f1"
INDIGO_LIGHT = "#818cf8"
VIOLET = "#8b5cf6"
VIOLET_LIGHT = "#a78bfa"
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

    rrect(d, [60, 50, 240, 88], 19, fill=INDIGO)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 560, 88], 19, fill=BOX)
    d.text((274, 56), "跨行业平移 · 第 2 篇", font=font(17, bold=True), fill=AMBER)

    d.text((60, 128), "自媒体写作 + 脚本 Agent", font=font(34, bold=True), fill=AMBER)
    d.text((60, 184), "Claude 当编辑 / 风格守门员", font=font(24, bold=True), fill=WHITE)
    d.text((60, 218), "复盘师", font=font(24, bold=True), fill=WHITE)

    chips = [
        ("一致",    INDIGO_LIGHT,  "Persona Lock"),
        ("不重复",  VIOLET_LIGHT,  "Embedding 去重"),
        ("越写越准", PINK,          "DSAT 闭环"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=INDIGO, width=2)
    d.text((80, 442), "把我手动跑过去 17 次的工作流 · 做成 Agent", font=font(20, bold=True), fill=INDIGO_LIGHT)
    d.text((80, 478), "用 Agent 写「如何用 Agent 写文章」的文章 · meta 自证", font=font(14), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 长文 vs 视频脚本 ============
def img_02():
    img, d = base()
    d.text((60, 40), "两类内容 · 不同节奏", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "长文 vs 视频脚本 · prompt 绝对不能共用", font=font(15), fill=LIGHT)

    rows = [
        ("长度",   "2000-5000 字",         "30s-3min · 口播 200-1500 字", INDIGO),
        ("结构",   "罗马数字 / 表格 / 代码", "钩子 → 主线 → 转折 → 结尾",   PURPLE),
        ("节奏",   "段落清晰 · 信息密度高",  "单句低密度 · 节奏感强",       PINK),
        ("视觉",   "PIL 配图 5 张",         "分镜 + B-roll + 字幕",        BLUE),
        ("发布",   "WeChat MP API",         "抖音 / 视频号 / B 站",         GREEN),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 36], 8, fill=BOX)
    d.text((80, y0 + 9), "维度", font=font(15, bold=True), fill=AMBER)
    d.text((250, y0 + 9), "公众号长文", font=font(15, bold=True), fill=INDIGO_LIGHT)
    d.text((620, y0 + 9), "短视频脚本", font=font(15, bold=True), fill=PINK)

    for i, (dim, a, b, c) in enumerate(rows):
        y = y0 + 50 + i * 70
        rrect(d, [60, y, 1020, y + 58], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 58], fill=c)
        d.text((80, y + 18), dim, font=font(17, bold=True), fill=WHITE)
        d.text((250, y + 18), a, font=font(14), fill=LIGHT)
        d.text((620, y + 18), b, font=font(14, bold=True), fill=PINK)

    watermark(d)
    img.save(os.path.join(OUT, "02_dual_type.png"))
    print("[OK] 02_dual_type")


# ============ 03: 7 段流水线 ============
def img_03():
    img, d = base()
    d.text((60, 40), "7 段流水线", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "每段对应一个 Subagent · Claude 全程编排", font=font(15), fill=LIGHT)

    stages = [
        ("选题",      "topic-miner",          "haiku",  CYAN),
        ("大纲",      "outline-writer",       "opus",   INDIGO),
        ("写作",      "article/video-writer", "sonnet", VIOLET),
        ("视觉",      "visual-coder",         "sonnet", PINK),
        ("多平台",    "adapter",              "sonnet", ORANGE),
        ("发布",      "publisher",            "haiku",  GREEN),
        ("回流",      "analyst",              "sonnet", AMBER),
    ]
    y0 = 130
    bw = 130
    gap = 6
    for i, (cn, en, model, c) in enumerate(stages):
        x = 60 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 130], 12, fill=BOX, outline=c, width=2)
        d.text((x + 14, y0 + 16), cn, font=font(22, bold=True), fill=c)
        d.text((x + 14, y0 + 58), en, font=mono(11), fill=SUB)
        # model badge
        rrect(d, [x + 14, y0 + 92, x + bw - 14, y0 + 116], 10, fill=DEEP)
        d.text((x + 22, y0 + 96), model, font=mono(11), fill=c)
        # arrow
        if i < len(stages) - 1:
            ax = x + bw + 1
            d.line([(ax, y0 + 65), (ax + 4, y0 + 65)], fill=LINE, width=2)
            d.polygon([(ax + 6, y0 + 65), (ax + 2, y0 + 61), (ax + 2, y0 + 69)], fill=LINE)

    # 三层风格守门
    d.text((60, 296), "风格控制 · 三层守门", font=font(17, bold=True), fill=AMBER)
    layers = [
        ("第 1 层", "Few-shot 例子",      "传 3 篇风格样本",        INDIGO),
        ("第 2 层", "Style Embedding",    "新文 vs 历史 cosine 打分", VIOLET),
        ("第 3 层", "Persona Lock",       "system_prompt 固化档案",  PINK),
    ]
    for i, (n, name, desc, c) in enumerate(layers):
        x = 60 + i * 326
        rrect(d, [x, 332, x + 312, 432], 12, fill=BOX, outline=c, width=2)
        d.text((x + 16, 344), n, font=font(13), fill=c)
        d.text((x + 16, 366), name, font=mono(15), fill=WHITE)
        d.text((x + 16, 396), desc, font=font(13), fill=SUB)

    # bottom — core insight
    rrect(d, [60, 454, 1020, 510], 12, fill=DEEP, outline=INDIGO, width=2)
    d.text((80, 470), "Claude 不只是写手 · 还要当编辑 / 风格守门员 / 复盘师", font=font(15, bold=True), fill=INDIGO_LIGHT)
    d.text((80, 492), "一个角色搞不定 · 必须 Subagent 分工", font=font(13), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_pipeline.png"))
    print("[OK] 03_pipeline")


# ============ 04: 25 工具 5 类 ============
def img_04():
    img, d = base()
    d.text((60, 40), "25 工具 · 5 类", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "选题 / 长文 / 脚本 / 视觉 / 多平台", font=font(15), fill=LIGHT)

    cats = [
        ("A 选题挖掘", CYAN, [
            "fetch_industry_news",
            "search_my_history",
            "mining_comments",
            "analyze_competitor",
            "hot_keyword_trend",
        ]),
        ("B 长文写作", INDIGO, [
            "generate_outline",
            "write_article",
            "polish_article",
            "generate_title_candidates",
            "generate_digest",
            "generate_keywords",
        ]),
        ("C 视频脚本", VIOLET, [
            "generate_video_outline",
            "generate_video_script",
            "estimate_duration",
            "generate_teleprompter",
            "generate_storyboard",
        ]),
        ("D 视觉工具", PINK, [
            "generate_pil_code  ← 取代 gen.py",
            "render_images",
            "generate_cover_prompt",
        ]),
        ("E 多平台 + 发布", ORANGE, [
            "adapt_xhs / adapt_x_thread / adapt_zhihu",
            "publish_wechat / publish_xhs / post_x_thread",
            "publish_video_draft",
        ]),
    ]

    layout = [
        (60, 116, 520, 226),    # A
        (540, 116, 1020, 250),  # B
        (60, 246, 520, 366),    # C
        (540, 270, 1020, 390),  # D
        (60, 386, 1020, 510),   # E
    ]
    for (name, c, items), (x1, y1, x2, y2) in zip(cats, layout):
        rrect(d, [x1, y1, x2, y2], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x1, y1, x1 + 140, y1 + 30], 8, fill=c)
        d.text((x1 + 12, y1 + 5), name, font=font(15, bold=True), fill=BG)
        for j, it in enumerate(items):
            d.text((x1 + 16, y1 + 40 + j * 18), "· " + it, font=mono(12), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_tools.png"))
    print("[OK] 04_tools")


# ============ 05: 多平台调性 + 3 周路线 ============
def img_05():
    img, d = base()
    d.text((60, 40), "多平台调性 + 3 周落地", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "每平台专门 prompt · 不是简单截短", font=font(15), fill=LIGHT)

    # platforms table
    plats = [
        ("公众号",     "深度 + 结构",         "2000-5000字",      GREEN),
        ("小红书",     "种草 + emoji",        "500-1500字",       PINK),
        ("X Thread",   "短句 + 数据",         "1500字 thread",    BLUE),
        ("知乎",       "干货 + 引证",         "3000+字",          AMBER),
        ("B站/视频号", "口播 + 字幕",         "30s-10min",        VIOLET),
    ]
    y0 = 116
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80, y0 + 8), "平台", font=font(14, bold=True), fill=AMBER)
    d.text((310, y0 + 8), "调性", font=font(14, bold=True), fill=AMBER)
    d.text((700, y0 + 8), "长度", font=font(14, bold=True), fill=AMBER)

    for i, (p, t, l, c) in enumerate(plats):
        y = y0 + 42 + i * 38
        rrect(d, [60, y, 1020, y + 32], 6, fill=DEEP)
        d.rectangle([60, y, 64, y + 32], fill=c)
        d.text((80, y + 8), p, font=font(15, bold=True), fill=c)
        d.text((310, y + 8), t, font=font(13), fill=SUB)
        d.text((700, y + 8), l, font=font(13), fill=LIGHT)

    # 3 weeks
    d.text((60, 342), "3 周落地路线", font=font(17, bold=True), fill=AMBER)
    weeks = [
        ("W1", "长文 + PIL 自动化",  "miner + outline + writer + visual",  INDIGO),
        ("W2", "多平台改写",          "adapt 工具 + publisher",            VIOLET),
        ("W3", "视频脚本 + 数据回流", "video-writer + analyst + DSAT",     PINK),
    ]
    y0 = 378
    bw = 320
    for i, (w, title, desc, c) in enumerate(weeks):
        x = 60 + i * (bw + 20)
        rrect(d, [x, y0, x + bw, y0 + 110], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x + 14, y0 + 14, x + 74, y0 + 48], 16, fill=c)
        d.text((x + 26, y0 + 20), w, font=font(20, bold=True), fill=BG)
        d.text((x + 90, y0 + 20), title, font=font(15, bold=True), fill=WHITE)
        d.text((x + 14, y0 + 64), "→ " + desc, font=mono(12), fill=SUB)
        if i < 2:
            ax = x + bw + 1
            d.line([(ax, y0 + 55), (ax + 16, y0 + 55)], fill=LINE, width=2)
            d.polygon([(ax + 18, y0 + 55), (ax + 12, y0 + 51), (ax + 12, y0 + 59)], fill=LINE)

    watermark(d)
    img.save(os.path.join(OUT, "05_platforms.png"))
    print("[OK] 05_platforms")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
