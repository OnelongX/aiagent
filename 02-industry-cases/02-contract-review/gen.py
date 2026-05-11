# -*- coding: utf-8 -*-
"""5 images for 合同审查助手 - Claude+Gemini+GPT 多模型协作"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\合同审查助手"
W, H = 1080, 600

BG = "#0f172a"
BOX = "#1e293b"
DEEP = "#0b1220"
LINE = "#334155"
WHITE = "#ffffff"
SUB = "#cbd5e1"
LIGHT = "#94a3b8"
DIM = "#64748b"
WHITE_DIM = "#e2e8f0"
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
ORANGE = "#fb923c"
PINK = "#ec4899"
LIME = "#84cc16"
TEAL = "#14b8a6"

# 三模型颜色
CLAUDE_C = "#fb923c"   # orange
GEMINI_C = "#60a5fa"   # blue
GPT_C    = "#4ade80"   # green

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

    rrect(d, [60, 50, 240, 88], 19, fill=PURPLE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 506, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 · 行业落地", font=font(17, bold=True), fill=AMBER)

    d.text((60, 130), "合同审查助手", font=font(40, bold=True), fill=AMBER)
    d.text((60, 184), "Claude + Gemini + GPT", font=font(26, bold=True), fill=WHITE)
    d.text((60, 220), "多模型协作实战", font=font(26, bold=True), fill=WHITE)

    # 3 model chips
    chips = [
        ("Claude", CLAUDE_C, "深度推理 / 修订"),
        ("Gemini", GEMINI_C, "扫描件 / 长文"),
        ("GPT",    GPT_C,    "JSON 结构化"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    # bottom — key data
    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=GREEN, width=2)
    d.text((80, 442), "漏判率 15% → < 2%", font=font(22, bold=True), fill=GREEN_LIGHT)
    d.text((80, 478), "成本仅为三模型全跑的 47% · 法务可用级别", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 三模型分工 ============
def img_02():
    img, d = base()
    d.text((60, 40), "三模型任务分配", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "别用一个模型干所有事 · 各家结构性优势不同", font=font(15), fill=LIGHT)

    rows = [
        ("扫描件 / 多模态", "Gemini 2.5 Pro", "原生多模态 + 2M context",   GEMINI_C),
        ("条款结构化抽取", "GPT-4.1",         "JSON mode · schema 不漂",   GPT_C),
        ("风险推理 + 修订", "Claude Opus 4.5", "法律语言精准 · 深度推理",   CLAUDE_C),
        ("红线匹配",       "(不用 LLM)",     "规则 + 向量召回 · 快 100×", LIGHT),
        ("终审交叉验证",   "三模型并发",       "投票 · disagree 升人工",    PINK),
    ]
    y0 = 130
    rrect(d, [60, y0, 1020, y0 + 36], 8, fill=BOX)
    d.text((80, y0 + 9), "任务", font=font(15, bold=True), fill=AMBER)
    d.text((310, y0 + 9), "首选模型", font=font(15, bold=True), fill=AMBER)
    d.text((600, y0 + 9), "原因", font=font(15, bold=True), fill=AMBER)

    for i, (task, model, why, c) in enumerate(rows):
        y = y0 + 50 + i * 70
        rrect(d, [60, y, 1020, y + 56], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 56], fill=c)
        d.text((80, y + 18), task, font=font(16, bold=True), fill=WHITE)
        d.text((310, y + 18), model, font=mono(15), fill=c)
        d.text((600, y + 18), why, font=font(14), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "02_models.png"))
    print("[OK] 02_models")


# ============ 03: 整体架构 ============
def img_03():
    img, d = base()
    d.text((60, 40), "整体架构", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "Claude Agent SDK 当 orchestrator · 异厂模型包成 tool", font=font(15), fill=LIGHT)

    # input
    rrect(d, [420, 110, 660, 158], 12, fill=BLUE)
    d.text((448, 122), "合同 PDF / 扫描件", font=font(18, bold=True), fill=WHITE)

    d.line([(540, 160), (540, 188)], fill=LINE, width=2)
    d.polygon([(540, 196), (534, 188), (546, 188)], fill=LINE)

    # main agent
    rrect(d, [380, 200, 700, 264], 12, fill=BOX, outline=AMBER, width=2)
    d.text((408, 213), "主 Agent (Claude SDK)", font=font(19, bold=True), fill=AMBER)
    d.text((408, 240), "orchestrator · 调度 5 段 Subagent", font=font(13), fill=SUB)

    # 5 subagents
    sub_y = 310
    subs = [
        ("ingester",      "Gemini",       GEMINI_C),
        ("extractor",     "GPT",          GPT_C),
        ("risk-team",     "Claude×3 交叉", PINK),
        ("reviser",       "Claude",       CLAUDE_C),
        ("report-writer", "Markdown",     PURPLE_LIGHT),
    ]
    col_w = 188
    for i, (name, model, c) in enumerate(subs):
        x = 60 + i * (col_w + 8)
        d.line([(540, 266), (x + col_w // 2, 302)], fill=LINE, width=1)
        rrect(d, [x, sub_y, x + col_w, sub_y + 88], 10, fill=BOX, outline=c, width=2)
        d.text((x + 12, sub_y + 14), name, font=mono(14), fill=c)
        d.text((x + 12, sub_y + 42), model, font=font(14, bold=True), fill=WHITE)
        d.text((x + 12, sub_y + 64), f"step {i+1}", font=font(11), fill=DIM)

    # bottom — output
    rrect(d, [60, 432, 1020, 510], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((80, 448), "审查报告 · 风险清单 · 修订对照 · 人工介入项", font=font(17, bold=True), fill=GREEN_LIGHT)
    d.text((80, 478), "整体定级 / 高危条款 / 三模型分歧记录", font=font(13), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_architecture.png"))
    print("[OK] 03_architecture")


# ============ 04: 8 个工具 ============
def img_04():
    img, d = base()
    d.text((60, 40), "8 个核心工具", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "三家模型包成 SDK tool · 主 Agent 当调度员", font=font(15), fill=LIGHT)

    tools = [
        ("parse_contract",   "Gemini",    "PDF / 扫描件 → 文本",   GEMINI_C),
        ("summarize_full",   "Gemini",    "整份合同摘要 + 定级",   GEMINI_C),
        ("extract_clauses",  "GPT",       "条款切分 JSON",         GPT_C),
        ("match_redlines",   "Rules",     "红线条款向量召回",      LIGHT),
        ("risk_analyze",     "Claude",    "单条款风险评级",        CLAUDE_C),
        ("cross_verify",     "三模型",     "并发打分 + 投票",       PINK),
        ("draft_revision",   "Claude",    "起草修订 diff",         CLAUDE_C),
        ("write_report",     "I/O",       "落 Markdown 报告",      PURPLE_LIGHT),
    ]
    y0 = 130
    # 2 columns
    for i, (name, who, desc, c) in enumerate(tools):
        col = i % 2
        row = i // 2
        x = 60 + col * 490
        y = y0 + row * 92
        rrect(d, [x, y, x + 472, y + 78], 10, fill=BOX, outline=c, width=2)
        d.text((x + 16, y + 12), name, font=mono(15), fill=c)
        # model badge
        bw = tw(d, who, font(12, bold=True)) + 16
        rrect(d, [x + 472 - bw - 12, y + 12, x + 472 - 12, y + 34], 10, fill=c)
        d.text((x + 472 - bw - 4, y + 14), who, font=font(12, bold=True), fill=BG)
        d.text((x + 16, y + 44), desc, font=font(15), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_tools.png"))
    print("[OK] 04_tools")


# ============ 05: 一次真实运行 ============
def img_05():
    img, d = base()
    d.text((60, 40), "一次真实运行", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "SaaS 服务合同 v3 · 45 页 · 客户方视角", font=font(15), fill=LIGHT)

    # left — input
    rrect(d, [60, 116, 460, 188], 12, fill=DEEP, outline=BLUE, width=2)
    d.text((80, 128), "输入", font=font(15, bold=True), fill=BLUE)
    d.text((80, 152), "审查 saas_agreement_v3.pdf", font=mono(13), fill=SUB)
    d.text((80, 168), "重点:数据所有权 / SLA / 续约", font=font(13), fill=SUB)

    # arrow
    d.line([(478, 152), (510, 152)], fill=AMBER, width=3)
    d.polygon([(518, 152), (508, 146), (508, 158)], fill=AMBER)

    # right — overall
    rrect(d, [528, 116, 1020, 188], 12, fill=DEEP, outline=RED, width=2)
    d.text((548, 128), "整体定级", font=font(15, bold=True), fill=RED)
    d.text((548, 152), "HIGH", font=font(22, bold=True), fill=RED)
    d.text((628, 158), "不建议直接签 · 需要谈判后再签", font=font(13), fill=SUB)

    # 6 high-risk clauses table
    d.text((60, 212), "6 条高危条款", font=font(17, bold=True), fill=AMBER)
    clauses = [
        ("#7",  "数据所有权",   "CRITICAL", RED),
        ("#12", "SLA 赔付上限", "HIGH",     AMBER_DEEP),
        ("#19", "自动续约",     "HIGH",     AMBER_DEEP),
        ("#23", "单方调价权",   "HIGH",     AMBER_DEEP),
        ("#28", "责任限额",     "MEDIUM",   AMBER),
        ("#31", "仲裁地",       "MEDIUM",   AMBER),
    ]
    y0 = 246
    for i, (cid, title, level, c) in enumerate(clauses):
        col = i % 2
        row = i // 2
        x = 60 + col * 490
        y = y0 + row * 50
        rrect(d, [x, y, x + 472, y + 42], 8, fill=BOX)
        d.text((x + 14, y + 12), cid, font=mono(15), fill=DIM)
        d.text((x + 66, y + 12), title, font=font(15, bold=True), fill=WHITE)
        bw = tw(d, level, font(12, bold=True)) + 14
        rrect(d, [x + 472 - bw - 10, y + 11, x + 472 - 10, y + 31], 10, fill=c)
        d.text((x + 472 - bw - 3, y + 13), level, font=font(12, bold=True), fill=BG)

    # bottom — call stats
    rrect(d, [60, 416, 1020, 510], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((80, 430), "调用统计", font=font(15, bold=True), fill=GREEN)
    stats = [
        ("Gemini", "2 次",    GEMINI_C),
        ("GPT",    "1 次",    GPT_C),
        ("Claude", "47 次",   CLAUDE_C),
        ("交叉验证", "8 次",   PINK),
        ("总成本",  "¥3.2",   GREEN_LIGHT),
    ]
    for i, (k, v, c) in enumerate(stats):
        x = 80 + i * 190
        d.text((x, 458), k, font=font(12), fill=DIM)
        d.text((x, 478), v, font=font(20, bold=True), fill=c)

    watermark(d)
    img.save(os.path.join(OUT, "05_walkthrough.png"))
    print("[OK] 05_walkthrough")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
