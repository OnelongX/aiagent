# -*- coding: utf-8 -*-
"""5 images for Gemini / Google AI SDK 完整教程 · AI 工具栈 #08"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# Google / Gemini 主题 · 深蓝 + Google 四色
BG       = "#0a1428"
BOX      = "#15243f"
DEEP     = "#060d1c"
LINE     = "#1f3554"
WHITE    = "#ffffff"
SUB      = "#cfd9eb"
LIGHT    = "#94a3c4"
DIM      = "#5b6a87"
GBLUE    = "#4285f4"          # Google 蓝
GBLUE_L  = "#82b1ff"
GRED     = "#ea4335"
GRED_L   = "#f8a89c"
GYELLOW  = "#fbbc04"
GYELLOW_L= "#fde047"
GGREEN   = "#34a853"
GGREEN_L = "#6ee7b7"
PURPLE   = "#8b5cf6"
PURPLE_L = "#c084fc"
PINK     = "#ec4899"
PINK_L   = "#f9a8d4"
ORANGE   = "#fb923c"
ORANGE_L = "#fdba74"
CYAN     = "#22d3ee"
CYAN_L   = "#67e8f9"

REG  = r"C:\Windows\Fonts\msyh.ttc"
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
    return img, ImageDraw.Draw(img)


def watermark(d):
    d.text((W - 180, H - 32), "实战复盘", font=font(14), fill=DIM)


# ============ 01 HERO ============
def img_01():
    img, d = base()
    # 4 色 chip · Google 标志色
    colors = [GBLUE, GRED, GYELLOW, GGREEN]
    for i, c in enumerate(colors):
        rrect(d, [60 + i * 16, 50, 78 + i * 16, 88], 4, fill=c)
    rrect(d, [60 + 4 * 16 + 12, 50, 220 + 4 * 16, 88], 19, fill=BOX)
    d.text((78 + 4 * 16 + 12, 56), "实战复盘", font=font(20, bold=True), fill=WHITE)
    rrect(d, [320 + 4 * 16, 50, 540 + 4 * 16, 88], 19, fill=BOX)
    d.text((340 + 4 * 16, 56), "AI 工具栈 #08", font=font(17, bold=True), fill=GBLUE_L)

    d.text((60, 128), "Gemini / Google AI SDK", font=font(40, bold=True), fill=GBLUE_L)
    d.text((60, 184), "google-genai + ADK · 凑齐三家", font=font(24, bold=True), fill=WHITE)
    d.text((60, 222), "OpenAI / Claude / Gemini · 一个项目混搭", font=font(18), fill=SUB)

    chips = [
        ("2M 上下文",       GYELLOW_L,  "8 倍于 Claude/GPT"),
        ("原生多模态",      GGREEN_L,   "图 + 视 + 音 + PDF"),
        ("Google Search",   GBLUE_L,    "联网 grounding 自带源"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(14), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=GBLUE, width=2)
    d.text((80, 444), "学完三家 SDK · 才能真正落地任务 × 模型矩阵", font=font(20, bold=True), fill=GBLUE_L)
    d.text((80, 478), "国内 livetoken 一行 base_url · Gemini / GPT / Claude 全打通", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 三家对照 ============
def img_02():
    img, d = base()
    d.text((60, 40), "OpenAI / Claude / Gemini · 三家对照", font=font(26, bold=True), fill=GBLUE_L)
    d.text((60, 78), "学完三家 · 一个项目混搭 · 该谁强用谁", font=font(15), fill=LIGHT)

    # header
    y0 = 122
    rrect(d, [60, y0, 1020, y0 + 34], 8, fill=BOX)
    d.text((80,  y0 + 9), "维度",   font=font(14, bold=True), fill=WHITE)
    d.text((310, y0 + 9), "OpenAI", font=font(14, bold=True), fill=GGREEN_L)
    d.text((550, y0 + 9), "Claude", font=font(14, bold=True), fill=ORANGE_L)
    d.text((790, y0 + 9), "Gemini", font=font(14, bold=True), fill=GBLUE_L)

    # (axis, openai, claude, gemini, o_mono, c_mono, g_mono)
    rows = [
        ("Client SDK",  "openai",          "anthropic",         "google-genai",       True,  True,  True),
        ("Agent 框架",  "openai-agents",   "claude-agent-sdk",  "google-adk",         True,  True,  True),
        ("上下文",      "200k",            "200k",              "2M",                 True,  True,  True),
        ("多模态",      "后挂 · 图音",     "后挂 · 图 PDF",     "原生 4 模态",        False, False, False),
        ("联网",        "web_search",      "WebSearch",         "Google Search",      True,  True,  True),
        ("上下文缓存",  "Prompt Cache",    "Prompt Cache",      "Caches · 75% 折扣",  True,  True,  False),
        ("实时",        "Realtime API",    "无",                "Live API · 双流",    True,  False, False),
        ("Agent 原语",  "Agent + Handoff", "Subagent",          "Seq/Parallel/Loop",  True,  True,  True),
        ("守门",        "Guardrails",      "Hooks",             "Callbacks",          True,  True,  True),
        ("本地 Dev UI", "无",              "无",                "adk web",            False, False, True),
    ]
    for i, (axis, o, c, g, o_m, c_m, g_m) in enumerate(rows):
        y = y0 + 40 + i * 30
        rrect(d, [60, y, 1020, y + 26], 5, fill=DEEP)
        d.rectangle([60, y, 64, y + 26], fill=GBLUE)
        d.text((80,  y + 5), axis, font=font(13, bold=True),                  fill=WHITE)
        d.text((310, y + 5), o,    font=(mono(13) if o_m else font(13)),      fill=GGREEN_L)
        d.text((550, y + 5), c,    font=(mono(13) if c_m else font(13)),      fill=ORANGE_L)
        d.text((790, y + 5), g,    font=(mono(13) if g_m else font(13)),      fill=GBLUE_L)

    watermark(d)
    img.save(os.path.join(OUT, "02_compare.png"))
    print("[OK] 02_compare")


# ============ 03 8 大核心能力 ============
def img_03():
    img, d = base()
    d.text((60, 40), "Google AI SDK · 8 大核心能力", font=font(26, bold=True), fill=GBLUE_L)
    d.text((60, 78), "google-genai 7 + ADK 1 · 三个杀手锏标黄色", font=font(15), fill=LIGHT)

    caps = [
        ("①", "Generate Content",       "基础对话 / 流式 / 多轮 chat",                GBLUE_L),
        ("②", "Multimodal · 杀手锏",    "图 / 视频 / 音频 / PDF 原生四合一",          GYELLOW_L),
        ("③", "Files API",              "大文件上传 + 跨请求复用",                    GGREEN_L),
        ("④", "Function Calling",       "纯函数直传 · SDK 自动转 schema",             CYAN_L),
        ("⑤", "Structured Output",      "response_schema + Pydantic 直传",            PURPLE_L),
        ("⑥", "内置工具 · 杀手锏",       "Google Search / Code Exec / URL Context",   GYELLOW_L),
        ("⑦", "Caches API · 杀手锏",     "上下文缓存 75% 折 · RAG 必用",               GYELLOW_L),
        ("⑧", "Live API + ADK",         "实时 WebSocket 双流 · Agent 编排框架",       PINK_L),
    ]
    y0 = 116
    for i, (n, name, desc, c) in enumerate(caps):
        y = y0 + i * 54
        rrect(d, [60, y, 1020, y + 46], 8, fill=BOX, outline=c, width=2)
        d.rectangle([60, y, 64, y + 46], fill=c)
        d.text((80, y + 6), n, font=font(20, bold=True), fill=c)
        d.text((120, y + 6), name, font=font(15, bold=True), fill=WHITE)
        d.text((120, y + 26), desc, font=font(12), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "03_capabilities.png"))
    print("[OK] 03_capabilities")


# ============ 04 ADK 5 个 Agent 原语 ============
def img_04():
    img, d = base()
    d.text((60, 40), "ADK · 5 种 Agent 编排原语", font=font(26, bold=True), fill=GBLUE_L)
    d.text((60, 78), "比 OpenAI / Claude 多一层 · 适合复杂工作流", font=font(15), fill=LIGHT)

    # (name, desc, eq, color)
    concepts = [
        ("LlmAgent",        "单个 LLM · instruction + tools + output_key", "= OpenAI Agent",          GBLUE_L),
        ("SequentialAgent", "串行多 Agent · A 跑完跑 B · 共享 session",     "OpenAI 没有 · 用 Handoff", GGREEN_L),
        ("ParallelAgent",   "并行多 Agent · 同时跑 · 取结果",               "OpenAI 没有",              GYELLOW_L),
        ("LoopAgent",       "循环执行直到达成条件 · max_iterations",         "OpenAI 没有",              PURPLE_L),
        ("Tool",            "函数 / 内置 / Agent-as-Tool",                  "= function_tool",          PINK_L),
    ]
    y0 = 124
    for i, (name, desc, eq, c) in enumerate(concepts):
        y = y0 + i * 70
        rrect(d, [60, y, 1020, y + 60], 12, fill=BOX, outline=c, width=2)
        rrect(d, [80, y + 10, 320, y + 50], 8, fill=c)
        d.text((96, y + 18), name, font=font(18, bold=True), fill=BG)
        d.text((350, y + 10), desc, font=font(14, bold=True), fill=WHITE)
        d.text((350, y + 34), eq,   font=font(13),            fill=SUB)

    rrect(d, [60, 488, 1020, 528], 8, fill=DEEP, outline=GBLUE, width=1)
    d.text((80, 500), "+ adk web 本地可视化调试 · 不依赖云 Tracing", font=font(13, bold=True), fill=GBLUE_L)

    watermark(d)
    img.save(os.path.join(OUT, "04_adk.png"))
    print("[OK] 04_adk")


# ============ 05 三家组合落地场景 ============
def img_05():
    img, d = base()
    d.text((60, 40), "三家 SDK · 组合落地场景", font=font(26, bold=True), fill=GBLUE_L)
    d.text((60, 78), "不是二选一三选一 · 是该谁强用谁 · 一层 LiteLLM 封装", font=font(15), fill=LIGHT)

    scenarios = [
        ("知识库 RAG · 长文档",      GYELLOW_L, "Gemini Caches",  "Claude 回答",      "GPT strict 提取"),
        ("客服 Agent",               GGREEN_L,  "Flash-Lite 分诊", "Claude 共情",      "GPT JSON 工单"),
        ("医疗影像 + 报告",          PINK_L,    "Gemini 影像",     "Claude 报告语言",  "GPT strict 结构"),
        ("法律合同审查",             PURPLE_L,  "Gemini PDF 全文", "Claude 漏判",      "GPT strict 风险"),
        ("工厂 MES + 工艺推荐",      ORANGE_L,  "Gemini 工艺手册", "Claude 推荐文",    "GPT 数字结构化"),
        ("自媒体 + 多平台分发",      CYAN_L,    "Gemini 视频生成", "Claude 主笔",      "GPT 封面图"),
    ]

    # header
    y0 = 122
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80,  y0 + 8), "场景",   font=font(14, bold=True), fill=WHITE)
    d.text((380, y0 + 8), "Gemini", font=font(14, bold=True), fill=GBLUE_L)
    d.text((600, y0 + 8), "Claude", font=font(14, bold=True), fill=ORANGE_L)
    d.text((830, y0 + 8), "OpenAI", font=font(14, bold=True), fill=GGREEN_L)

    for i, (scene, c, g, cl, o) in enumerate(scenarios):
        y = y0 + 38 + i * 50
        rrect(d, [60, y, 1020, y + 44], 8, fill=BOX, outline=c, width=2)
        d.rectangle([60, y, 64, y + 44], fill=c)
        d.text((80,  y + 13), scene, font=font(14, bold=True), fill=WHITE)
        d.text((380, y + 13), g,     font=font(13),            fill=GBLUE_L)
        d.text((600, y + 13), cl,    font=font(13),            fill=ORANGE_L)
        d.text((830, y + 13), o,     font=font(13),            fill=GGREEN_L)

    watermark(d)
    img.save(os.path.join(OUT, "05_combo.png"))
    print("[OK] 05_combo")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
