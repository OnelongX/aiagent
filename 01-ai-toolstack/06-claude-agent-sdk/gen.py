# -*- coding: utf-8 -*-
"""5 images for Claude Agent SDK 教程 - 1080x600"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\ClaudeAgentSDK教程"
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
INDIGO = "#6366f1"

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


# ============ 01: HERO - Agent SDK 概览 ============
def img_01():
    img, d = base()

    rrect(d, [60, 50, 240, 88], 19, fill=ORANGE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)

    rrect(d, [256, 50, 460, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 6/6 收官", font=font(18, bold=True), fill=AMBER)

    d.text((60, 130), "Claude Agent SDK 完整教程", font=font(34, bold=True), fill=AMBER)
    d.text((60, 178), "从 0 构建你自己的 AI Agent", font=font(24, bold=True), fill=WHITE)
    d.text((60, 218), "Python + TypeScript · 6 大核心能力 · 内置 10 工具", font=font(15), fill=LIGHT)

    items = [
        ("Python", "pip install\nclaude-agent-sdk", BLUE),
        ("TypeScript", "npm install\n@anthropic-ai/claude-agent-sdk", AMBER),
        ("引擎", "= Claude Code\n库版本", GREEN),
        ("生产可用", "CI/CD · Web服务\n生产环境", PURPLE),
    ]

    by = 270
    bw = (W - 120 - 60) // 4
    bh = 230

    for i, (name, body, color) in enumerate(items):
        x = 60 + i * (bw + 20)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)
        d.text((x + 22, by + 18), name, font=font(20, bold=True), fill=color)
        d.line([(x + 22, by + 56), (x + bw - 22, by + 56)], fill=LINE, width=1)
        for j, line in enumerate(body.split("\n")):
            d.text((x + 22, by + 80 + j * 28), line, font=mono(12), fill=WHITE)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "从用工具到造工具 · 国内 AI 开发者的关键跃迁", font=font(16, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))


# ============ 02: SDK vs CLI vs Managed Agents 对比 ============
def img_02():
    img, d = base()

    d.text((60, 40), "Agent SDK vs CLI vs Managed Agents", font=font(26, bold=True), fill=WHITE)
    d.text((60, 84), "3 种 Claude Agent 形态 · 各自适合场景", font=font(15), fill=LIGHT)

    hy = 130
    rrect(d, [60, hy, W - 60, hy + 38], 6, fill=DEEP)
    d.text((76, hy + 9), "维度", font=font(13, bold=True), fill=AMBER)
    d.text((290, hy + 9), "Agent SDK", font=font(13, bold=True), fill=BLUE)
    d.text((550, hy + 9), "Claude Code CLI", font=font(13, bold=True), fill=ORANGE)
    d.text((830, hy + 9), "Managed Agents", font=font(13, bold=True), fill=PURPLE)

    rows = [
        ("形态", "库 / 编程接口", "CLI / TUI", "REST API"),
        ("跑哪", "你的进程", "你的机器", "Anthropic 托管"),
        ("接口", "Python / TS", "终端", "REST"),
        ("Agent 操作", "你的文件系统", "你的文件系统", "托管 sandbox"),
        ("会话状态", "JSONL 你磁盘", "同", "Anthropic 托管"),
        ("自定义工具", "in-process 函数", "不支持", "Claude 触发"),
        ("适合", "本地原型 / agent", "日常开发", "生产 / 长任务"),
    ]

    ry = hy + 48
    rh = 50
    for i, (k, sdk, cli, ma) in enumerate(rows):
        bg = BOX if i % 2 == 0 else DEEP
        rrect(d, [60, ry, W - 60, ry + rh - 4], 6, fill=bg)
        d.text((76, ry + 14), k, font=font(13, bold=True), fill=AMBER)
        d.text((290, ry + 14), sdk, font=font(12), fill=WHITE)
        d.text((550, ry + 14), cli, font=font(12), fill=WHITE)
        d.text((830, ry + 14), ma, font=font(12), fill=WHITE)
        ry += rh

    # bottom
    rrect(d, [60, ry + 6, W - 60, ry + 60], 8, fill=DEEP, outline=GREEN, width=2)
    d.text((80, ry + 22), "常见路径:本地用 SDK 原型 → 上 Managed Agents 跑生产", font=font(14, bold=True), fill=GREEN)

    watermark(d)
    img.save(os.path.join(OUT, "02_compare.png"))


# ============ 03: 6 大核心能力 ============
def img_03():
    img, d = base()

    d.text((60, 40), "6 大核心能力 · SDK 全开放", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "Claude Code 有什么 · SDK 就有什么", font=font(15), fill=LIGHT)

    items = [
        ("01", "Built-in Tools", "10 种工具", "Read / Write / Edit / Bash\nGlob / Grep / WebSearch / WebFetch", BLUE),
        ("02", "Hooks", "生命周期回调", "PreToolUse / PostToolUse\nStop / SessionStart / SessionEnd", PURPLE),
        ("03", "Subagents", "派出专项 agent", "code-reviewer / security-reviewer\n主 agent 委派 + 报告", PINK),
        ("04", "MCP", "接外部系统", "数据库 / 浏览器 / API / GitHub\nPlaywright / Slack 等几百个", AMBER),
        ("05", "Permissions", "工具权限控制", "allowed_tools / permission_mode\nread-only / acceptEdits / plan", GREEN),
        ("06", "Sessions", "跨会话上下文", "resume / fork\nClaude 记得文件 / 分析 / 历史", CYAN),
    ]

    by = 130
    cw = (W - 120 - 30) // 2
    ch = 130
    spacing = 12

    for i, (num, name, sub, body, color) in enumerate(items):
        x = 60 + (i % 2) * (cw + 30)
        y = by + (i // 2) * (ch + spacing)
        rrect(d, [x, y, x + cw, y + ch], 12, fill=BOX, outline=color, width=2)
        d.rectangle([x, y, x + 8, y + ch], fill=color)
        d.text((x + 22, y + 14), num, font=font(20, bold=True), fill=color)
        d.text((x + 70, y + 14), name, font=font(18, bold=True), fill=WHITE)
        d.text((x + 70, y + 44), sub, font=font(13), fill=AMBER)
        d.line([(x + 22, y + 70), (x + cw - 22, y + 70)], fill=LINE, width=1)
        for j, line in enumerate(body.split("\n")):
            d.text((x + 22, y + 82 + j * 22), line, font=mono(11), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "03_six_caps.png"))


# ============ 04: 自定义工具流程 ============
def img_04():
    img, d = base()

    d.text((60, 40), "自定义工具 · createSdkMcpServer", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "任何 Python / TypeScript 函数 → Claude 可调用工具", font=font(15), fill=LIGHT)

    # 4 步流程
    steps = [
        ("STEP 1", "定义工具函数",
         "@tool(\n  name=\"query_db\",\n  description=\"...\",\n  input_schema=Schema\n)\nasync def query_db(args):\n    return {\"content\": ...}", BLUE),
        ("STEP 2", "createSdkMcpServer",
         "from claude_agent_sdk import \\\n  create_sdk_mcp_server\n\nmcp = create_sdk_mcp_server(\n  name=\"my-tools\",\n  tools=[query_db]\n)", PURPLE),
        ("STEP 3", "传给 query()",
         "async for msg in query(\n  prompt=\"...\",\n  options=ClaudeAgentOptions(\n    mcp_servers={\n      \"my-tools\": mcp\n    }\n  )\n)", AMBER),
        ("STEP 4", "Claude 自动调用",
         "Claude 看到工具描述\n判断什么时候调用\n→ 调你的函数\n→ 拿结果继续推理", GREEN),
    ]

    pw = (W - 120 - 30) // 2
    ph = 200
    by = 130
    spacing_x = 30
    spacing_y = 20

    for i, (step, title, code, color) in enumerate(steps):
        x = 60 + (i % 2) * (pw + spacing_x)
        y = by + (i // 2) * (ph + spacing_y)

        rrect(d, [x, y, x + pw, y + ph], 12, fill=BOX, outline=color, width=2)
        d.rectangle([x, y, x + 8, y + ph], fill=color)

        d.ellipse([x + 22, y + 14, x + 30, y + 22], fill="#ff5f56")
        d.ellipse([x + 36, y + 14, x + 44, y + 22], fill="#ffbd2e")
        d.ellipse([x + 50, y + 14, x + 58, y + 22], fill="#27c93f")

        d.text((x + 75, y + 12), step, font=font(12, bold=True), fill=color)
        d.text((x + 75, y + 28), title, font=font(13, bold=True), fill=WHITE)

        cy = y + 56
        rrect(d, [x + 18, cy, x + pw - 18, y + ph - 12], 6, fill=DEEP)

        for j, line in enumerate(code.split("\n")):
            color_line = SUB
            if "@" in line or "=" in line:
                color_line = TEAL_LIGHT
            elif line.startswith("from") or line.startswith("import"):
                color_line = BLUE
            elif "async" in line or "def" in line:
                color_line = AMBER
            elif line.startswith("→"):
                color_line = GREEN
            d.text((x + 28, cy + 8 + j * 16), line, font=mono(10), fill=color_line)

    watermark(d)
    img.save(os.path.join(OUT, "04_custom_tools.png"))


# ============ 05: 安装 → Hello World → 实战 ============
def img_05():
    img, d = base()

    d.text((60, 40), "Claude Agent SDK · 4 步走完整流程", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "5 分钟跑通第一个 agent · 国内开发者第三方接入", font=font(15), fill=LIGHT)

    panels = [
        ("STEP 1", "安装 SDK(选一种)",
         "$ pip install \\\n    claude-agent-sdk\n\n# 或 TypeScript\n$ npm install \\\n    @anthropic-ai/\\\n    claude-agent-sdk",
         BLUE),
        ("STEP 2", "设置 API Key(走 livetoken)",
         '$ export \\\n  ANTHROPIC_AUTH_TOKEN=\\\n  "sk-livetoken-xxx"\n\n$ export \\\n  ANTHROPIC_BASE_URL=\\\n  "https://livetoken.top"',
         AMBER),
        ("STEP 3", "写 Hello World agent",
         '# hello.py\nimport asyncio\nfrom claude_agent_sdk \\\n  import query\n\nasync def main():\n  async for msg in query(\n    prompt="What\'s here?"\n  ):\n    print(msg)',
         PURPLE),
        ("STEP 4", "运行 + Claude 自动跑工具循环",
         '$ python hello.py\n[Claude 调用 Bash...]\n[Claude 调用 Glob...]\n[Claude 整理结果...]\n\n→ 输出文件清单\n✓ Done',
         GREEN),
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
            elif line.startswith("#"):
                color_line = LIGHT
            elif line.startswith("[") or line.startswith("→") or line.startswith("✓"):
                color_line = AMBER
            elif "import" in line or "async" in line or "def" in line:
                color_line = TEAL_LIGHT
            d.text((x + 28, cy + 8 + j * 14), line, font=mono(10), fill=color_line)

    watermark(d)
    img.save(os.path.join(OUT, "05_walkthrough.png"))


def main():
    img_01()
    print("[OK] 01_hero.png")
    img_02()
    print("[OK] 02_compare.png")
    img_03()
    print("[OK] 03_six_caps.png")
    img_04()
    print("[OK] 04_custom_tools.png")
    img_05()
    print("[OK] 05_walkthrough.png")
    print("\nDone:", OUT)


if __name__ == "__main__":
    main()
