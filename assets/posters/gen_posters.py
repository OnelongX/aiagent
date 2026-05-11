# -*- coding: utf-8 -*-
"""5 张推广海报 · 朋友圈方图 + 小红书竖图

输出到 ./posters/ 下,直接发朋友圈 / 小红书。
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE     = os.path.dirname(os.path.abspath(__file__))
OUT      = HERE  # 输出到当前目录
QR_PATH  = os.path.join(os.path.dirname(HERE), "wechat-qrcode.png")

# Colors
BG_DARK   = "#0b1220"
BG_NAVY   = "#0f172a"
BOX       = "#1e293b"
DEEP      = "#070d18"
LINE      = "#334155"
WHITE     = "#ffffff"
SUB       = "#cbd5e1"
LIGHT     = "#94a3b8"
DIM       = "#64748b"
AMBER     = "#fbbf24"
AMBER_L   = "#fde047"
AMBER_D   = "#f59e0b"
GOLD      = "#eab308"
ORANGE    = "#fb923c"
ORANGE_L  = "#fdba74"
GREEN     = "#22c55e"
GREEN_L   = "#4ade80"
EMERALD   = "#10b981"
CYAN      = "#06b6d4"
CYAN_L    = "#22d3ee"
TEAL      = "#14b8a6"
BLUE      = "#3b82f6"
BLUE_L    = "#60a5fa"
INDIGO    = "#6366f1"
VIOLET    = "#8b5cf6"
PURPLE    = "#a855f7"
PURPLE_L  = "#c084fc"
PINK      = "#ec4899"
ROSE      = "#f43f5e"
RED       = "#ef4444"
RED_L     = "#fca5a5"
LIME      = "#84cc16"

REG   = r"C:\Windows\Fonts\msyh.ttc"
BOLD  = r"C:\Windows\Fonts\msyhbd.ttc"
MONO  = r"C:\Windows\Fonts\consola.ttf"
EMOJI = r"C:\Windows\Fonts\seguisym.ttf"   # Segoe UI Symbol · 支持 ❌✅★●→ 等


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def sym(size, bold=False):
    """符号字体 · 用于 ✓ ✗ ★ → ● 等 msyh 不渲染的字符"""
    try:
        return ImageFont.truetype(EMOJI, size)
    except Exception:
        return font(size, bold)


def tw(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[2] - b[0]


def th(d, t, f):
    b = d.textbbox((0, 0), t, font=f)
    return b[3] - b[1]


def rrect(d, xy, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


def vertical_gradient(W, H, top, bottom):
    """生成竖向渐变背景"""
    img = Image.new("RGB", (W, H), top)
    px = img.load()
    tr, tg, tb = Image.new("RGB", (1, 1), top).getpixel((0, 0))
    br, bg, bb = Image.new("RGB", (1, 1), bottom).getpixel((0, 0))
    for y in range(H):
        r = tr + (br - tr) * y // H
        g = tg + (bg - tg) * y // H
        b = tb + (bb - tb) * y // H
        for x in range(W):
            px[x, y] = (r, g, b)
    return img


def paste_qr(img, x, y, size=200, border=True):
    """在 (x, y) 粘贴公众号二维码"""
    if not os.path.exists(QR_PATH):
        return
    qr = Image.open(QR_PATH).convert("RGB")
    # 原图是绿底带文字 · 缩到 size
    qr = qr.resize((size, int(qr.height * size / qr.width)), Image.LANCZOS)
    if border:
        d = ImageDraw.Draw(img)
        b = 8
        rrect(d,
              [x - b, y - b, x + qr.width + b, y + qr.height + b],
              16, fill=WHITE)
    img.paste(qr, (x, y))


def watermark(d, W, H):
    d.text((W - 220, H - 36), "实战复盘 · IamOnelong", font=font(15), fill=DIM)


def github_url(d, W, y, color=AMBER_L):
    txt = "github.com/OnelongX/aiagent"
    f = font(20, bold=True)
    w = tw(d, txt, f)
    d.text(((W - w) // 2, y), txt, font=f, fill=color)


# ============ 海报 1 · 朋友圈方图 1080×1080 · 数字震撼 ============
def poster_01_square():
    W, H = 1080, 1080
    img = vertical_gradient(W, H, "#0a0f1e", "#1a2540")
    d = ImageDraw.Draw(img)

    # 顶部 badge
    rrect(d, [W // 2 - 200, 60, W // 2 + 200, 110], 25, fill=AMBER)
    bf = font(22, bold=True)
    btxt = "实战复盘 · GitHub 全开源"
    d.text(((W - tw(d, btxt, bf)) // 2, 70), btxt, font=bf, fill=BG_NAVY)

    # 主标题
    title1 = "13 个行业"
    title2 = "1 套骨架"
    f_big = font(96, bold=True)
    d.text(((W - tw(d, title1, f_big)) // 2, 160), title1, font=f_big, fill=AMBER)
    d.text(((W - tw(d, title2, f_big)) // 2, 274), title2, font=f_big, fill=WHITE)

    sub = "我把 AI Agent 代码全开源了"
    sf = font(28, bold=True)
    d.text(((W - tw(d, sub, sf)) // 2, 400), sub, font=sf, fill=ORANGE_L)

    # 4 个大数字
    stats = [
        ("22+", "篇实战",    AMBER),
        ("13",  "个行业",    ORANGE),
        ("8",   "全栈代码",  GREEN_L),
        ("6",   "工程定律",  PURPLE_L),
    ]
    sx, sy = 80, 470
    cw, ch, gap = 215, 200, 20
    for i, (num, label, c) in enumerate(stats):
        x = sx + i * (cw + gap)
        rrect(d, [x, sy, x + cw, sy + ch], 18, fill=BOX, outline=c, width=3)
        # 数字
        nf = font(70, bold=True)
        d.text((x + (cw - tw(d, num, nf)) // 2, sy + 28), num, font=nf, fill=c)
        # 标签
        lf = font(20, bold=True)
        d.text((x + (cw - tw(d, label, lf)) // 2, sy + 130), label, font=lf, fill=SUB)

    # 行业 chips
    industries = [
        ("法律",  PURPLE), ("教育",  EMERALD), ("医疗",  PINK),
        ("金融",  GOLD),   ("制造",  ORANGE),  ("绿电",  GREEN),
        ("电商",  ROSE),   ("客服",  TEAL),    ("内容",  CYAN_L),
    ]
    iy = 720
    cw = 110
    gap_x = 8
    total = len(industries) * (cw + gap_x) - gap_x
    start_x = (W - total) // 2
    for i, (name, c) in enumerate(industries):
        x = start_x + i * (cw + gap_x)
        rrect(d, [x, iy, x + cw, iy + 50], 12, fill=BOX, outline=c, width=2)
        f = font(22, bold=True)
        d.text((x + (cw - tw(d, name, f)) // 2, iy + 12), name, font=f, fill=c)

    # 二维码 + URL
    paste_qr(img, 80, 830, size=180)
    d.text((300, 850), "扫码关注「实战复盘」", font=font(28, bold=True), fill=WHITE)
    d.text((300, 894), "公众号:IamOnelong", font=font(20), fill=AMBER_L)
    d.text((300, 930), "每周更新 AI Agent 行业落地实战", font=font(18), fill=SUB)
    d.text((300, 968), "github.com/OnelongX/aiagent", font=font(20, bold=True), fill=AMBER)

    watermark(d, W, H)
    img.save(os.path.join(OUT, "01_square_friends.png"))
    print("[OK] 01_square_friends · 朋友圈方图")


# ============ 海报 2 · 小红书首图 1080×1440 · 红线对照 ============
def poster_02_xhs_redlines():
    W, H = 1080, 1440
    img = vertical_gradient(W, H, "#0a0f1e", "#1a2540")
    d = ImageDraw.Draw(img)

    # 顶部
    rrect(d, [60, 60, 280, 110], 25, fill=AMBER)
    d.text((96, 72), "实战复盘", font=font(22, bold=True), fill=BG_NAVY)

    # 钩子标题
    hook = "做 AI 项目前"
    title = "先抄这张表"
    f_hook = font(50, bold=True)
    f_big  = font(76, bold=True)
    d.text((60, 170), hook, font=f_hook, fill=WHITE)
    d.text((60, 240), title, font=f_big, fill=AMBER)
    d.text((60, 340), "5 大重监管行业 · AI 红线对照", font=font(26, bold=True), fill=ORANGE_L)
    d.text((60, 380), "给法务 / 合规的一页 brief", font=font(20), fill=SUB)

    # 5 行行业卡
    industries = [
        ("法律",  PURPLE,  "执业责任",       "AI 不下结论"),
        ("教育",  EMERALD, "未成年保护",     "AI 不贴标签"),
        ("医疗",  PINK,    "执业 + 生命",     "AI 不下诊断"),
        ("金融",  GOLD,    "持牌 + 投保",     "AI 不荐股"),
        ("制造",  ORANGE,  "物理 + 工艺密",   "AI 不越边界"),
    ]
    y0 = 460
    for i, (name, c, redline, cannot) in enumerate(industries):
        y = y0 + i * 110
        rrect(d, [60, y, W - 60, y + 96], 16, fill=BOX, outline=c, width=3)
        # 行业 tag
        rrect(d, [80, y + 22, 240, y + 74], 12, fill=c)
        d.text((100, y + 32), name, font=font(28, bold=True), fill=BG_NAVY)
        # 红线
        d.text((270, y + 18), "红线类型", font=font(15), fill=DIM)
        d.text((270, y + 44), redline, font=font(24, bold=True), fill=WHITE)
        # cannot
        d.text((680, y + 18), "AI 不能", font=font(15), fill=DIM)
        d.text((680, y + 44), cannot, font=font(24, bold=True), fill=c)

    # 干货底部
    rrect(d, [60, 1030, W - 60, 1130], 18, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 1050), "★ 13 篇行业落地代码全开源", font=font(26, bold=True), fill=AMBER_L)
    d.text((80, 1088), "FastAPI + Docker · 5 分钟跑通", font=font(18), fill=SUB)

    # 二维码 + URL
    paste_qr(img, 60, 1180, size=200)
    d.text((300, 1200), "扫码关注公众号", font=font(28, bold=True), fill=WHITE)
    d.text((300, 1244), "→ IamOnelong", font=font(24, bold=True), fill=AMBER_L)
    d.text((300, 1284), "github.com/OnelongX/aiagent", font=font(20, bold=True), fill=AMBER)
    d.text((300, 1320), "#AIAgent #ClaudeCode #开源项目 #法律 #医疗", font=font(15), fill=LIGHT)

    watermark(d, W, H)
    img.save(os.path.join(OUT, "02_xhs_redlines.png"))
    print("[OK] 02_xhs_redlines · 小红书红线对照")


# ============ 海报 3 · 小红书 1080×1440 · 13 篇全景 ============
def poster_03_xhs_landscape():
    W, H = 1080, 1440
    img = vertical_gradient(W, H, "#0a0f1e", "#1a2540")
    d = ImageDraw.Draw(img)

    rrect(d, [60, 60, 280, 110], 25, fill=AMBER)
    d.text((96, 72), "实战复盘", font=font(22, bold=True), fill=BG_NAVY)

    # 标题
    d.text((60, 170), "13 篇 AI Agent", font=font(64, bold=True), fill=AMBER)
    d.text((60, 244), "行业落地实战", font=font(64, bold=True), fill=WHITE)
    d.text((60, 340), "从绿电到 MES · 完整可跑代码", font=font(24, bold=True), fill=ORANGE_L)
    d.text((60, 376), "Claude Agent SDK + FastAPI + Docker", font=font(20), fill=SUB)

    # 13 个 case · 3 列 × 5 行(最后一行 3 个)
    cases = [
        ("#1",  "绿电方案",   ORANGE_L),
        ("#2",  "合同审查",   PURPLE_L),
        ("#3",  "知识库",     BLUE_L),
        ("#4",  "企业客服",   TEAL),
        ("#5",  "电商客服",   ROSE),
        ("#6",  "全栈工作台", GREEN_L),
        ("#7",  "Vectorless", CYAN_L),
        ("#8",  "学生论文",   LIME),
        ("#9",  "法律",       PURPLE),
        ("#10", "教育",       EMERALD),
        ("#11", "医疗",       PINK),
        ("#12", "金融",       GOLD),
        ("#13", "制造",       ORANGE),
    ]
    cols = 3
    cw = (W - 120 - (cols - 1) * 16) // cols
    ch = 96
    sx, sy = 60, 460
    for i, (num, name, c) in enumerate(cases):
        col, row = i % cols, i // cols
        x = sx + col * (cw + 16)
        y = sy + row * (ch + 16)
        rrect(d, [x, y, x + cw, y + ch], 14, fill=BOX, outline=c, width=2)
        rrect(d, [x + 12, y + 14, x + 78, y + 44], 8, fill=c)
        d.text((x + 22, y + 18), num, font=font(20, bold=True), fill=BG_NAVY)
        d.text((x + 14, y + 56), name, font=font(22, bold=True), fill=c)

    # 底部
    rrect(d, [60, 1030, W - 60, 1130], 18, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 1050), "★ 8 篇带完整代码 · Docker 5 分钟跑通", font=font(26, bold=True), fill=AMBER_L)
    d.text((80, 1088), "1 套骨架 · 13 种装填 · 模式行业无关", font=font(18), fill=SUB)

    paste_qr(img, 60, 1180, size=200)
    d.text((300, 1200), "★ GitHub 完整开源", font=font(28, bold=True), fill=WHITE)
    d.text((300, 1244), "github.com/OnelongX/aiagent", font=font(22, bold=True), fill=AMBER)
    d.text((300, 1284), "公众号「实战复盘」每周更新", font=font(20), fill=AMBER_L)
    d.text((300, 1320), "#AIAgent #ClaudeCode #FastAPI #全栈", font=font(15), fill=LIGHT)

    watermark(d, W, H)
    img.save(os.path.join(OUT, "03_xhs_landscape.png"))
    print("[OK] 03_xhs_landscape · 小红书 13 篇全景")


# ============ 海报 4 · 朋友圈方图 1080×1080 · 干货向 ============
def poster_04_square_thesis():
    W, H = 1080, 1080
    img = vertical_gradient(W, H, "#0a0f1e", "#1a2540")
    d = ImageDraw.Draw(img)

    # quote 引用框 · 用大字"|" 作引用 bar
    d.rectangle([60, 80, 80, 170], fill=AMBER)
    d.text((100, 80), "干货", font=font(28, bold=True), fill=AMBER)
    d.text((100, 124), "AI Agent 实战", font=font(22, bold=True), fill=ORANGE_L)

    # 大字 thesis
    d.text((60, 200), "写过 13 个", font=font(60, bold=True), fill=WHITE)
    d.text((60, 270), "AI 行业 case", font=font(60, bold=True), fill=WHITE)
    d.text((60, 340), "才悟出的 1 句话:", font=font(60, bold=True), fill=WHITE)

    # 核心 thesis · highlight
    rrect(d, [60, 460, W - 60, 620], 20, fill=DEEP, outline=AMBER, width=3)
    d.text((80, 482), "工程模式行业无关", font=font(46, bold=True), fill=AMBER_L)
    d.text((80, 540), "红线决定形态", font=font(46, bold=True), fill=AMBER)

    # 6 工程定律
    laws = [
        "1. 工具优先 · LLM 不计算",
        "2. 权限在数据层 · 不在 Prompt",
        "3. Subagent 分工 · Haiku 分流",
        "4. Hooks 守红线 · 不让 LLM 决定",
        "5. 评测驱动 · 跌 5% block 上线",
        "6. 红线先于功能 · 熔断不进 LLM",
    ]
    y = 660
    for line in laws:
        d.text((60, y), line, font=font(22, bold=True), fill=SUB)
        y += 36

    # 二维码 + URL
    paste_qr(img, 60, 880, size=160)
    d.text((260, 900), "完整 13 篇综述", font=font(24, bold=True), fill=WHITE)
    d.text((260, 938), "公众号「实战复盘」", font=font(20, bold=True), fill=AMBER_L)
    d.text((260, 974), "IamOnelong", font=font(18), fill=SUB)
    d.text((260, 1010), "github.com/OnelongX/aiagent", font=font(18, bold=True), fill=AMBER)

    watermark(d, W, H)
    img.save(os.path.join(OUT, "04_square_thesis.png"))
    print("[OK] 04_square_thesis · 朋友圈干货向")


# ============ 海报 5 · 小红书首图 1080×1440 · 钩子向 ============
def poster_05_xhs_hook():
    W, H = 1080, 1440
    img = vertical_gradient(W, H, "#0a0f1e", "#1a2540")
    d = ImageDraw.Draw(img)

    rrect(d, [60, 60, 280, 110], 25, fill=AMBER)
    d.text((96, 72), "实战复盘", font=font(22, bold=True), fill=BG_NAVY)

    # 钩子 · 大字提问
    d.text((60, 170), "做 AI Agent", font=font(64, bold=True), fill=WHITE)
    d.text((60, 244), "卡在哪一步?", font=font(64, bold=True), fill=AMBER)

    # 痛点列表
    rrect(d, [60, 350, W - 60, 720], 18, fill=BOX, outline=ORANGE_L, width=2)
    d.text((90, 374), "你是不是也卡在这里 ↓", font=font(28, bold=True), fill=ORANGE_L)

    pains = [
        "以为 Agent = 一个超大 Prompt",
        "不知道用 Claude 还是 GPT 还是 Gemini",
        "知道要做但不知道怎么拆工具",
        "怕合规怕红线不敢上线",
        "看了一堆教程仍然写不出 MVP",
    ]
    y = 430
    for text in pains:
        # 用红色方块代替 ❌
        d.rectangle([100, y + 6, 132, y + 38], fill=RED)
        d.text((108, y + 4), "✗", font=sym(28, bold=True), fill=WHITE)
        d.text((150, y), text, font=font(22, bold=True), fill=SUB)
        y += 56

    # 解药
    rrect(d, [60, 750, W - 60, 1010], 18, fill=DEEP, outline=AMBER, width=3)
    items = [
        ("13 篇行业落地实战 · 全开源",        AMBER_L,  True),
        ("5 大重监管行业(法/教/医/金/制)",   GREEN_L, False),
        ("8 篇带完整可跑代码",                GREEN_L, False),
        ("6 大行业无关的工程定律",            GREEN_L, False),
        ("AI 红线工具箱 5 个模板",            GREEN_L, False),
        ("Docker 5 分钟跑通",                 GREEN_L, False),
    ]
    y = 772
    for text, c, is_title in items:
        # 绿色对勾方块代替 ✅
        d.rectangle([80, y + 4, 112, y + 36], fill=EMERALD)
        d.text((87, y + 2), "✓", font=sym(28, bold=True), fill=WHITE)
        size = 28 if is_title else 22
        d.text((130, y), text, font=font(size, bold=True), fill=c)
        y += 42

    # 二维码 + URL
    paste_qr(img, 60, 1080, size=200)
    d.text((300, 1100), "扫码免费领", font=font(32, bold=True), fill=WHITE)
    d.text((300, 1150), "→ 公众号:IamOnelong", font=font(24, bold=True), fill=AMBER_L)
    d.text((300, 1195), "github.com/OnelongX/aiagent", font=font(20, bold=True), fill=AMBER)
    d.text((300, 1235), "Star 收藏 · 每周更新", font=font(18), fill=SUB)
    d.text((300, 1280), "#AIAgent #Claude #开源 #FastAPI", font=font(14), fill=LIGHT)

    watermark(d, W, H)
    img.save(os.path.join(OUT, "05_xhs_hook.png"))
    print("[OK] 05_xhs_hook · 小红书钩子向")


if __name__ == "__main__":
    poster_01_square()
    poster_02_xhs_redlines()
    poster_03_xhs_landscape()
    poster_04_square_thesis()
    poster_05_xhs_hook()
    print("\n[DONE] 5 posters saved to", OUT)
