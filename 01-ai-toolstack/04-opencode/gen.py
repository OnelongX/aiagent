# -*- coding: utf-8 -*-
"""5 images for opencode 配置教程 - 1080x600"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\opencode配置教程"
W, H = 1080, 600

BG = "#0f172a"
BOX = "#1e293b"
DEEP = "#0b1220"
LINE = "#334155"
WHITE = "#ffffff"
SUB = "#cbd5e1"
LIGHT = "#94a3b8"
DIM = "#64748b"
TEAL = "#14b8a6"
TEAL_LIGHT = "#5eead4"
AMBER = "#fbbf24"
AMBER_DEEP = "#f59e0b"
RED = "#ef4444"
GREEN = "#22c55e"
PURPLE = "#a855f7"
BLUE = "#3b82f6"
PINK = "#ec4899"
CYAN = "#06b6d4"
ORANGE = "#fb923c"
LIME = "#84cc16"

REG = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
MONO = r"C:\Windows\Fonts\consola.ttf"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def mono(size, bold=False):
    try:
        return ImageFont.truetype(MONO, size)
    except Exception:
        return font(size, bold)


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


# ============ 01: HERO - opencode 概览 ============
def img_01():
    img, d = base()

    rrect(d, [60, 50, 240, 88], 19, fill=LIME)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)

    rrect(d, [256, 50, 460, 88], 19, fill=BOX)
    d.text((274, 56), "AI 编程工具栈 · 3/3", font=font(18, bold=True), fill=AMBER)

    d.text((60, 130), "opencode 配置完整教程", font=font(36, bold=True), fill=AMBER)
    d.text((60, 178), "开源 AI 编程 CLI · 一个工具跑遍 75+ 模型", font=font(20, bold=True), fill=WHITE)
    d.text((60, 220), "Codex + Claude Code + opencode = 工具栈三件套", font=font(15), fill=LIGHT)

    items = [
        ("75+", "模型 / Provider", "AI SDK 全覆盖", LIME),
        ("100%", "开源", "Go 实现 · 可审计", GREEN),
        ("多端", "TUI / CLI / IDE", "终端 + 桌面 + 扩展", PURPLE),
        ("通用", "不绑厂商", "OpenAI 兼容自动适配", AMBER),
    ]

    by = 270
    bw = (W - 120 - 60) // 4
    bh = 230

    for i, (num, label, sub, color) in enumerate(items):
        x = 60 + i * (bw + 20)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)
        f_big = font(40, bold=True)
        num_w = tw(d, num, f_big)
        d.text((x + (bw - num_w) // 2, by + 36), num, font=f_big, fill=color)
        f_lbl = font(15, bold=True)
        lbl_w = tw(d, label, f_lbl)
        d.text((x + (bw - lbl_w) // 2, by + 100), label, font=f_lbl, fill=WHITE)
        d.line([(x + 22, by + 132), (x + bw - 22, by + 132)], fill=LINE, width=1)
        f_sub = font(12)
        sub_w = tw(d, sub, f_sub)
        d.text((x + (bw - sub_w) // 2, by + 150), sub, font=f_sub, fill=LIGHT)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "杀招:一个 livetoken token 跑 Codex + Claude Code + opencode", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))


# ============ 02: 3 引擎对比 ============
def img_02():
    img, d = base()

    d.text((60, 40), "AI 编程工具栈 · 3 引擎对比", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "Codex / Claude Code / opencode 各自定位", font=font(15), fill=LIGHT)

    # Header
    hy = 130
    rrect(d, [60, hy, W - 60, hy + 38], 6, fill=DEEP)
    d.text((76, hy + 9), "维度", font=font(13, bold=True), fill=AMBER)
    d.text((280, hy + 9), "Codex", font=font(13, bold=True), fill=BLUE)
    d.text((520, hy + 9), "Claude Code", font=font(13, bold=True), fill=ORANGE)
    d.text((780, hy + 9), "opencode", font=font(13, bold=True), fill=LIME)

    rows = [
        ("厂商", "OpenAI", "Anthropic", "sst.dev / 社区"),
        ("开源", "✗ 闭源", "✗ 闭源", "✓ 开源(Go)"),
        ("主要模型", "GPT 系列", "Claude 系列", "75+ provider"),
        ("协议", "Responses API", "Messages API", "OpenAI 兼容"),
        ("自定义 provider", "单 provider", "单 provider", "多 provider 共存"),
        ("最强场景", "VS Code 内嵌", "Plan + Subagent", "多模型 + 本地"),
    ]

    ry = hy + 48
    rh = 55
    for i, (k, c, cc, oc) in enumerate(rows):
        bg = BOX if i % 2 == 0 else DEEP
        rrect(d, [60, ry, W - 60, ry + rh - 4], 6, fill=bg)
        d.text((76, ry + 16), k, font=font(13, bold=True), fill=AMBER)
        d.text((280, ry + 16), c, font=font(13), fill=WHITE)
        d.text((520, ry + 16), cc, font=font(13), fill=WHITE)
        is_open = "✓" in oc
        d.text((780, ry + 16), oc, font=font(13, bold=True), fill=GREEN if is_open else LIME)
        ry += rh

    # bottom
    rrect(d, [60, ry + 6, W - 60, ry + 60], 8, fill=DEEP, outline=LIME, width=2)
    d.text((80, ry + 22), "opencode 最大特点 = 通用 · 不绑特定厂商", font=font(15, bold=True), fill=LIME)

    watermark(d)
    img.save(os.path.join(OUT, "02_compare.png"))


# ============ 03: 自定义 provider 配置 ============
def img_03():
    img, d = base()

    d.text((60, 40), "自定义 Provider · 通用模板", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "@ai-sdk/openai-compatible · 接入任何 OpenAI 兼容服务", font=font(15), fill=LIGHT)

    # Code block
    cy = 130
    rrect(d, [60, cy, W - 60, cy + 280], 12, fill=DEEP, outline=PURPLE, width=2)
    d.rectangle([60, cy, 68, cy + 280], fill=PURPLE)

    # Mac dots
    d.ellipse([85, cy + 16, 93, cy + 24], fill="#ff5f56")
    d.ellipse([99, cy + 16, 107, cy + 24], fill="#ffbd2e")
    d.ellipse([113, cy + 16, 121, cy + 24], fill="#27c93f")
    d.text((140, cy + 14), "~/.config/opencode/opencode.json", font=mono(13, bold=True), fill=PURPLE)

    code = [
        ('  "provider": {', WHITE),
        ('    "livetoken": {', WHITE),
        ('      "npm": "@ai-sdk/openai-compatible",', GREEN),
        ('      "name": "Livetoken",', GREEN),
        ('      "options": {', WHITE),
        ('        "baseURL": "https://livetoken.top",', AMBER),
        ('        "apiKey": "{env:LIVETOKEN_API_KEY}"', AMBER),
        ('      },', WHITE),
        ('      "models": {', WHITE),
        ('        "gpt-5.5":         { "name": "GPT-5.5" },', LIME),
        ('        "claude-sonnet-4": { "name": "Claude Sonnet 4" },', LIME),
        ('        "deepseek-r1":     { "name": "DeepSeek R1" }', LIME),
        ('      }', WHITE),
        ('    }', WHITE),
        ('  }', WHITE),
    ]
    for i, (line, color) in enumerate(code):
        d.text((85, cy + 50 + i * 16), line, font=mono(11), fill=color)

    # 3 关键参数
    by = 430
    items = [
        ("npm", "永远填 @ai-sdk/openai-compatible", BLUE),
        ("baseURL", "第三方 endpoint 根 URL · 不带 /v1", AMBER),
        ("models", "声明可见模型清单 · /model 命令切换", LIME),
    ]
    for i, (k, v, color) in enumerate(items):
        y = by + i * 32
        rrect(d, [60, y, W - 60, y + 28], 6, fill=BOX)
        d.rectangle([60, y, 66, y + 28], fill=color)
        d.text((76, y + 6), k, font=mono(13, bold=True), fill=color)
        d.text((220, y + 6), v, font=font(13), fill=WHITE)

    watermark(d)
    img.save(os.path.join(OUT, "03_provider.png"))


# ============ 04: 多模型聚合实战 ============
def img_04():
    img, d = base()

    d.text((60, 40), "多模型聚合 · 一个 provider 7 个模型", font=font(26, bold=True), fill=WHITE)
    d.text((60, 84), "TUI 内 /model 命令 · 任意切换", font=font(15), fill=LIGHT)

    # Models list panel
    items = [
        ("01", "gpt-5.5", "GPT-5.5", "OpenAI · 主力", BLUE),
        ("02", "gpt-5", "GPT-5", "OpenAI · 推理", BLUE),
        ("03", "claude-sonnet-4", "Claude Sonnet 4", "Anthropic · 重构", ORANGE),
        ("04", "claude-opus-4", "Claude Opus 4", "Anthropic · 复杂任务", ORANGE),
        ("05", "gemini-2.5-pro", "Gemini 2.5 Pro", "Google · 长上下文", AMBER),
        ("06", "deepseek-r1", "DeepSeek R1", "DeepSeek · 推理便宜", PURPLE),
        ("07", "qwen-3-coder", "Qwen3 Coder", "阿里 · 代码专项", LIME),
    ]

    by = 130
    bh = 50
    spacing = 5

    for i, (num, model_id, name, role, color) in enumerate(items):
        y = by + i * (bh + spacing)
        rrect(d, [60, y, W - 60, y + bh], 8, fill=BOX)
        d.rectangle([60, y, 66, y + bh], fill=color)
        d.text((80, y + 14), num, font=font(15, bold=True), fill=color)
        d.text((130, y + 14), model_id, font=mono(13, bold=True), fill=GREEN)
        d.text((430, y + 14), name, font=font(14, bold=True), fill=WHITE)
        d.text((720, y + 14), role, font=font(12), fill=LIGHT)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "1 个 livetoken token · 7 个模型 · /model 命令切换", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "04_multimodel.png"))


# ============ 05: 安装 → 配置 → 启动 走完整流程 ============
def img_05():
    img, d = base()

    d.text((60, 40), "opencode 配置 · 4 步走完整流程", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "5 分钟搞定 · 一个 token 跑遍 75+ 模型", font=font(15), fill=LIGHT)

    panels = [
        ("STEP 1", "安装 opencode",
         "$ brew install \\\n    anomalyco/tap/opencode\n\n$ opencode --version\nopencode 1.0.0",
         BLUE),
        ("STEP 2", "编辑 opencode.json",
         '$ mkdir -p ~/.config/opencode\n$ vim opencode.json\n\n{\n  "$schema": "...",\n  "model": "livetoken/gpt-5.5",\n  "provider": { ... }\n}',
         PURPLE),
        ("STEP 3", "设置 API Key",
         '$ export \\\n  LIVETOKEN_API_KEY="sk-xxx"\n\n$ source ~/.zshrc\n$ echo $LIVETOKEN_API_KEY\nsk-xxx',
         AMBER),
        ("STEP 4", "启动 + 切换模型",
         '$ cd ~/my-project\n$ opencode\n\n[opencode TUI]\n> /model\n> claude-sonnet-4\n> 帮我重构 utils.py\n✓ Done',
         LIME),
    ]

    pw = (W - 120 - 30) // 2
    ph = 200
    by = 130
    spacing_x = 30
    spacing_y = 20

    for i, (step, title, code, color) in enumerate(panels):
        x = 60 + (i % 2) * (pw + spacing_x)
        y = by + (i // 2) * (ph + spacing_y)

        rrect(d, [x, y, x + pw, y + ph], 12, fill=BOX, outline=color, width=2)
        d.rectangle([x, y, x + 8, y + ph], fill=color)

        # Mac dots
        d.ellipse([x + 22, y + 14, x + 30, y + 22], fill="#ff5f56")
        d.ellipse([x + 36, y + 14, x + 44, y + 22], fill="#ffbd2e")
        d.ellipse([x + 50, y + 14, x + 58, y + 22], fill="#27c93f")

        d.text((x + 75, y + 12), step, font=font(12, bold=True), fill=color)
        d.text((x + 75, y + 28), title, font=font(13, bold=True), fill=WHITE)

        cy = y + 56
        rrect(d, [x + 18, cy, x + pw - 18, y + ph - 12], 6, fill=DEEP)

        for j, line in enumerate(code.split("\n")):
            color_line = SUB
            if line.startswith("$"):
                color_line = GREEN
            elif line.startswith("["):
                color_line = LIGHT
            elif line.startswith(">"):
                color_line = AMBER
            elif line.startswith("✓"):
                color_line = GREEN
            elif '"' in line:
                color_line = TEAL_LIGHT
            d.text((x + 28, cy + 10 + j * 17), line, font=mono(10), fill=color_line)

    watermark(d)
    img.save(os.path.join(OUT, "05_walkthrough.png"))


def main():
    img_01()
    print("[OK] 01_hero.png")
    img_02()
    print("[OK] 02_compare.png")
    img_03()
    print("[OK] 03_provider.png")
    img_04()
    print("[OK] 04_multimodel.png")
    img_05()
    print("[OK] 05_walkthrough.png")
    print("\nDone:", OUT)


if __name__ == "__main__":
    main()
