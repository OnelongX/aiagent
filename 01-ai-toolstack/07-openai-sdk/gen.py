# -*- coding: utf-8 -*-
"""5 images for OpenAI SDK 完整教程 · AI 工具栈 #07"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# OpenAI 主题 · 黑 + 翠绿(品牌色)
BG       = "#0a1612"
BOX      = "#13231d"
DEEP     = "#050b09"
LINE     = "#1f3a30"
WHITE    = "#ffffff"
SUB      = "#cfe8de"
LIGHT    = "#86b5a4"
DIM      = "#56756a"
TEAL     = "#10a37f"          # OpenAI 招牌绿
TEAL_L   = "#1ec891"
TEAL_D   = "#0b7560"
MINT     = "#34d399"
EMERALD  = "#10b981"
LIME     = "#a3e635"
CYAN     = "#22d3ee"
BLUE     = "#60a5fa"
INDIGO   = "#818cf8"
PURPLE   = "#c084fc"
PINK     = "#f472b6"
ROSE     = "#fb7185"
ORANGE   = "#fb923c"
ORANGE_L = "#fdba74"
AMBER    = "#fbbf24"
AMBER_L  = "#fde047"
RED      = "#ef4444"
RED_L    = "#fca5a5"

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
    rrect(d, [60, 50, 240, 88], 19, fill=TEAL)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 #07", font=font(17, bold=True), fill=TEAL_L)

    d.text((60, 128), "OpenAI SDK 完整教程", font=font(40, bold=True), fill=TEAL_L)
    d.text((60, 184), "Chat Completions → Responses → Agents SDK", font=font(22, bold=True), fill=WHITE)
    d.text((60, 222), "三件套 · 8 大核心能力 · Python + TS 双语", font=font(18), fill=SUB)

    chips = [
        ("Responses API",   AMBER_L,  "2025/3 推出 · 替代旧 API"),
        ("Agents SDK",      MINT,     "官方 Agent 编排框架"),
        ("Strict JSON",     CYAN,     "100% schema 输出"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(14), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=TEAL, width=2)
    d.text((80, 444), "学完能切换 OpenAI / Claude SDK · 1 分钟上手", font=font(20, bold=True), fill=TEAL_L)
    d.text((80, 478), "国内 livetoken 一行 base_url · 280+ 模型同 endpoint", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 OPENAI vs CLAUDE 对照 ============
def img_02():
    img, d = base()
    d.text((60, 40), "OpenAI vs Claude · SDK 对照", font=font(26, bold=True), fill=TEAL_L)
    d.text((60, 78), "两家设计哲学不同 · 一张图看懂", font=font(15), fill=LIGHT)

    # 标记每行的两个字段是否为纯英文(用 mono),含中文用 font
    # (axis, openai, claude, openai_is_mono, claude_is_mono)
    rows = [
        ("Client SDK",    "openai",                                    "anthropic",                          True,  True),
        ("Agent 框架",    "openai-agents",                             "claude-agent-sdk",                   True,  True),
        ("状态管理",      "服务端(Responses)",                        "客户端(session)",                    False, False),
        ("内置工具",      "web_search/file_search/code_interpreter",   "Read/Write/Edit/Bash/WebSearch +",   True,  True),
        ("多 Agent",      "Handoff · 转移",                            "Subagent · 嵌套",                    False, False),
        ("守门",          "Guardrails · class",                        "Hooks · callback",                   False, False),
        ("结构化输出",    "strict=True · 100%",                        "JSON mode · 软约束",                 False, False),
        ("Tracing",       "内置 · 自动上传",                           "需第三方 · LangSmith",               False, False),
        ("代码 / shell",  "code_interpreter",                          "Bash + 10 种内置 · 更全",             False, False),
        ("中转 endpoint", "OPENAI_BASE_URL",                           "ANTHROPIC_BASE_URL",                 True,  True),
    ]

    # header
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80,  y0 + 8), "维度",   font=font(14, bold=True), fill=TEAL_L)
    d.text((430, y0 + 8), "OpenAI", font=font(14, bold=True), fill=AMBER_L)
    d.text((760, y0 + 8), "Claude", font=font(14, bold=True), fill=ORANGE_L)

    for i, (axis, o, c, o_mono, c_mono) in enumerate(rows):
        y = y0 + 38 + i * 33
        rrect(d, [60, y, 1020, y + 28], 6, fill=DEEP)
        d.rectangle([60, y, 64, y + 28], fill=TEAL)
        d.text((80,  y + 6), axis, font=font(13, bold=True),                    fill=WHITE)
        d.text((430, y + 6), o,    font=(mono(13) if o_mono else font(13)),     fill=AMBER_L)
        d.text((760, y + 6), c,    font=(mono(13) if c_mono else font(13)),     fill=ORANGE_L)

    watermark(d)
    img.save(os.path.join(OUT, "02_compare.png"))
    print("[OK] 02_compare")


# ============ 03 8 大核心能力 ============
def img_03():
    img, d = base()
    d.text((60, 40), "OpenAI SDK · 8 大核心能力", font=font(26, bold=True), fill=TEAL_L)
    d.text((60, 78), "Client SDK 7 + Agents SDK 1 · 全面覆盖", font=font(15), fill=LIGHT)

    caps = [
        ("①", "Chat Completions",    "兼容性最强 · 旧 API · 第三方 endpoint 必备",   AMBER_L),
        ("②", "Responses API",       "新 API · 服务端 state · 多模态统一",          MINT),
        ("③", "Function Calling",    "自定义工具 · LLM 自动选 · 你跑函数",          CYAN),
        ("④", "Structured Outputs",  "strict=True · Pydantic 直传 · 100% schema",  BLUE),
        ("⑤", "Vision",              "图 / PDF 直接传 · 不用 OCR",                 PURPLE),
        ("⑥", "Embeddings",          "text-embedding-3-large · 英文 OK",            INDIGO),
        ("⑦", "Audio",               "TTS / Whisper / Realtime API",               PINK),
        ("⑧", "Agents SDK",          "Agent / Runner / Handoff / Guardrail / Tracing", TEAL_L),
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


# ============ 04 Agents SDK · 5 个核心概念 ============
def img_04():
    img, d = base()
    d.text((60, 40), "Agents SDK · 5 个核心概念", font=font(26, bold=True), fill=TEAL_L)
    d.text((60, 78), "Agent / Runner / Tool / Handoff / Guardrail", font=font(15), fill=LIGHT)

    # (name, desc, eq, eq_is_mono, color)
    concepts = [
        ("Agent",     "instructions + tools + model",       "约等于 Subagent",      False, MINT),
        ("Runner",    "跑 Agent · 自动循环",                 "约等于 query()",       False, BLUE),
        ("Tool",      "@function_tool 自动 schema",          "约等于 function_call", False, AMBER_L),
        ("Handoff",   "Agent 之间转移控制权",                "约等于 转人工但转 AI", False, PURPLE),
        ("Guardrail", "输入 / 输出守门 · 触发 tripwire",     "约等于 Hooks",         False, RED_L),
    ]
    y0 = 124
    for i, (name, desc, eq, eq_mono, c) in enumerate(concepts):
        y = y0 + i * 72
        rrect(d, [60, y, 1020, y + 60], 12, fill=BOX, outline=c, width=2)
        # name 大字
        rrect(d, [80, y + 10, 260, y + 50], 8, fill=c)
        d.text((96, y + 18), name, font=font(20, bold=True), fill=BG)
        # desc
        d.text((290, y + 10), desc, font=font(15, bold=True), fill=WHITE)
        d.text((290, y + 34), eq,   font=(mono(13) if eq_mono else font(13)), fill=SUB)

    rrect(d, [60, 488, 1020, 528], 8, fill=DEEP, outline=TEAL, width=1)
    d.text((80, 500), "+ Tracing 自动可观测 · platform.openai.com/traces 看执行链", font=font(13, bold=True), fill=TEAL_L)

    watermark(d)
    img.save(os.path.join(OUT, "04_agents_sdk.png"))
    print("[OK] 04_agents_sdk")


# ============ 05 Python + TypeScript 双语 ============
def img_05():
    img, d = base()
    d.text((60, 40), "Python + TypeScript 双语对照", font=font(26, bold=True), fill=TEAL_L)
    d.text((60, 78), "90% API 同形 · 区别只在语法", font=font(15), fill=LIGHT)

    # 左右 panel
    py_x, ts_x = 60, 560
    panel_w = 460
    panel_y = 116
    panel_h = 380

    # Python panel
    rrect(d, [py_x, panel_y, py_x + panel_w, panel_y + panel_h], 12, fill=BOX, outline=AMBER_L, width=2)
    d.text((py_x + 20, panel_y + 14), "Python · openai-agents", font=font(16, bold=True), fill=AMBER_L)
    py_code = [
        "from agents import Agent, Runner,",
        "    function_tool",
        "",
        "@function_tool",
        "def add(a: int, b: int) -> int:",
        '    """两数相加"""',
        "    return a + b",
        "",
        "agent = Agent(",
        '    name="算术",',
        "    tools=[add],",
        '    model="gpt-5",',
        ")",
        "",
        'result = Runner.run_sync(',
        '    agent, "3 加 5")',
        "print(result.final_output)",
    ]
    for i, line in enumerate(py_code):
        d.text((py_x + 20, panel_y + 50 + i * 19), line, font=mono(13), fill=SUB)

    # TS panel
    rrect(d, [ts_x, panel_y, ts_x + panel_w, panel_y + panel_h], 12, fill=BOX, outline=CYAN, width=2)
    d.text((ts_x + 20, panel_y + 14), "TypeScript · @openai/agents", font=font(16, bold=True), fill=CYAN)
    ts_code = [
        'import { Agent, run, tool }',
        '    from "@openai/agents";',
        'import { z } from "zod";',
        "",
        "const add = tool({",
        '  name: "add",',
        "  parameters: z.object({",
        "    a: z.number(), b: z.number()",
        "  }),",
        "  execute: async ({a,b}) => a + b,",
        "});",
        "",
        'const agent = new Agent({',
        '  name: "算术", tools: [add],',
        '  model: "gpt-5",',
        "});",
        "",
        'const r = await run(agent, "3 加 5");',
    ]
    for i, line in enumerate(ts_code):
        d.text((ts_x + 20, panel_y + 50 + i * 19), line, font=mono(13), fill=SUB)

    # 底部
    rrect(d, [60, 520, 1020, 558], 8, fill=DEEP, outline=TEAL, width=1)
    d.text((80, 530), "两端 API 形态一致 · 跨栈复用同一套设计", font=font(13, bold=True), fill=TEAL_L)

    watermark(d)
    img.save(os.path.join(OUT, "05_dual_lang.png"))
    print("[OK] 05_dual_lang")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
