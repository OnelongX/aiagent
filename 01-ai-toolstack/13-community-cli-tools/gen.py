# -*- coding: utf-8 -*-
"""9 images for 5 个非官方 AI CLI 神器 · AI 工具栈 #13"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# 主题 · 暗黑 + 5 工具 5 色
BG       = "#0a0e1a"
BOX      = "#14192a"
DEEP     = "#050810"
LINE     = "#26304a"
WHITE    = "#ffffff"
SUB      = "#cfd9eb"
LIGHT    = "#94a8c4"
DIM      = "#5b6a87"

# 5 工具 5 色
DEEPSEEK = "#a78bfa"          # 蓝紫
AICHAT   = "#fb923c"          # 橙
AIDER    = "#34d399"          # 绿(代码 / git)
MODS     = "#c084fc"          # 紫(charm 风格)
FABRIC   = "#f87171"          # 红(创意 · pattern)

# 辅助
AMBER    = "#fbbf24"
AMBER_L  = "#fde047"
CYAN     = "#67e8f9"
BLUE_L   = "#93c5fd"
GREEN_L  = "#86efac"
PINK_L   = "#f9a8d4"
YELLOW   = "#fde047"

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
    rrect(d, [60, 50, 240, 88], 19, fill=AMBER)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 #13", font=font(17, bold=True), fill=AMBER_L)

    d.text((60, 128), "5 个非官方 AI CLI 神器", font=font(40, bold=True), fill=AMBER_L)
    d.text((60, 188), "社区出品 · 国内开发者必备", font=font(22, bold=True), fill=WHITE)
    d.text((60, 226), "GitHub 合计 60k+ star · 一行装 · 一行换 endpoint", font=font(16), fill=SUB)

    # 5 工具横排小 chip
    tools = [
        ("DeepSeek-TUI", DEEPSEEK),
        ("aichat",       AICHAT),
        ("aider",        AIDER),
        ("mods",         MODS),
        ("fabric",       FABRIC),
    ]
    cw = 192
    for i, (name, c) in enumerate(tools):
        x = 60 + i * (cw + 8)
        rrect(d, [x, 290, x + cw, 350], 12, fill=BOX, outline=c, width=2)
        d.text((x + (cw - tw(d, name, font(17, bold=True))) // 2, 305), name, font=font(17, bold=True), fill=c)

    rrect(d, [60, 380, 1020, 520], 14, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 398), "官方 CLI 教你怎么用我家模型", font=font(18), fill=LIGHT)
    d.text((80, 426), "社区 CLI 教你怎么用 AI", font=font(20, bold=True), fill=AMBER_L)
    d.text((80, 462), "单一职责 · Unix 哲学 · 可 hack · 零厂商绑定", font=font(14), fill=SUB)
    d.text((80, 488), "★ 整套国内 livetoken 一个 base_url 全打通", font=font(14, bold=True), fill=GREEN_L)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 5 工具速览 ============
def img_02():
    img, d = base()
    d.text((60, 40), "5 个工具速览 · 各有杀手锏", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "都 2025-2026 仍活跃维护 · GitHub 合计 60k+ star", font=font(15), fill=LIGHT)

    tools = [
        ("DeepSeek-TUI", DEEPSEEK, "Hmbown",         "Rust",   "1M 上下文 + 流式推理可视化"),
        ("aichat",       AICHAT,   "sigoden(中)",   "Rust",   "280+ 模型瑞士军刀 · REPL+pipe+RAG"),
        ("aider",        AIDER,    "Aider-AI",       "Python", "git-aware + 自动 commit · 20k+ star"),
        ("mods",         MODS,     "charmbracelet",  "Go",     "Unix pipe 极简 · 不做 REPL"),
        ("fabric",       FABRIC,   "danielmiessler", "Go",     "200+ Prompt Pattern 库"),
    ]

    y0 = 122
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    headers = ["工具", "作者", "语言", "杀手锏"]
    col_x = [60, 260, 460, 600]
    for i, h in enumerate(headers):
        d.text((col_x[i] + 12, y0 + 8), h, font=font(13, bold=True), fill=AMBER_L)

    for i, (name, c, author, lang, killer) in enumerate(tools):
        y = y0 + 38 + i * 68
        rrect(d, [60, y, 1020, y + 58], 10, fill=BOX, outline=c, width=2)
        # 工具名 + 色块
        rrect(d, [78, y + 12, 250, y + 46], 8, fill=c)
        d.text((90, y + 20), name, font=font(16, bold=True), fill=BG)
        # 其他列
        d.text((col_x[1] + 12, y + 20), author, font=font(13), fill=WHITE)
        d.text((col_x[2] + 12, y + 20), lang,   font=mono(13), fill=SUB)
        d.text((col_x[3] + 12, y + 20), killer, font=font(13, bold=True), fill=c)

    watermark(d)
    img.save(os.path.join(OUT, "02_overview.png"))
    print("[OK] 02_overview")


# ============ 通用单工具页生成器 ============
def tool_page(name, color, killer_lines, install_lines, demo_lines,
              filename, accent_extra=None):
    """单工具深度页通用模板"""
    img, d = base()
    rrect(d, [60, 50, 60 + 240, 92], 8, fill=color)
    d.text((78, 60), name, font=font(22, bold=True), fill=BG)
    d.text((320, 60), "杀手锏 / 安装 / Demo · 一图收齐", font=font(15), fill=LIGHT)

    # 杀手锏
    rrect(d, [60, 116, 1020, 224], 12, fill=BOX, outline=color, width=2)
    d.text((78, 130), "杀手锏", font=font(15, bold=True), fill=color)
    for i, line in enumerate(killer_lines):
        d.text((78, 158 + i * 20), "• " + line, font=font(13), fill=SUB)

    # 安装(自动判断每行:纯 ASCII 用 mono · 含中文用 msyh)
    rrect(d, [60, 244, 540, 540], 12, fill=BOX, outline=color, width=2)
    d.text((78, 258), "安装", font=font(15, bold=True), fill=color)
    for i, line in enumerate(install_lines):
        is_ascii = line.isascii()
        d.text((78, 286 + i * 22), line, font=(mono(12) if is_ascii else font(12)), fill=SUB)

    # Demo
    rrect(d, [560, 244, 1020, 540], 12, fill=BOX, outline=color, width=2)
    d.text((578, 258), "用法 Demo", font=font(15, bold=True), fill=color)
    for i, line in enumerate(demo_lines):
        is_ascii = line.isascii()
        d.text((578, 286 + i * 22), line, font=(mono(12) if is_ascii else font(12)), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, filename))
    print(f"[OK] {filename}")


# ============ 03-07 各工具页 ============
def img_03_deepseek_tui():
    tool_page(
        "DeepSeek-TUI",
        DEEPSEEK,
        killer_lines=[
            "DeepSeek V4 · 1M 上下文",
            "Shift+Tab 切流式推理级别(off / high / max)",
            "@path 加文件到上下文 · Subagent 协作",
            "1M token 大代码库不爆 · NVIDIA NIM / Ollama 备选",
        ],
        install_lines=[
            "# 4 种装法任选",
            "npm install -g deepseek-tui",
            "cargo install deepseek-tui-cli --locked",
            "brew tap Hmbown/deepseek-tui",
            "  brew install deepseek-tui",
            "",
            "# 配 key",
            "export DEEPSEEK_API_KEY=sk-xxx",
            "deepseek doctor",
            "",
            "# Docker(不装本地)",
            "docker run -it -e DEEPSEEK_API_KEY \\",
            "    -v $PWD:/workspace \\",
            "    ghcr.io/hmbown/deepseek-tui",
        ],
        demo_lines=[
            "# 交互模式",
            "deepseek",
            "",
            "# 一次性",
            'deepseek "重构这个函数"',
            "",
            "# 自动选模型 + 推理级别",
            'deepseek --model auto "修这个 bug"',
            "",
            "# 工具调用免确认(快但危险)",
            "deepseek --yolo",
            "",
            "# 用 livetoken 中转",
            "deepseek auth set \\",
            "  --provider openai-compatible \\",
            "  --api-base https://livetoken.top/v1",
        ],
        filename="03_deepseek_tui.png",
    )


def img_04_aichat():
    tool_page(
        "aichat",
        AICHAT,
        killer_lines=[
            "280+ 模型同一 CLI(OpenAI/Claude/Gemini/Ollama/DeepSeek/Qwen ...)",
            "Shell Assistant · aichat -e \"安装 nvim 并配 lazyvim\"",
            "RAG 内置 · aichat --rag mydocs 自动建索引",
            "自带 HTTP server · aichat --serve 当 OpenAI 兼容 API 用",
            "国内开发者 sigoden 出品",
        ],
        install_lines=[
            "# 任选一种",
            "cargo install aichat",
            "brew install aichat",
            "scoop install aichat",
            "",
            "# 配 ~/.config/aichat/config.yaml",
            "clients:",
            "- type: openai-compatible",
            "  name: livetoken",
            "  api_base:",
            "    https://livetoken.top/v1",
            "  api_key: sk-xxxxx",
            "  models:",
            "  - name: claude-sonnet-4-5",
            "  - name: gpt-5",
        ],
        demo_lines=[
            "# 单轮",
            'aichat "解释 Subagent"',
            "",
            "# 切模型",
            'aichat -m claude-sonnet-4-5 "..."',
            "",
            "# Unix pipe(杀手锏)",
            'cat error.log | aichat "找异常"',
            "",
            "# Shell Assistant",
            'aichat -e "找 100M 以上的文件"',
            "",
            "# Code Mode(直出代码)",
            'aichat -c "Python 素数生成器"',
            "",
            "# RAG",
            "aichat --rag mydocs",
            "",
            "# 当 OpenAI 兼容 API",
            "aichat --serve 0.0.0.0:8080",
        ],
        filename="04_aichat.png",
    )


def img_05_aider():
    tool_page(
        "aider",
        AIDER,
        killer_lines=[
            "git-aware · 改文件自动 git commit · 出问题 git revert 秒回",
            "Repo Map · 自动建整个 repo 索引 · 大 repo 不乱改",
            "--architect 双模型 · Claude Opus 想 + Sonnet 改 · 省一半钱",
            "20k+ star · 圈内公认神器 · Paul Gauthier 出品",
        ],
        install_lines=[
            "# 推荐(独立 Python)",
            "pip install aider-install",
            "aider-install",
            "",
            "# 直接 pip",
            "pip install aider-chat",
            "",
            "# 配 key(任选其一)",
            "export ANTHROPIC_API_KEY=sk-ant-xxx",
            "export OPENAI_API_KEY=sk-xxx",
            "export DEEPSEEK_API_KEY=sk-xxx",
            "",
            "# 国内 livetoken",
            "export OPENAI_API_BASE=\\",
            "  https://livetoken.top/v1",
            "export OPENAI_API_KEY=\\",
            "  sk-livetoken-xxx",
        ],
        demo_lines=[
            "# 在 git repo 根目录跑",
            "cd your-project",
            "aider                    # 默认 Sonnet",
            "aider --model \\",
            "  deepseek/deepseek-chat",
            "",
            "# 交互",
            "aider> /add src/*.py",
            "aider> 把 calc_price 改成",
            "       阶梯计价 · 更新调用",
            "# 自动改多文件 + commit",
            "",
            "aider> /undo     # 撤销",
            "aider> /run pytest",
            "",
            "# Architect 模式",
            "aider --architect \\",
            "  --model opus-4-5 \\",
            "  --editor-model sonnet",
        ],
        filename="05_aider.png",
    )


def img_06_mods():
    tool_page(
        "mods",
        MODS,
        killer_lines=[
            "Charm 团队出品 · Bubble Tea / Glow 同家",
            "Unix pipe 极简哲学 · 不做 REPL · 不做 Agent",
            "stderr 出动画 · stdout 出结果 · 完美链式管道",
            "适合 shell 党 / vim 党 · 把 AI 加进现有工作流",
        ],
        install_lines=[
            "# macOS",
            "brew install \\",
            "  charmbracelet/tap/mods",
            "",
            "# Linux",
            "sudo apt install mods",
            "yay -S mods",
            "",
            "# Go",
            "go install github.com/\\",
            "  charmbracelet/mods@latest",
            "",
            "# 配 ~/.config/mods/mods.yml",
            "apis:",
            "  livetoken:",
            "    base-url: ...",
            "    api-key-env: LIVETOKEN_KEY",
        ],
        demo_lines=[
            "# 解释代码",
            'cat main.go | mods "解释"',
            "",
            "# review · 找 bug",
            "git diff | mods \\",
            '  "review · 找 bug"',
            "",
            "# 自动写 commit message",
            "git diff --cached | mods \\",
            '  "commit msg · 一行"',
            "",
            "# 翻译日志",
            "docker logs api 2>&1 | \\",
            '  mods "翻译错误成中文"',
            "",
            "# 链式管道",
            'curl api | mods "找异常" \\',
            '  | mods "总结一句"',
            "",
            "# 续传",
            'echo "继续" | mods --continue',
        ],
        filename="06_mods.png",
    )


def img_07_fabric():
    tool_page(
        "fabric",
        FABRIC,
        killer_lines=[
            "200+ 社区 Prompt Pattern 库",
            "每个 pattern 是 ~/.config/fabric/patterns/<name>/system.md",
            "summarize / extract_wisdom / analyze_paper / explain_code ...",
            "URL / YouTube / PDF 输入支持",
            "Daniel Miessler 出品 · 内容创作神器",
        ],
        install_lines=[
            "# Go",
            "go install github.com/\\",
            "  danielmiessler/fabric@latest",
            "",
            "# 初始化(下载 patterns)",
            "fabric --setup",
            "",
            "# 列所有 patterns",
            "fabric -l",
            "",
            "# 200+ pattern 在",
            "~/.config/fabric/patterns/",
            "",
            "# 自定义 pattern",
            "mkdir -p ~/.config/fabric/\\",
            "  patterns/my_pattern",
            "echo 'You are ...' > \\",
            "  .../system.md",
        ],
        demo_lines=[
            "# 提取智慧点",
            'echo "AI Agent..." | \\',
            "  fabric -p extract_wisdom",
            "",
            "# 网页总结",
            "fabric -u \\",
            "  https://blog.com/post \\",
            "  -p summarize",
            "",
            "# YouTube 视频",
            "fabric -y \\",
            "  https://youtube.com/... \\",
            "  -p extract_wisdom",
            "",
            "# 链式",
            "fabric -u $url -p summarize \\",
            "  | fabric -p extract_main_idea",
            "",
            "# 改模型",
            "fabric -p analyze_paper \\",
            "  --model gpt-5 < paper.txt",
        ],
        filename="07_fabric.png",
    )


# ============ 08 组合工作流 ============
def img_08():
    img, d = base()
    d.text((60, 40), "5 工具组合工作流 · 谁干啥", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "不是替代关系 · 是互补 · 一个开发者的日常", font=font(15), fill=LIGHT)

    flows = [
        ("早上看日志",       MODS,     'docker logs api | mods "总结昨晚问题"'),
        ("跨文件改代码",     AIDER,    'aider · /add src/*.py · 描述改动 · 自动 commit'),
        ("跑 DeepSeek 推理", DEEPSEEK, 'deepseek --model auto "复杂分布式问题"'),
        ("多模型对比同问题", AICHAT,   'aichat -m claude / -m gpt-5 / -m gemini'),
        ("写日报 / 提取智慧", FABRIC,   'cat history | fabric -p summarize'),
        ("写 commit msg",    MODS,     'git diff --cached | mods "commit msg"'),
    ]
    y0 = 122
    for i, (scene, c, cmd) in enumerate(flows):
        y = y0 + i * 62
        rrect(d, [60, y, 1020, y + 52], 12, fill=BOX, outline=c, width=2)
        rrect(d, [78, y + 10, 260, y + 42], 8, fill=c)
        d.text((92, y + 16), scene, font=font(15, bold=True), fill=BG)
        # 自动判断
        is_ascii = cmd.isascii()
        d.text((280, y + 16), cmd, font=(mono(13) if is_ascii else font(13)), fill=SUB)

    rrect(d, [60, 500, 1020, 540], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 514), "★ 5 个工具加起来 < 1 个 IDE 的内存 · 灵活性 N 倍", font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "08_workflow.png"))
    print("[OK] 08_workflow")


# ============ 09 决策树 ============
def img_09():
    img, d = base()
    d.text((60, 40), "决策树 · 怎么选?", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "按你最常干的事 · 选 1 个开始 · 慢慢加", font=font(15), fill=LIGHT)

    decisions = [
        ("写代码 / 改代码 · git 严格管理",      AIDER,    "aider", "git-aware + Repo Map"),
        ("DeepSeek 重度用户 + 看推理过程",      DEEPSEEK, "DeepSeek-TUI", "Shift+Tab 切推理级别"),
        ("多模型对比 / 切换 / 通用 REPL",       AICHAT,   "aichat", "280+ 模型同一 CLI"),
        ("shell 党 / vim 党 / Unix pipe 党",   MODS,     "mods", "极简 · 不做 REPL"),
        ("内容创作 / 提取 / 总结 / 翻译",       FABRIC,   "fabric", "200+ pattern 复用"),
        ("我都要(进阶)",                       AMBER,    "全装", "按场景切 · 不要绑死一个"),
    ]
    y0 = 116
    for i, (scene, c, pick, why) in enumerate(decisions):
        y = y0 + i * 70
        rrect(d, [60, y, 1020, y + 58], 12, fill=BOX, outline=c, width=2)
        # 场景
        rrect(d, [78, y + 12, 420, y + 46], 8, fill=c)
        d.text((90, y + 19), scene, font=font(14, bold=True), fill=BG)
        # 选谁
        d.text((440, y + 12), "→ " + pick, font=font(17, bold=True), fill=c)
        d.text((440, y + 36), why, font=font(13), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "09_decision.png"))
    print("[OK] 09_decision")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03_deepseek_tui()
    img_04_aichat()
    img_05_aider()
    img_06_mods()
    img_07_fabric()
    img_08()
    img_09()
    print("\n[DONE] 9 images saved to", OUT)
