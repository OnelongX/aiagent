# -*- coding: utf-8 -*-
"""4 images for Codex CLI 配置教程 - 1080x600"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\Codex配置教程"
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


# ============ 01: HERO - Codex CLI 配置全图 ============
def img_01():
    img, d = base()

    rrect(d, [60, 50, 240, 88], 19, fill=CYAN)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)

    rrect(d, [256, 50, 420, 88], 19, fill=BOX)
    d.text((274, 56), "AI 编程 · 工具教程", font=font(18, bold=True), fill=AMBER)

    d.text((60, 130), "Codex CLI 配置完整教程", font=font(36, bold=True), fill=AMBER)
    d.text((60, 178), "从 0 到 1 用上自定义模型 + 第三方提供商", font=font(20, bold=True), fill=WHITE)
    d.text((60, 220), "一个 base_url · 同时跑 GPT-5 / Claude / Gemini / DeepSeek", font=font(15), fill=LIGHT)

    items = [
        ("01", "安装", "brew / npm / winget", BLUE),
        ("02", "配置", "~/.codex/config.toml", PURPLE),
        ("03", "API key", "环境变量", AMBER),
        ("04", "测试", "codex 启动", GREEN),
    ]

    by = 270
    bw = (W - 120 - 60) // 4
    bh = 230

    for i, (num, name, detail, color) in enumerate(items):
        x = 60 + i * (bw + 20)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)
        d.text((x + 22, by + 18), num, font=font(28, bold=True), fill=color)
        d.text((x + 22, by + 70), name, font=font(24, bold=True), fill=WHITE)
        d.line([(x + 22, by + 116), (x + bw - 22, by + 116)], fill=LINE, width=1)
        d.text((x + 22, by + 130), detail, font=mono(13), fill=SUB)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "5 分钟搞定 · 模型够全 · 跑得稳 · 接入懒得动手", font=font(16, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))


# ============ 02: 配置文件 4 大模块 ============
def img_02():
    img, d = base()

    d.text((60, 40), "config.toml · 4 大配置模块", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "模型选择 · 推理强度 · 行为控制 · 自定义提供商", font=font(15), fill=LIGHT)

    items = [
        ("01", "模型选择", "model / model_provider / review_model",
         "主模型 · 提供商引用 · review 模型", BLUE),
        ("02", "推理强度", "model_reasoning_effort / verbosity",
         "minimal / low / medium / high / xhigh", PURPLE),
        ("03", "行为控制", "approval_policy / sandbox_mode / web_search",
         "执行许可 · 沙箱 · 联网搜索", AMBER),
        ("04", "自定义提供商", "[model_providers.X] block",
         "base_url · wire_api · env_key", GREEN),
    ]

    by = 130
    bh = 95
    spacing = 8

    for i, (num, name, code, detail, color) in enumerate(items):
        y = by + i * (bh + spacing)
        rrect(d, [60, y, W - 60, y + bh], 12, fill=BOX)
        d.rectangle([60, y, 68, y + bh], fill=color)
        d.text((90, y + 14), num, font=font(20, bold=True), fill=color)
        d.text((150, y + 14), name, font=font(20, bold=True), fill=WHITE)
        d.text((150, y + 46), code, font=mono(13), fill=AMBER)
        d.text((150, y + 70), detail, font=font(13), fill=LIGHT)

    # bottom
    rrect(d, [60, 510, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 525), "4 大模块 + 1 个 [model_providers.X] = 完整配置", font=font(16, bold=True), fill=AMBER)
    d.text((90, 553), "API key 不写在 toml 里 · 用环境变量", font=font(14), fill=GREEN)

    watermark(d)
    img.save(os.path.join(OUT, "02_config_blocks.png"))


# ============ 03: 自定义提供商接入流程 ============
def img_03():
    img, d = base()

    d.text((60, 40), "自定义提供商接入 · 一行 base_url", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "OpenAI 兼容服务 · Codex / Cursor / Cline 全通用", font=font(15), fill=LIGHT)

    # Code block
    cy = 130
    rrect(d, [60, cy, W - 60, cy + 220], 12, fill=DEEP, outline=PURPLE, width=2)
    d.rectangle([60, cy, 68, cy + 220], fill=PURPLE)
    d.text((85, cy + 18), "[model_providers.cm]", font=mono(16, bold=True), fill=PURPLE)
    code_lines = [
        ('name', '"OpenAI"', "显示名"),
        ('base_url', '"https://livetoken.top"', "兼容端点"),
        ('wire_api', '"responses"', "GPT-5 必须"),
        ('env_key', '"OPENAI_API_KEY"', "读环境变量"),
    ]
    for i, (k, v, note) in enumerate(code_lines):
        y = cy + 56 + i * 36
        d.text((100, y), k, font=mono(15, bold=True), fill=AMBER)
        d.text((220, y), "=", font=mono(15), fill=WHITE)
        d.text((250, y), v, font=mono(15), fill=GREEN)
        d.text((620, y), "← " + note, font=font(13), fill=LIGHT)

    # 4 个原因
    by = 380
    bh = 50
    items = [
        ("模型全", "GPT-5 / Claude / Gemini / DeepSeek 一个端点全有", GREEN),
        ("协议全", "responses 协议完整支持 · 推理摘要不丢", BLUE),
        ("接入简", "改 1 行 base_url · 代码不动", AMBER),
        ("跑得稳", "国内直连 · 长 SSE / 并发 / 推理任务都稳", PURPLE),
    ]
    for i, (k, v, color) in enumerate(items):
        x = 60 + (i % 2) * ((W - 120) // 2 + 5)
        y = by + (i // 2) * (bh + 8)
        rrect(d, [x, y, x + (W - 120) // 2 - 5, y + bh], 8, fill=BOX)
        d.rectangle([x, y, x + 6, y + bh], fill=color)
        d.text((x + 18, y + 8), "✓ " + k, font=font(14, bold=True), fill=color)
        d.text((x + 18, y + 28), v, font=font(11), fill=LIGHT)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "我自己实战配的是 livetoken.top · 4 个理由都满足", font=font(16, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "03_provider.png"))


# ============ 04: 3 套预设对比 ============
def img_04():
    img, d = base()

    d.text((60, 40), "3 套预设 · 复制即用", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "开发主力 / 复杂重构 / 省钱模式", font=font(15), fill=LIGHT)

    items = [
        ("预设 1", "开发主力", "GPT-5.5 + 高思考",
         "model_reasoning_effort\n= high\n\nsandbox_mode\n= workspace-write\n\napproval_policy\n= on-request\n\nservice_tier\n= fast", GREEN),
        ("预设 2", "复杂重构", "xhigh + 多模型",
         "model_reasoning_effort\n= xhigh\n\nplan_mode_reasoning_effort\n= xhigh\n\nmodel_verbosity\n= high\n\nreview_model\n= gpt-5.4", AMBER),
        ("预设 3", "省钱模式", "low + 只读",
         "model_reasoning_effort\n= low\n\nsandbox_mode\n= read-only\n\napproval_policy\n= always\n\nservice_tier\n= standard", BLUE),
    ]

    bw = (W - 120 - 40) // 3
    bx = 60
    by = 130
    bh = 380

    for i, (num, name, sub, body, color) in enumerate(items):
        x = bx + i * (bw + 20)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)
        d.text((x + 25, by + 18), num, font=font(15, bold=True), fill=DIM)
        d.text((x + 25, by + 44), name, font=font(22, bold=True), fill=color)
        d.text((x + 25, by + 80), sub, font=font(14, bold=True), fill=AMBER)
        d.line([(x + 25, by + 110), (x + bw - 25, by + 110)], fill=LINE, width=1)
        for j, line in enumerate(body.split("\n")):
            d.text((x + 25, by + 124 + j * 22), line, font=mono(11), fill=SUB if line.strip() else LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "04_presets.png"))


# ============ 05: 实战流程 4 步走 ============
def img_05():
    img, d = base()

    d.text((60, 40), "配置 Codex · 4 步走完整流程", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "复制粘贴即可 · 5 分钟搞定", font=font(15), fill=LIGHT)

    panels = [
        ("STEP 1", "安装 Codex CLI", "$ npm install -g @openai/codex\n\n$ codex --version\nCodex 1.0.0", BLUE),
        ("STEP 2", "编辑 ~/.codex/config.toml",
         'model = "gpt-5.5"\nmodel_provider = "cm"\n\n[model_providers.cm]\nname = "OpenAI"\nbase_url = "https://livetoken.top"\nwire_api = "responses"\nenv_key = "OPENAI_API_KEY"', PURPLE),
        ("STEP 3", "设置 API Key",
         '$ echo \'export OPENAI_API_KEY=\\\n  "sk-xxxxx"\' >> ~/.zshrc\n\n$ source ~/.zshrc\n$ echo $OPENAI_API_KEY\nsk-xxxxx', AMBER),
        ("STEP 4", "启动并使用",
         '$ cd ~/my-project\n$ codex\n\n> 帮我重构 src/utils.py\n\n[Codex 思考中...]\n[修改 src/utils.py]\n[运行测试 ✓]\nDone.', GREEN),
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

        # Window dots (mac-style chrome)
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
            elif "model" in line or "base_url" in line or "wire_api" in line or "env_key" in line or "[model" in line:
                color_line = TEAL_LIGHT
            d.text((x + 28, cy + 10 + j * 17), line, font=mono(10), fill=color_line)

    watermark(d)
    img.save(os.path.join(OUT, "05_walkthrough.png"))


def main():
    img_01()
    print("[OK] 01_hero.png")
    img_02()
    print("[OK] 02_config_blocks.png")
    img_03()
    print("[OK] 03_provider.png")
    img_04()
    print("[OK] 04_presets.png")
    img_05()
    print("[OK] 05_walkthrough.png")
    print("\nDone:", OUT)


if __name__ == "__main__":
    main()
