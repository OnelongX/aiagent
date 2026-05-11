# -*- coding: utf-8 -*-
"""5 images for Hermes Agent + OpenClaw 教程 - 1080x600"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\HermesOpenClaw配置"
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
ROSE = "#f43f5e"
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


# ============ 01: HERO ============
def img_01():
    img, d = base()

    rrect(d, [60, 50, 240, 88], 19, fill=ROSE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)

    rrect(d, [256, 50, 460, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 5/5 收官", font=font(18, bold=True), fill=AMBER)

    d.text((60, 130), "Hermes Agent + OpenClaw", font=font(34, bold=True), fill=AMBER)
    d.text((60, 178), "让 AI 走出 IDE · 接入你的所有聊天平台", font=font(20, bold=True), fill=WHITE)
    d.text((60, 220), "20+ 平台 · 自我改进 · 一个 token 跑 5 工具栈", font=font(15), fill=LIGHT)

    items = [
        ("Hermes", "自我改进 AI agent", "Nous Research\n跨会话学习 · 持久化\n20+ 平台", INDIGO),
        ("OpenClaw", "自托管个人 AI 网关", "openclaw.ai\n本地 gateway · 数据不外发\n22+ 聊天渠道", LIME),
    ]

    by = 270
    bw = (W - 120 - 30) // 2
    bh = 230

    for i, (name, sub, body, color) in enumerate(items):
        x = 60 + i * (bw + 30)
        rrect(d, [x, by, x + bw, by + bh], 14, fill=BOX, outline=color, width=2)
        d.rectangle([x, by, x + 8, by + bh], fill=color)
        d.text((x + 25, by + 18), name, font=font(28, bold=True), fill=color)
        d.text((x + 25, by + 60), sub, font=font(15, bold=True), fill=AMBER)
        d.line([(x + 25, by + 100), (x + bw - 25, by + 100)], fill=LINE, width=1)
        for j, line in enumerate(body.split("\n")):
            d.text((x + 25, by + 116 + j * 32), line, font=font(13), fill=SUB)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "5 工具栈完整版 · Codex + Claude Code + opencode + Hermes + OpenClaw", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))


# ============ 02: Hermes vs OpenClaw 对比 ============
def img_02():
    img, d = base()

    d.text((60, 40), "Hermes Agent vs OpenClaw 对比", font=font(28, bold=True), fill=WHITE)
    d.text((60, 84), "AI 走出 IDE · 接入你日常用的平台", font=font(15), fill=LIGHT)

    hy = 130
    rrect(d, [60, hy, W - 60, hy + 38], 6, fill=DEEP)
    d.text((76, hy + 9), "维度", font=font(13, bold=True), fill=AMBER)
    d.text((360, hy + 9), "Hermes Agent", font=font(13, bold=True), fill=INDIGO)
    d.text((720, hy + 9), "OpenClaw", font=font(13, bold=True), fill=LIME)

    rows = [
        ("厂商", "Nous Research", "openclaw.ai 社区"),
        ("定位", "自我改进 AI agent", "自托管 AI 网关"),
        ("CLI / TUI", "hermes / hermes --tui", "openclaw onboard"),
        ("跨平台", "20+ 平台", "22+ 聊天渠道"),
        ("特色", "学习 loop · 跨会话记忆", "本地 gateway · 数据不外发"),
        ("模型", "OpenAI / Claude / 自定义", "OpenAI / Claude / OR"),
    ]

    ry = hy + 48
    rh = 55
    for i, (k, h, o) in enumerate(rows):
        bg = BOX if i % 2 == 0 else DEEP
        rrect(d, [60, ry, W - 60, ry + rh - 4], 6, fill=bg)
        d.text((76, ry + 16), k, font=font(13, bold=True), fill=AMBER)
        d.text((360, ry + 16), h, font=font(13), fill=WHITE)
        d.text((720, ry + 16), o, font=font(13), fill=WHITE)
        ry += rh

    # bottom
    rrect(d, [60, ry + 6, W - 60, ry + 60], 8, fill=DEEP, outline=AMBER, width=2)
    d.text((80, ry + 22), "Hermes 跨会话学习 · OpenClaw 跨平台接入", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "02_compare.png"))


# ============ 03: Hermes Self-Improving Loop ============
def img_03():
    img, d = base()

    d.text((60, 40), "Hermes 杀招 · Self-Improving Loop", font=font(26, bold=True), fill=INDIGO)
    d.text((60, 84), "其他 agent 没有 · 跨会话学习 + 持久化记忆", font=font(15), fill=LIGHT)

    items = [
        ("01", "Skill Creation", "用过的工具 / 流程", "→ 自动沉淀为可复用 skill", BLUE),
        ("02", "Skill Improvement", "同一 skill 反复用", "→ 自动改进版本", PURPLE),
        ("03", "Knowledge Persistence", "重要事实", "→ 自动记忆 · 跨会话保留", AMBER),
        ("04", "User Model Deepening", "你的偏好 / 习惯 / 项目背景", "→ 越用越懂你", GREEN),
    ]

    by = 130
    bh = 78
    spacing = 8

    for i, (num, name, source, effect, color) in enumerate(items):
        y = by + i * (bh + spacing)
        rrect(d, [60, y, W - 60, y + bh], 12, fill=BOX)
        d.rectangle([60, y, 68, y + bh], fill=color)
        d.text((90, y + 14), num, font=font(20, bold=True), fill=color)
        d.text((150, y + 14), name, font=font(18, bold=True), fill=WHITE)
        d.text((150, y + 46), source, font=font(13), fill=LIGHT)
        d.text((620, y + 28), effect, font=font(13, bold=True), fill=GREEN)

    # bottom
    rrect(d, [60, 510, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 525), "3-5 次会话后开始有感觉 · 第 10 次会话起 = 像跟你工作很久的同事", font=font(15, bold=True), fill=AMBER)
    d.text((90, 553), "Codex / Claude Code / opencode 都没有这个能力", font=font(13), fill=GREEN)

    watermark(d)
    img.save(os.path.join(OUT, "03_hermes_loop.png"))


# ============ 04: OpenClaw 22+ 平台 ============
def img_04():
    img, d = base()

    d.text((60, 40), "OpenClaw · 22+ 聊天平台接入", font=font(28, bold=True), fill=LIME)
    d.text((60, 84), "本地 gateway · 数据不出你的机器", font=font(15), fill=LIGHT)

    # Top: gateway architecture
    py = 130
    rrect(d, [60, py, W - 60, py + 100], 14, fill=BOX, outline=LIME, width=2)
    d.rectangle([60, py, 68, py + 100], fill=LIME)
    d.text((85, py + 14), "本地 Gateway 架构", font=font(17, bold=True), fill=LIME)
    d.text((85, py + 44), "你的机器 (127.0.0.1:7878)", font=mono(13), fill=WHITE)
    d.text((85, py + 66), "→ 转发到聊天平台 (22+ 渠道)", font=mono(13), fill=AMBER)
    d.text((85, py + 84), "→ 调用 AI provider (livetoken / OpenAI / Claude)", font=mono(13), fill=GREEN)

    # 平台 grid (22+ channels)
    channels = [
        ("微信", PINK), ("QQ", BLUE), ("飞书", PURPLE), ("Telegram", CYAN),
        ("Slack", AMBER), ("Discord", INDIGO), ("WhatsApp", GREEN), ("iMessage", BLUE),
        ("Teams", PURPLE), ("Signal", BLUE), ("LINE", GREEN), ("Matrix", AMBER),
        ("Mattermost", BLUE), ("Google Chat", AMBER), ("Twitch", PURPLE), ("WebChat", LIME),
    ]

    by = 250
    cw = (W - 120 - 60) // 8
    ch = 35
    spacing_x = 8
    spacing_y = 8

    for i, (name, color) in enumerate(channels):
        x = 60 + (i % 8) * (cw + spacing_x)
        y = by + (i // 8) * (ch + spacing_y)
        rrect(d, [x, y, x + cw, y + ch], 8, fill=BOX, outline=color, width=1)
        f_ch = font(13, bold=True)
        ch_w = tw(d, name, f_ch)
        d.text((x + (cw - ch_w) // 2, y + 8), name, font=f_ch, fill=color)

    # 还有 6+ 更多
    d.text((60, by + 110), "+ Nextcloud Talk · Tlon · Zalo · IRC · Synology · Nostr 等 6+ 渠道", font=font(13), fill=LIGHT)

    # bottom
    rrect(d, [60, 480, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 495), "openclaw onboard · 引导式配置 5 步", font=font(16, bold=True), fill=AMBER)
    d.text((90, 525), "1. Gateway · 2. Workspace · 3. Channels · 4. Skills · 5. API providers", font=font(13), fill=WHITE)
    d.text((90, 553), "数据不外发 · 全部跑在你机器上 · 隐私优先", font=font(13, bold=True), fill=GREEN)

    watermark(d)
    img.save(os.path.join(OUT, "04_openclaw.png"))


# ============ 05: 5 工具栈 终极方案 ============
def img_05():
    img, d = base()

    d.text((60, 40), "5 工具栈 · 一个 token 跑全部", font=font(28, bold=True), fill=AMBER)
    d.text((60, 84), "AI 工作流的极致方案 · IDE 内 + IDE 外 + 跨平台", font=font(15), fill=LIGHT)

    items = [
        ("01", "Codex", "OpenAI · IDE 写代码", "GPT-5 系列", BLUE),
        ("02", "Claude Code", "Anthropic · 重构 / Plan", "Claude 系列", ORANGE),
        ("03", "opencode", "开源 · 多模型聚合", "75+ 模型", LIME),
        ("04", "Hermes", "Nous · 自我改进 agent", "跨会话记忆", INDIGO),
        ("05", "OpenClaw", "自托管 · 跨平台网关", "22+ 聊天渠道", ROSE),
    ]

    by = 130
    bh = 70
    spacing = 7

    for i, (num, name, role, model, color) in enumerate(items):
        y = by + i * (bh + spacing)
        rrect(d, [60, y, W - 60, y + bh], 12, fill=BOX)
        d.rectangle([60, y, 68, y + bh], fill=color)
        d.text((90, y + 14), num, font=font(20, bold=True), fill=color)
        d.text((150, y + 14), name, font=font(20, bold=True), fill=WHITE)
        d.text((150, y + 44), role, font=font(13), fill=LIGHT)
        d.text((720, y + 26), model, font=font(13, bold=True), fill=AMBER)

    # bottom
    rrect(d, [60, 525, W - 60, 580], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((90, 540), "5 工具 + 1 个 livetoken token = 完整 AI 工作流", font=font(15, bold=True), fill=AMBER)

    watermark(d)
    img.save(os.path.join(OUT, "05_full_stack.png"))


def main():
    img_01()
    print("[OK] 01_hero.png")
    img_02()
    print("[OK] 02_compare.png")
    img_03()
    print("[OK] 03_hermes_loop.png")
    img_04()
    print("[OK] 04_openclaw.png")
    img_05()
    print("[OK] 05_full_stack.png")
    print("\nDone:", OUT)


if __name__ == "__main__":
    main()
