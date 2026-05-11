# -*- coding: utf-8 -*-
"""4 images for Claude 全家桶配置 article - 1080x600"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\Claude全家桶配置"
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


# ============ 01: HERO - Claude 全家桶 2 产品 3 端 ============
def img_01():
    img, d = base()

    rrect(d, [60, 50, 240, 88], 19, fill=ORANGE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)

    rrect(d, [256, 50, 460, 88], 19, fill=BOX)
    d.text((274, 56), "Claude 全家桶 · 完整配置", font=font(18, bold=True), fill=AMBER)

    d.text((60, 130), "Claude 桌面 app + VS Code 扩展", font=font(30, bold=True), fill=AMBER)
    d.text((60, 175), "完整配置教程", font=font(30, bold=True), fill=WHITE)
    d.text((60, 220), "一个 API key · 跑遍 Claude 全家桶", font=font(15), fill=LIGHT)

    items = [
        ("Claude Desktop", "聊天 + MCP", "GUI 桌面客户端\n文件分析 + 工具调用", ORANGE),
        ("Claude Code CLI", "AI 编程 CLI", "终端命令行\nPlan + Subagent", BLUE),
        ("Claude Code", "VS Code 扩展", "IDE 内嵌\n选中代码 → 问 AI", GREEN),
    ]

    by = 270
    bw = (W - 120 - 40) // 3
    bh = 230

    for i, (name, sub, body, color) in enumerate(items):
        x = 60 + i * (bw + 20)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)
        d.text((x + 22, by + 18), name, font=font(20, bold=True), fill=color)
        d.text((x + 22, by + 56), sub, font=font(15, bold=True), fill=AMBER)
        d.line([(x + 22, by + 96), (x + bw - 22, by + 96)], fill=LINE, width=1)
        for j, line in enumerate(body.split("\n")):
            d.text((x + 22, by + 110 + j * 30), line, font=font(13), fill=SUB)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "杀招:一个 token 同时跑 Codex + Claude Code 双引擎", font=font(16, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))


# ============ 02: Claude Desktop 3 标签页 + MCP ============
def img_02():
    img, d = base()

    d.text((60, 40), "Claude Desktop · 3 标签页统一应用", font=font(26, bold=True), fill=ORANGE)
    d.text((60, 84), "Chat / Cowork / Code · Code 标签跟 CLI 共享 settings.json", font=font(15), fill=LIGHT)

    # 3 tabs visualization
    tabs = [
        ("Chat", "聊天 + MCP", "claude_desktop_config.json", "Anthropic 账号", ORANGE),
        ("Cowork", "Dispatch 长任务", "Pro / Max 订阅", "Anthropic 账号", PURPLE),
        ("Code", "= Claude Code", "~/.claude/settings.json", "✓ 支持第三方 API", GREEN),
    ]

    by = 130
    bw = (W - 120 - 40) // 3
    bh = 230

    for i, (name, use, config, auth, color) in enumerate(tabs):
        x = 60 + i * (bw + 20)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)

        d.text((x + 22, by + 14), "标签页", font=font(11), fill=DIM)
        d.text((x + 22, by + 32), name, font=font(28, bold=True), fill=color)
        d.line([(x + 22, by + 80), (x + bw - 22, by + 80)], fill=LINE, width=1)
        d.text((x + 22, by + 92), "用途", font=font(11), fill=DIM)
        d.text((x + 22, by + 110), use, font=font(14, bold=True), fill=WHITE)
        d.line([(x + 22, by + 138), (x + bw - 22, by + 138)], fill=LINE, width=1)
        d.text((x + 22, by + 150), "配置入口", font=font(11), fill=DIM)
        d.text((x + 22, by + 168), config, font=mono(10), fill=AMBER)
        d.line([(x + 22, by + 196), (x + bw - 22, by + 196)], fill=LINE, width=1)
        d.text((x + 22, by + 208), auth, font=font(12, bold=True), fill=color)

    # bottom highlight box
    rrect(d, [60, 380, W - 60, 510], 14, fill=BOX, outline=GREEN, width=2)
    d.rectangle([60, 380, 68, 510], fill=GREEN)
    d.text((90, 395), "Code 标签 · 关键事实", font=font(18, bold=True), fill=GREEN)
    d.text((90, 425), "Code 标签 + CLI + VS Code 扩展 = 3 个端共享同一份 settings.json", font=font(14, bold=True), fill=WHITE)
    d.text((90, 452), "你在 CLI 里配的 ANTHROPIC_BASE_URL · Desktop Code 标签也生效", font=font(13), fill=LIGHT)
    d.text((90, 478), '官方:"Desktop and CLI read the same configuration files."', font=font(12), fill=AMBER)

    # very bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "配一次 settings.json · 3 个端同时切到第三方 API", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "02_desktop.png"))


# ============ 03: Claude Code CLI + VS Code 扩展 ============
def img_03():
    img, d = base()

    d.text((60, 40), "Claude Code · CLI + VS Code 扩展", font=font(28, bold=True), fill=BLUE)
    d.text((60, 84), "Anthropic 官方 AI 编程工具 · 跟 Codex 对标", font=font(15), fill=LIGHT)

    # 安装
    py = 130
    rrect(d, [60, py, W - 60, py + 75], 12, fill=DEEP)
    d.rectangle([60, py, 68, py + 75], fill=GREEN)
    d.text((85, py + 12), "安装", font=font(15, bold=True), fill=GREEN)
    d.text((85, py + 36), "npm install -g @anthropic-ai/claude-code", font=mono(13), fill=WHITE)
    d.text((85, py + 56), "VS Code Marketplace 搜 Claude Code (CLI 装好后扩展自动联动)", font=font(11), fill=LIGHT)

    # 配置文件
    py2 = 220
    rrect(d, [60, py2, W - 60, py2 + 105], 12, fill=DEEP)
    d.rectangle([60, py2, 68, py2 + 105], fill=PURPLE)
    d.text((85, py2 + 12), "配置文件 3 处", font=font(15, bold=True), fill=PURPLE)
    cfg_lines = [
        ("全局设置", "~/.claude/settings.json", "模型 / 权限 / 环境变量"),
        ("项目记忆", "<project>/.claude/CLAUDE.md", "项目背景 / 代码风格 / 命令"),
        ("全局记忆", "~/.claude/CLAUDE.md", "跨项目通用记忆"),
    ]
    for i, (k, p, desc) in enumerate(cfg_lines):
        y = py2 + 40 + i * 22
        d.text((85, y), k, font=font(12, bold=True), fill=AMBER)
        d.text((180, y), p, font=mono(11), fill=GREEN)
        d.text((480, y), desc, font=font(11), fill=LIGHT)

    # 关键变量
    py3 = 340
    rrect(d, [60, py3, W - 60, py3 + 120], 12, fill=BOX, outline=AMBER, width=2)
    d.rectangle([60, py3, 68, py3 + 120], fill=AMBER)
    d.text((85, py3 + 14), "第三方接入 · 关键变量", font=font(15, bold=True), fill=AMBER)
    env_lines = [
        ("ANTHROPIC_AUTH_TOKEN", '"sk-xxxxx"', "API 密钥"),
        ("ANTHROPIC_BASE_URL", '"https://livetoken.top"', "替换默认 api.anthropic.com"),
    ]
    for i, (k, v, note) in enumerate(env_lines):
        y = py3 + 46 + i * 32
        d.text((100, y), k, font=mono(13, bold=True), fill=AMBER)
        d.text((360, y), "=", font=mono(13), fill=WHITE)
        d.text((385, y), v, font=mono(13), fill=GREEN)
        d.text((720, y), "← " + note, font=font(11), fill=LIGHT)

    # bottom
    rrect(d, [60, 480, W - 60, 580], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((90, 495), "Claude Code 特色:CLAUDE.md 项目记忆 · Subagent · Plan 模式", font=font(14, bold=True), fill=GREEN)
    d.text((90, 525), "VS Code 扩展内部调用 CLI · 必须先装 CLI", font=font(13), fill=LIGHT)
    d.text((90, 553), "ANTHROPIC_BASE_URL 不要带 /v1 · 末尾不要斜杠", font=font(13), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "03_code.png"))


# ============ 04: 双引擎 - 一个 token 跑 Codex + Claude Code ============
def img_04():
    img, d = base()

    d.text((60, 40), "双引擎 · 一个 token 跑 Codex + Claude Code", font=font(26, bold=True), fill=AMBER)
    d.text((60, 84), "国内 AI 编程工作流的最优解 · 不维护两个账号", font=font(15), fill=LIGHT)

    # 中间一个 token
    cy = 130
    rrect(d, [380, cy, 700, cy + 100], 14, fill=BOX, outline=AMBER, width=3)
    d.rectangle([380, cy, 388, cy + 100], fill=AMBER)
    d.text((405, cy + 18), "1 个 token", font=font(20, bold=True), fill=AMBER)
    d.text((405, cy + 50), "sk-livetoken-xxxxx", font=mono(14), fill=GREEN)
    d.text((405, cy + 76), "余额合并算 · 不是 ×2", font=font(12), fill=LIGHT)

    # 左侧 Codex
    py = 270
    rrect(d, [60, py, 525, py + 230], 14, fill=BOX, outline=BLUE, width=2)
    d.rectangle([60, py, 68, py + 230], fill=BLUE)
    d.text((85, py + 14), "Codex", font=font(22, bold=True), fill=BLUE)
    d.text((85, py + 50), "OpenAI 协议 · GPT-5 / o 系列", font=font(13), fill=LIGHT)
    rrect(d, [85, py + 80, 505, py + 218], 8, fill=DEEP)
    d.text((100, py + 90), "OPENAI_API_KEY", font=mono(13, bold=True), fill=AMBER)
    d.text((100, py + 110), "= sk-livetoken-xxxxx", font=mono(12), fill=GREEN)
    d.text((100, py + 138), "~/.codex/config.toml:", font=mono(12, bold=True), fill=PURPLE)
    d.text((100, py + 158), 'base_url = "https://livetoken.top"', font=mono(11), fill=GREEN)
    d.text((100, py + 178), 'wire_api = "responses"', font=mono(11), fill=GREEN)
    d.text((100, py + 200), "→ codex 命令启动", font=font(12, bold=True), fill=AMBER)

    # 右侧 Claude Code
    rx = 555
    rrect(d, [rx, py, rx + 465, py + 230], 14, fill=BOX, outline=ORANGE, width=2)
    d.rectangle([rx, py, rx + 8, py + 230], fill=ORANGE)
    d.text((rx + 25, py + 14), "Claude Code", font=font(22, bold=True), fill=ORANGE)
    d.text((rx + 25, py + 50), "Anthropic 协议 · Claude Sonnet / Opus", font=font(13), fill=LIGHT)
    rrect(d, [rx + 25, py + 80, rx + 445, py + 218], 8, fill=DEEP)
    d.text((rx + 40, py + 90), "ANTHROPIC_AUTH_TOKEN", font=mono(13, bold=True), fill=AMBER)
    d.text((rx + 40, py + 110), "= sk-livetoken-xxxxx (同一个!)", font=mono(12), fill=GREEN)
    d.text((rx + 40, py + 138), "ANTHROPIC_BASE_URL", font=mono(13, bold=True), fill=AMBER)
    d.text((rx + 40, py + 158), '= "https://livetoken.top"', font=mono(12), fill=GREEN)
    d.text((rx + 40, py + 200), "→ claude 命令启动", font=font(12, bold=True), fill=AMBER)

    # bottom
    rrect(d, [60, 520, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 533), "重构用 Sonnet / 推理用 GPT-5 / Plan 用 Claude / 快速 review 用 Codex", font=font(13, bold=True), fill=AMBER)
    d.text((90, 558), "4 种场景 · 同一个 token · 任意切换", font=font(13), fill=GREEN)

    watermark(d)
    img.save(os.path.join(OUT, "04_dual.png"))


# ============ 05: 双引擎实战截图 ============
def img_05():
    img, d = base()

    d.text((60, 40), "双引擎实战 · 同一个 token 跑两套 AI", font=font(26, bold=True), fill=WHITE)
    d.text((60, 84), "终端 1 跑 Codex(GPT-5)· 终端 2 跑 Claude Code(Sonnet)", font=font(15), fill=LIGHT)

    panels = [
        ("Codex CLI", "OpenAI 协议",
         '$ codex\nWelcome to Codex.\nUsing GPT-5.5\n\n> 帮我写个 fibonacci\n\n[Codex 思考中...]\n[使用工具:write_file]\n\nfunction fib(n) {\n  if (n <= 1) return n;\n  return fib(n-1) + fib(n-2);\n}\n\n✓ Done',
         BLUE),
        ("Claude Code", "Anthropic 协议",
         '$ claude\nWelcome to Claude Code.\nUsing claude-sonnet-4\n\n> 重构 fib 用迭代法\n\n[Claude 思考中...]\n[使用工具:Edit]\n\nfunction fib(n) {\n  let [a, b] = [0, 1];\n  for (let i=0; i<n; i++)\n    [a,b] = [b, a+b];\n  return a;\n}\n\n✓ Done',
         ORANGE),
    ]

    pw = (W - 120 - 30) // 2
    ph = 380
    by = 130
    spacing_x = 30

    for i, (name, proto, code, color) in enumerate(panels):
        x = 60 + i * (pw + spacing_x)
        y = by

        rrect(d, [x, y, x + pw, y + ph], 12, fill=BOX, outline=color, width=2)
        d.rectangle([x, y, x + 8, y + ph], fill=color)

        # Mac-style window dots
        d.ellipse([x + 22, y + 14, x + 30, y + 22], fill="#ff5f56")
        d.ellipse([x + 36, y + 14, x + 44, y + 22], fill="#ffbd2e")
        d.ellipse([x + 50, y + 14, x + 58, y + 22], fill="#27c93f")

        d.text((x + 80, y + 14), name, font=font(16, bold=True), fill=color)
        d.text((x + 80, y + 36), proto, font=font(11), fill=AMBER)

        cy = y + 64
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
            elif "function" in line or "for" in line or "let" in line or "if" in line or "return" in line:
                color_line = TEAL_LIGHT
            d.text((x + 28, cy + 8 + j * 17), line, font=mono(10), fill=color_line)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "同一个 livetoken token 计费 · 余额合并 · 不是 ×2", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "05_dual_run.png"))


def main():
    img_01()
    print("[OK] 01_hero.png")
    img_02()
    print("[OK] 02_desktop.png")
    img_03()
    print("[OK] 03_code.png")
    img_04()
    print("[OK] 04_dual.png")
    img_05()
    print("[OK] 05_dual_run.png")
    print("\nDone:", OUT)


if __name__ == "__main__":
    main()
