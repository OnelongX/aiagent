# -*- coding: utf-8 -*-
"""4 images for Codex 三端通用 article - 1080x600"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\Codex三端通用"
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


# ============ 01: HERO - 1 份 config × 3 端 ============
def img_01():
    img, d = base()

    rrect(d, [60, 50, 240, 88], 19, fill=CYAN)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)

    rrect(d, [256, 50, 460, 88], 19, fill=BOX)
    d.text((274, 56), "Codex 进阶 · 三端通用", font=font(18, bold=True), fill=AMBER)

    d.text((60, 130), "Codex 三端通用配置", font=font(36, bold=True), fill=AMBER)
    d.text((60, 178), "一份 config.toml · 跑遍 CLI / 桌面 app / VS Code 插件", font=font(18, bold=True), fill=WHITE)
    d.text((60, 218), "Codex 体系隐藏福利 · 改一次 · 3 端同步", font=font(15), fill=LIGHT)

    # 中间一份 config 文件
    cy = 270
    rrect(d, [60, cy, 320, cy + 230], 14, fill=BOX, outline=AMBER, width=3)
    d.rectangle([60, cy, 68, cy + 230], fill=AMBER)
    d.text((85, cy + 18), "1 份 config", font=font(20, bold=True), fill=AMBER)
    d.text((85, cy + 56), "~/.codex/", font=mono(15, bold=True), fill=WHITE)
    d.text((85, cy + 80), "config.toml", font=mono(15, bold=True), fill=WHITE)
    d.line([(85, cy + 116), (300, cy + 116)], fill=LINE, width=1)
    d.text((85, cy + 132), "model =", font=mono(13), fill=GREEN)
    d.text((85, cy + 156), "model_provider =", font=mono(13), fill=GREEN)
    d.text((85, cy + 180), "base_url =", font=mono(13), fill=GREEN)
    d.text((85, cy + 204), "wire_api =", font=mono(13), fill=GREEN)

    # 中间箭头
    d.text((350, cy + 100), "→", font=font(50, bold=True), fill=AMBER)

    # 右侧 3 个端
    items = [
        ("Codex CLI", "终端命令行", BLUE),
        ("Codex 桌面 app", "GUI 客户端", PURPLE),
        ("VS Code 插件", "IDE 内嵌", GREEN),
    ]
    rx = 440
    rh = 70
    spacing = 10
    for i, (name, desc, color) in enumerate(items):
        y = cy + i * (rh + spacing)
        rrect(d, [rx, y, rx + (W - rx - 60), y + rh], 12, fill=BOX, outline=color, width=2)
        d.rectangle([rx, y, rx + 6, y + rh], fill=color)
        d.text((rx + 18, y + 14), name, font=font(20, bold=True), fill=color)
        d.text((rx + 18, y + 44), desc, font=font(13), fill=LIGHT)
        d.text((rx + (W - rx - 60) - 80, y + 22), "✓ 自动读取", font=font(13, bold=True), fill=GREEN)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "改一次 base_url · 3 端同步 · 维护成本 / 3", font=font(16, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))


# ============ 02: 3 端各自的特点 ============
def img_02():
    img, d = base()

    d.text((60, 40), "3 个端各自的特点", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "功能一致 · 形态不同 · 各有侧重", font=font(15), fill=LIGHT)

    items = [
        ("Codex CLI", "终端命令行", BLUE,
         "✓ 最快进入交互\n✓ 完整 plan 模式\n✓ SSH 远程友好\n✗ 看长输出累"),
        ("Codex 桌面 app", "GUI 客户端", PURPLE,
         "✓ 聊天体验最好\n✓ 多会话标签\n✓ 看推理摘要舒服\n✗ IDE 切换割裂"),
        ("VS Code 插件", "IDE 内嵌", GREEN,
         "✓ 侧边栏内嵌\n✓ 选中代码 → 问 AI\n✓ 看 diff 友好\n✗ VS Code 之外用不上"),
    ]

    bw = (W - 120 - 40) // 3
    bx = 60
    by = 130
    bh = 380

    for i, (name, sub, color, body) in enumerate(items):
        x = bx + i * (bw + 20)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)
        d.text((x + 25, by + 22), name, font=font(22, bold=True), fill=color)
        d.text((x + 25, by + 60), sub, font=font(15), fill=AMBER)
        d.line([(x + 25, by + 95), (x + bw - 25, by + 95)], fill=LINE, width=1)
        for j, line in enumerate(body.split("\n")):
            color_line = GREEN if line.startswith("✓") else RED
            d.text((x + 25, by + 110 + j * 36), line, font=font(13), fill=color_line)

    watermark(d)
    img.save(os.path.join(OUT, "02_three_surfaces.png"))


# ============ 03: 共享配置流程 ============
def img_03():
    img, d = base()

    d.text((60, 40), "配置共享 · 4 个具体收益", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "OpenAI 设计 Codex 时就把配置中枢放在 ~/.codex/", font=font(15), fill=LIGHT)

    items = [
        ("01", "改一次 base_url · 3 端同步", "切换提供商时只改 1 个文件", BLUE),
        ("02", "API key 集中管理", "全部走 OPENAI_API_KEY 环境变量", PURPLE),
        ("03", "模型偏好统一", "reasoning_effort 在 3 端表现一致", AMBER),
        ("04", "沙箱策略一致", "sandbox_mode 在 3 端都生效", GREEN),
    ]

    by = 130
    bh = 95
    spacing = 8

    for i, (num, name, detail, color) in enumerate(items):
        y = by + i * (bh + spacing)
        rrect(d, [60, y, W - 60, y + bh], 12, fill=BOX)
        d.rectangle([60, y, 68, y + bh], fill=color)
        d.text((90, y + 14), num, font=font(20, bold=True), fill=color)
        d.text((150, y + 14), name, font=font(20, bold=True), fill=WHITE)
        d.text((150, y + 50), "→ " + detail, font=font(13), fill=LIGHT)

    # bottom
    rrect(d, [60, 510, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 525), "省下来的不是时间 · 是注意力", font=font(17, bold=True), fill=AMBER)
    d.text((90, 553), "团队管理员维护 1 份模板 · 所有人 3 端通用", font=font(14), fill=GREEN)

    watermark(d)
    img.save(os.path.join(OUT, "03_share_config.png"))


# ============ 04: 3 端使用场景对照 ============
def img_04():
    img, d = base()

    d.text((60, 40), "3 端使用场景对照", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "1 份配置 + 3 个端 = 各种场景都覆盖", font=font(15), fill=LIGHT)

    rows = [
        ("写新模块 / 重构", "VS Code 插件", GREEN),
        ("调奇怪 bug 慢慢聊", "桌面 app", PURPLE),
        ("服务器看日志 / 远程", "CLI", BLUE),
        ("跑 plan 模式自动任务", "CLI", BLUE),
        ("写文档 / README / 注释", "VS Code 插件", GREEN),
        ("周末随手问技术问题", "桌面 app", PURPLE),
        ("团队脚本化任务", "CLI", BLUE),
    ]

    # Header
    hy = 130
    rrect(d, [60, hy, W - 60, hy + 38], 6, fill=DEEP)
    d.text((76, hy + 9), "场景", font=font(14, bold=True), fill=AMBER)
    d.text((640, hy + 9), "推荐端", font=font(14, bold=True), fill=AMBER)

    ry = hy + 48
    rh = 48
    for i, (scene, recommended, color) in enumerate(rows):
        bg = BOX if i % 2 == 0 else DEEP
        rrect(d, [60, ry, W - 60, ry + rh - 4], 6, fill=bg)
        d.rectangle([60, ry, 66, ry + rh - 4], fill=color)
        d.text((76, ry + 14), scene, font=font(15), fill=WHITE)
        d.text((640, ry + 14), recommended, font=font(15, bold=True), fill=color)
        ry += rh

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "调试同一问题来回切端 · 上下文不变 · 工作流最完整", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "04_use_cases.png"))


def main():
    img_01()
    print("[OK] 01_hero.png")
    img_02()
    print("[OK] 02_three_surfaces.png")
    img_03()
    print("[OK] 03_share_config.png")
    img_04()
    print("[OK] 04_use_cases.png")
    print("\nDone:", OUT)


if __name__ == "__main__":
    main()
