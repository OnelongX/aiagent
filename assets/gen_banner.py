# -*- coding: utf-8 -*-
"""Generate GitHub social preview banner"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1280, 640

BG = "#0a0e1a"
BOX = "#1e293b"
WHITE = "#ffffff"
SUB = "#cbd5e1"
LIGHT = "#94a3b8"
DIM = "#64748b"
AMBER = "#fbbf24"
AMBER_LIGHT = "#fde047"

ARTICLE_COLORS = [
    "#06b6d4", "#0891b2", "#fb923c", "#22d3ee", "#a855f7", "#fb923c",
    "#22c55e", "#a855f7", "#06b6d4", "#fb923c", "#ec4899",
    "#14b8a6", "#6366f1", "#fbbf24",
]

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


def tw(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[2] - b[0]


def rrect(d, xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def banner():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    stripe_w = W / 14
    for i, c in enumerate(ARTICLE_COLORS):
        x = int(i * stripe_w)
        d.rectangle([x, 0, int((i + 1) * stripe_w), 8], fill=c)

    rrect(d, [60, 60, 220, 100], 20, fill=AMBER)
    d.text((78, 70), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [236, 60, 460, 100], 20, fill=BOX)
    d.text((254, 70), "Claude Agent SDK", font=font(16, bold=True), fill=AMBER_LIGHT)

    d.text((60, 144), "AI Agent 实战手册", font=font(72, bold=True), fill=AMBER)
    d.text((60, 232), "14 篇 Claude Agent SDK 教程", font=font(32, bold=True), fill=WHITE)
    d.text((60, 274), "从工具栈配置 · 到行业落地 · 到跨行业平移", font=font(24), fill=SUB)

    stats = [("14", "实战教程", "#22d3ee"),
             ("15+", "覆盖行业", "#4ade80"),
             ("5", "工程定律", "#fb923c")]
    sy = 350
    for i, (n, lab, c) in enumerate(stats):
        x = 60 + i * 260
        rrect(d, [x, sy, x + 240, sy + 110], 16, fill=BOX, outline=c, width=2)
        d.text((x + 24, sy + 16), n, font=font(48, bold=True), fill=c)
        d.text((x + 24, sy + 76), lab, font=font(18), fill=SUB)

    tags_y = 502
    d.text((60, tags_y), "TECH STACK", font=mono(13), fill=DIM)
    tags = [("Claude Sonnet 4.5", "#fb923c"), ("GPT-5", "#4ade80"),
            ("Gemini 2.5 Pro", "#60a5fa"), ("MCP", "#c084fc"),
            ("Qdrant", "#14b8a6"), ("RAGAS", "#ec4899")]
    tx = 60
    for tag, c in tags:
        w = tw(d, tag, font(14, bold=True)) + 24
        ty = tags_y + 28
        rrect(d, [tx, ty, tx + w, ty + 32], 16, fill=BOX, outline=c, width=1)
        d.text((tx + 12, ty + 7), tag, font=font(14, bold=True), fill=c)
        tx += w + 10

    d.text((W - 380, H - 90), "github.com/OnelongX/aiagent", font=mono(15), fill=LIGHT)
    d.text((W - 380, H - 64), "公众号:实战复盘", font=font(15, bold=True), fill=AMBER_LIGHT)
    d.text((W - 380, H - 40), "每周更新行业落地实战", font=font(13), fill=DIM)

    img.save(os.path.join(OUT, "banner.png"))
    print(f"[OK] banner.png ({W}x{H})")


def header():
    sw, sh = 1200, 300
    img = Image.new("RGB", (sw, sh), BG)
    d = ImageDraw.Draw(img)

    stripe_w = sw / 14
    for i, c in enumerate(ARTICLE_COLORS):
        x = int(i * stripe_w)
        d.rectangle([x, 0, int((i + 1) * stripe_w), 6], fill=c)

    d.text((40, 50), "AI Agent 实战手册", font=font(56, bold=True), fill=AMBER)
    d.text((40, 130), "14 篇 Claude Agent SDK 实战教程", font=font(22, bold=True), fill=WHITE)
    d.text((40, 168), "工具栈配置 · 行业落地 · 跨行业平移", font=font(18), fill=SUB)

    d.text((40, 218), "14 教程", font=font(16, bold=True), fill="#22d3ee")
    d.text((140, 218), "·", font=font(16), fill=DIM)
    d.text((160, 218), "15+ 行业", font=font(16, bold=True), fill="#4ade80")
    d.text((280, 218), "·", font=font(16), fill=DIM)
    d.text((300, 218), "5 工程定律", font=font(16, bold=True), fill="#fb923c")
    d.text((420, 218), "·", font=font(16), fill=DIM)
    d.text((440, 218), "Claude · GPT-5 · Gemini", font=font(16, bold=True), fill="#c084fc")

    d.text((40, 258), "github.com/OnelongX/aiagent", font=mono(13), fill=LIGHT)
    d.text((300, 258), "公众号:实战复盘", font=font(13, bold=True), fill=AMBER_LIGHT)

    img.save(os.path.join(OUT, "header.png"))
    print(f"[OK] header.png ({sw}x{sh})")


if __name__ == "__main__":
    banner()
    header()
