# -*- coding: utf-8 -*-
"""5 images for 二手手机 Agent · 跨行业平移第 1 篇"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\二手手机Agent"
W, H = 1080, 600

BG = "#0f172a"
BOX = "#1e293b"
DEEP = "#0b1220"
LINE = "#334155"
WHITE = "#ffffff"
SUB = "#cbd5e1"
LIGHT = "#94a3b8"
DIM = "#64748b"
AMBER = "#fbbf24"
RED = "#ef4444"
GREEN = "#22c55e"
GREEN_LIGHT = "#4ade80"
PURPLE = "#a855f7"
PURPLE_LIGHT = "#c084fc"
BLUE = "#3b82f6"
BLUE_LIGHT = "#60a5fa"
CYAN = "#06b6d4"
ORANGE = "#fb923c"
ORANGE_LIGHT = "#fdba74"
PINK = "#ec4899"
ROSE = "#f43f5e"
TEAL = "#14b8a6"
TEAL_LIGHT = "#5eead4"
EMERALD = "#10b981"
EMERALD_LIGHT = "#34d399"
LIME = "#84cc16"
INDIGO = "#6366f1"

# 三引擎色
CLAUDE_C = "#fb923c"   # orange
GPT_C    = "#4ade80"   # green
GEMINI_C = "#60a5fa"   # blue

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

    rrect(d, [60, 50, 240, 88], 19, fill=TEAL)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 560, 88], 19, fill=BOX)
    d.text((274, 56), "跨行业平移 · 第 1 篇", font=font(17, bold=True), fill=AMBER)

    d.text((60, 128), "二手手机推荐 + 售卖", font=font(38, bold=True), fill=AMBER)
    d.text((60, 184), "2B/2C 双线 + 微信", font=font(26, bold=True), fill=WHITE)
    d.text((60, 220), "生态全打通", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("Claude",  CLAUDE_C,  "大脑 · 推理"),
        ("GPT-5",   GPT_C,     "会计 · 数字"),
        ("Gemini",  GEMINI_C,  "质检员 · 报告"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=TEAL, width=2)
    d.text((80, 442), "把绿电电商的工程模式 · 平移到二手 3C", font=font(20, bold=True), fill=TEAL_LIGHT)
    d.text((80, 478), "首次跨行业平移 · 验证模式可复用", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 跟绿电对比 ============
def img_02():
    img, d = base()
    d.text((60, 40), "跟绿电电商的 7 个核心差异", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "工程上比绿电更难 · 但模式相同", font=font(15), fill=LIGHT)

    rows = [
        ("SKU",     "标品 · 统一价",      "每台 IMEI 唯一",          TEAL),
        ("推荐",    "不需要 · 出方案",    "必须有引擎 + 库存平衡",   GREEN),
        ("客群",    "单一 2C",            "2C + 2B 双线",            BLUE),
        ("检测",    "厂保",               "12 项报告 + Gemini 解读", GEMINI_C),
        ("议价",    "一口价",             "2C 小议 + 2B 阶梯谈判",   ORANGE),
        ("渠道",    "网页为主",           "微信 4 触点全打通",       PINK),
        ("模型",    "Claude + GPT-5",     "Claude + GPT-5 + Gemini", PURPLE),
    ]
    y0 = 120
    rrect(d, [60, y0, 1020, y0 + 34], 8, fill=BOX)
    d.text((80, y0 + 8), "维度", font=font(14, bold=True), fill=AMBER)
    d.text((230, y0 + 8), "绿电电商 #5", font=font(14, bold=True), fill=PINK)
    d.text((600, y0 + 8), "二手手机(本篇)", font=font(14, bold=True), fill=TEAL_LIGHT)

    for i, (dim, a, b, c) in enumerate(rows):
        y = y0 + 46 + i * 50
        rrect(d, [60, y, 1020, y + 42], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 42], fill=c)
        d.text((80, y + 13), dim, font=font(16, bold=True), fill=WHITE)
        d.text((230, y + 13), a, font=font(13), fill=LIGHT)
        d.text((600, y + 13), b, font=font(14, bold=True), fill=TEAL_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "02_diff.png"))
    print("[OK] 02_diff")


# ============ 03: 双流水线 ============
def img_03():
    img, d = base()
    d.text((60, 40), "2C 零售 + 2B 批发 · 双流水线", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "共享底层 · prompt / 工具 / Subagent 完全分离", font=font(15), fill=LIGHT)

    # 2C line
    rrect(d, [60, 116, 200, 156], 8, fill=BLUE)
    d.text((76, 124), "2C", font=font(20, bold=True), fill=BG)
    d.text((116, 124), "零售线", font=font(17, bold=True), fill=WHITE)

    stages_c = [("咨询", BLUE_LIGHT), ("推荐", CYAN), ("看图", CYAN),
                ("议价", AMBER), ("下单", ORANGE), ("物流", PINK), ("售后", PURPLE_LIGHT)]
    y0 = 170
    bw = 124
    gap = 8
    for i, (name, c) in enumerate(stages_c):
        x = 60 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 50], 10, fill=BOX, outline=c, width=2)
        d.text((x + 14, y0 + 16), name, font=font(15, bold=True), fill=c)
        if i < len(stages_c) - 1:
            ax = x + bw + 1
            d.line([(ax, y0 + 25), (ax + 6, y0 + 25)], fill=LINE, width=2)
            d.polygon([(ax + 8, y0 + 25), (ax + 3, y0 + 21), (ax + 3, y0 + 29)], fill=LINE)

    # 2B line
    rrect(d, [60, 256, 200, 296], 8, fill=ORANGE)
    d.text((76, 264), "2B", font=font(20, bold=True), fill=BG)
    d.text((116, 264), "批发线", font=font(17, bold=True), fill=WHITE)

    stages_b = [("询价", ORANGE_LIGHT), ("资质", AMBER), ("报价", GREEN_LIGHT),
                ("验货", BLUE_LIGHT), ("合同", PURPLE), ("PO", PINK), ("账期", ROSE)]
    y1 = 310
    for i, (name, c) in enumerate(stages_b):
        x = 60 + i * (bw + gap)
        rrect(d, [x, y1, x + bw, y1 + 50], 10, fill=BOX, outline=c, width=2)
        d.text((x + 14, y1 + 16), name, font=font(15, bold=True), fill=c)
        if i < len(stages_b) - 1:
            ax = x + bw + 1
            d.line([(ax, y1 + 25), (ax + 6, y1 + 25)], fill=LINE, width=2)
            d.polygon([(ax + 8, y1 + 25), (ax + 3, y1 + 21), (ax + 3, y1 + 29)], fill=LINE)

    # shared底层
    rrect(d, [60, 392, 1020, 510], 14, fill=DEEP, outline=TEAL, width=2)
    d.text((80, 408), "共享底层", font=font(17, bold=True), fill=TEAL_LIGHT)
    items = [
        "· SKU 库 (每台 IMEI 唯一 + 12 项检测)",
        "· OMS / 库存 / 物流 / 财务",
        "· 微信生态(公众号 / 小程序 / 企微 / 视频号)",
        "· Claude + GPT-5 + Gemini 三引擎",
    ]
    for i, item in enumerate(items):
        col = i % 2
        row = i // 2
        d.text((80 + col * 470, 438 + row * 30), item, font=font(13), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "03_dual_flow.png"))
    print("[OK] 03_dual_flow")


# ============ 04: 微信生态 4 触点 ============
def img_04():
    img, d = base()
    d.text((60, 40), "微信生态 4 触点 · 1 套 backend", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "OpenID / UnionID 跨平台串号 · 统一 Agent 编排", font=font(15), fill=LIGHT)

    # 4 触点 in row
    touchpoints = [
        ("公众号",      "Service",       "OpenID-A · 48h 客服窗口",     GREEN,    "🟢"),
        ("小程序",      "Mini Prog",     "OpenID-A · 内置客服 + 支付",  BLUE,     "🔵"),
        ("企业微信",    "Work",          "External UID · 1v1 + 群机器人", ORANGE, "🟠"),
        ("视频号",      "Channels",      "OpenID-A · 私信 + 直播弹幕",   PINK,    "🟣"),
    ]
    y0 = 120
    bw = 240
    gap = 12
    for i, (name, en, desc, c, _) in enumerate(touchpoints):
        x = 60 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 132], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x + 12, y0 + 12, x + bw - 12, y0 + 48], 8, fill=c)
        d.text((x + 22, y0 + 18), name, font=font(18, bold=True), fill=BG)
        d.text((x + 12, y0 + 62), en, font=mono(13), fill=c)
        d.text((x + 12, y0 + 88), desc[:18], font=font(12), fill=SUB)
        if len(desc) > 18:
            d.text((x + 12, y0 + 108), desc[18:], font=font(12), fill=SUB)

    # arrows converging
    for i in range(4):
        x = 60 + i * (bw + gap) + bw // 2
        d.line([(x, 260), (540, 304)], fill=LINE, width=1)

    # unionid layer
    rrect(d, [380, 296, 700, 348], 10, fill=BOX, outline=TEAL, width=2)
    d.text((396, 308), "统一用户中台 (unionid 串)", font=font(15, bold=True), fill=TEAL_LIGHT)

    d.line([(540, 350), (540, 380)], fill=LINE, width=2)
    d.polygon([(540, 388), (534, 380), (546, 380)], fill=LINE)

    # agent
    rrect(d, [320, 394, 760, 458], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((360, 406), "Claude Agent SDK", font=font(20, bold=True), fill=AMBER)
    d.text((360, 432), "orchestrator · 5 Subagent · 20 工具", font=font(13), fill=SUB)

    # bottom: 关键纪律
    rrect(d, [60, 478, 1020, 514], 8, fill=DEEP, outline=RED, width=1)
    d.text((80, 488), "纪律:OpenID ≠ UnionID · 48h 窗口 · 企微不能主动发 · 弹幕走限流", font=font(13, bold=True), fill="#fca5a5")

    watermark(d)
    img.save(os.path.join(OUT, "04_wechat.png"))
    print("[OK] 04_wechat")


# ============ 05: 三引擎 + 4 周路线 ============
def img_05():
    img, d = base()
    d.text((60, 40), "三引擎分配 + 4 周落地", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "按任务分模型 · 不要二选一", font=font(15), fill=LIGHT)

    # 三引擎 task table
    tasks = [
        ("检测报告解读",       "Gemini 2.5 Pro",      GEMINI_C),
        ("2C 推荐对话 / 共情", "Claude Sonnet 4.5",   CLAUDE_C),
        ("2B 阶梯报价谈判",    "GPT-5",                GPT_C),
        ("风控打分",           "GPT-5",                GPT_C),
        ("客服话术 / 售后",    "Claude Sonnet 4.5",   CLAUDE_C),
        ("库存平衡排序",       "不用 LLM",             LIGHT),
    ]
    y0 = 116
    for i, (task, model, c) in enumerate(tasks):
        col = i % 2
        row = i // 2
        x = 60 + col * 490
        y = y0 + row * 56
        rrect(d, [x, y, x + 472, y + 46], 8, fill=BOX)
        d.rectangle([x, y, x + 4, y + 46], fill=c)
        d.text((x + 16, y + 14), task, font=font(14, bold=True), fill=WHITE)
        bw = tw(d, model, mono(13)) + 16
        rrect(d, [x + 472 - bw - 10, y + 13, x + 472 - 10, y + 33], 8, fill=DEEP)
        d.text((x + 472 - bw - 2, y + 14), model, font=mono(13), fill=c)

    # 4 weeks
    d.text((60, 304), "4 周落地路线", font=font(17, bold=True), fill=AMBER)
    weeks = [
        ("W1", "2C 推荐 + 公众号",   "推荐引擎 + 客服消息",       CYAN),
        ("W2", "下单 + 支付 + 物流", "微信支付 · IMEI 锁 · ¥3000", PINK),
        ("W3", "2B 批发 + 企微",     "信用线 · 阶梯 · 法大大",     ORANGE),
        ("W4", "Gemini 报告 + 评测", "OCR + Containment + 灰度",   GREEN),
    ]
    y0 = 340
    bw = 240
    gap = 8
    for i, (w, title, desc, c) in enumerate(weeks):
        x = 60 + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 138], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x + 12, y0 + 12, x + 64, y0 + 46], 16, fill=c)
        d.text((x + 24, y0 + 18), w, font=font(20, bold=True), fill=BG)
        d.text((x + 76, y0 + 18), title[:10], font=font(13, bold=True), fill=WHITE)
        words = desc.split(" · ")
        for j, ww in enumerate(words):
            d.text((x + 12, y0 + 60 + j * 22), "· " + ww, font=font(12), fill=SUB)
        if i < 3:
            ax = x + bw + 1
            d.line([(ax, y0 + 70), (ax + 5, y0 + 70)], fill=LINE, width=2)
            d.polygon([(ax + 7, y0 + 70), (ax + 2, y0 + 66), (ax + 2, y0 + 74)], fill=LINE)

    watermark(d)
    img.save(os.path.join(OUT, "05_engines.png"))
    print("[OK] 05_engines")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
