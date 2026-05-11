# -*- coding: utf-8 -*-
"""5 images for 企业级客服系统 - Claude Agent SDK 边界实战"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\企业客服系统"
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
AMBER_DEEP = "#f59e0b"
RED = "#ef4444"
GREEN = "#22c55e"
GREEN_LIGHT = "#4ade80"
PURPLE = "#a855f7"
PURPLE_LIGHT = "#c084fc"
BLUE = "#3b82f6"
BLUE_LIGHT = "#60a5fa"
CYAN = "#06b6d4"
CYAN_LIGHT = "#22d3ee"
TEAL = "#14b8a6"
ORANGE = "#fb923c"
ORANGE_DEEP = "#f97316"
ORANGE_LIGHT = "#fdba74"
PINK = "#ec4899"
LIME = "#84cc16"

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

    rrect(d, [60, 50, 240, 88], 19, fill=ORANGE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 506, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 · 行业落地", font=font(17, bold=True), fill=AMBER)

    d.text((60, 130), "企业级客服系统", font=font(40, bold=True), fill=AMBER)
    d.text((60, 186), "Claude Agent SDK", font=font(26, bold=True), fill=WHITE)
    d.text((60, 222), "边界实战", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("不许承诺",    ORANGE,  "措辞监控"),
        ("不许越权",    PINK,    "二次确认"),
        ("不许自由发挥", AMBER,   "固定话术"),
    ]
    y = 296
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 510], 14, fill=DEEP, outline=ORANGE, width=2)
    d.text((80, 448), "客服系统的关键词不是聪明 · 是克制", font=font(20, bold=True), fill=ORANGE_LIGHT)
    d.text((80, 478), "LLM 越自由 · 商业风险越大", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: KB vs 客服 ============
def img_02():
    img, d = base()
    d.text((60, 40), "知识库 Q&A vs 客服系统", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "看着像 · 工程上是两套系统", font=font(15), fill=LIGHT)

    rows = [
        ("用户",     "内部员工(可信)",     "外部客户(不可信)",        BLUE),
        ("任务",     "只答疑",               "答疑 + 动作执行",          ORANGE),
        ("渠道",     "单一(内网)",         "多渠道(微信/小程序/邮件)", PURPLE),
        ("失败兜底", "我不知道",             "必须转人工",               PINK),
        ("评测",     "RAGAS",                "CSAT + Containment + AHT", GREEN),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 38], 8, fill=BOX)
    d.text((80, y0 + 10), "维度", font=font(15, bold=True), fill=AMBER)
    d.text((250, y0 + 10), "知识库 Q&A", font=font(15, bold=True), fill=CYAN_LIGHT)
    d.text((620, y0 + 10), "客服系统", font=font(15, bold=True), fill=ORANGE_LIGHT)

    for i, (dim, kb, cs, c) in enumerate(rows):
        y = y0 + 52 + i * 74
        rrect(d, [60, y, 1020, y + 60], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 60], fill=c)
        d.text((80, y + 20), dim, font=font(17, bold=True), fill=WHITE)
        d.text((250, y + 20), kb, font=font(14), fill=LIGHT)
        d.text((620, y + 20), cs, font=font(15, bold=True), fill=ORANGE_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "02_diff.png"))
    print("[OK] 02_diff")


# ============ 03: 四层架构 ============
def img_03():
    img, d = base()
    d.text((60, 40), "四层架构", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "渠道 → 状态 → Agent → 工具", font=font(15), fill=LIGHT)

    layers = [
        ("渠道层", BLUE,    "Web / 小程序 / 微信 / 邮件 / 飞书 → unified format"),
        ("状态层", PURPLE,  "Redis (session) · Postgres (历史 + 用户档案)"),
        ("Agent",  ORANGE,  "triager / info / action / escalator · 4 个 Subagent"),
        ("工具层", GREEN,   "KB / CRM / OMS / 工单 / Slack / 财务"),
    ]
    y0 = 116
    h = 84
    for i, (name, c, desc) in enumerate(layers):
        y = y0 + i * (h + 16)
        rrect(d, [60, y, 1020, y + h], 14, fill=BOX, outline=c, width=2)
        rrect(d, [60, y, 200, y + h], 14, fill=c)
        d.text((78, y + 22), name, font=font(22, bold=True), fill=BG)
        d.text((78, y + 52), f"Layer {i+1}", font=font(13, bold=True), fill=BG)
        d.text((228, y + 28), desc, font=font(15), fill=SUB)
        if i < 3:
            ay = y + h
            d.line([(540, ay), (540, ay + 8)], fill=LINE, width=2)
            d.polygon([(540, ay + 14), (534, ay + 6), (546, ay + 6)], fill=LINE)

    watermark(d)
    img.save(os.path.join(OUT, "03_architecture.png"))
    print("[OK] 03_architecture")


# ============ 04: 12 工具(信息 vs 动作) ============
def img_04():
    img, d = base()
    d.text((60, 40), "12 个工具 · 信息 vs 动作", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "一半工具是动作 · 客服 ≠ 纯 RAG", font=font(15), fill=LIGHT)

    # left col — 信息工具
    rrect(d, [60, 116, 100, 156], 8, fill=BLUE)
    d.text((76, 124), "A", font=font(20, bold=True), fill=BG)
    d.text((116, 124), "信息工具 · 读取 · 无副作用", font=font(17, bold=True), fill=BLUE_LIGHT)

    info_tools = [
        ("kb_search",       "知识库检索"),
        ("get_order",       "订单查询(ACL!)"),
        ("track_shipping",  "物流"),
        ("get_profile",     "用户档案"),
        ("analyze_intent",  "意图 + 情绪"),
    ]
    for i, (name, desc) in enumerate(info_tools):
        y = 170 + i * 50
        rrect(d, [60, y, 520, y + 42], 8, fill=BOX)
        d.text((76, y + 12), name, font=mono(14), fill=BLUE_LIGHT)
        d.text((280, y + 12), desc, font=font(13), fill=SUB)

    # right col — 动作工具
    rrect(d, [560, 116, 600, 156], 8, fill=ORANGE)
    d.text((576, 124), "B", font=font(20, bold=True), fill=BG)
    d.text((616, 124), "动作工具 · 写入 · 必须 guard", font=font(17, bold=True), fill=ORANGE_LIGHT)

    action_tools = [
        ("issue_refund",       "退款(金额 hook!)"),
        ("update_address",     "改地址"),
        ("send_coupon",        "发券(配额!)"),
        ("issue_invoice",      "开发票"),
        ("create_ticket",      "建工单"),
        ("escalate_to_human",  "转人工(带摘要)"),
        ("record_csat",        "记 CSAT"),
    ]
    for i, (name, desc) in enumerate(action_tools):
        y = 170 + i * 40
        rrect(d, [560, y, 1020, y + 32], 8, fill=BOX)
        d.text((576, y + 8), name, font=mono(13), fill=ORANGE_LIGHT)
        d.text((780, y + 8), desc, font=font(12), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_tools.png"))
    print("[OK] 04_tools")


# ============ 05: 评测 + 3 周路线 ============
def img_05():
    img, d = base()
    d.text((60, 40), "评测 + 3 周落地", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "CSAT / Containment / AHT / FCR · MVP → 灰度", font=font(15), fill=LIGHT)

    # 4 metrics
    metrics = [
        ("CSAT",        "> 4.2",     "Customer Satisfaction",  GREEN),
        ("Containment", "> 60%",     "AI 独立解决率",         CYAN),
        ("AHT",         "< 180s",    "Average Handle Time",   ORANGE),
        ("FCR",         "> 75%",     "First Contact Res.",    PURPLE),
    ]
    for i, (k, v, desc, c) in enumerate(metrics):
        x = 60 + i * 240
        rrect(d, [x, 116, x + 220, 220], 12, fill=BOX, outline=c, width=2)
        d.text((x + 16, 128), k, font=mono(15), fill=c)
        d.text((x + 16, 152), v, font=font(24, bold=True), fill=c)
        d.text((x + 16, 192), desc, font=font(11), fill=DIM)

    # 3 weeks
    d.text((60, 250), "3 周落地路线", font=font(17, bold=True), fill=AMBER)
    weeks = [
        ("W1", "单渠道 + 答疑",    "网页 + KB + 转人工兜底",          CYAN),
        ("W2", "动作 + 多渠道",    "订单/物流 + 微信/小程序",         ORANGE),
        ("W3", "退款审批 + 灰度",  "退款 hook + CSAT + 5% 流量",      GREEN),
    ]
    y0 = 288
    bw = 320
    for i, (w, title, desc, c) in enumerate(weeks):
        x = 60 + i * (bw + 20)
        rrect(d, [x, y0, x + bw, y0 + 130], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x + 16, y0 + 16, x + 76, y0 + 50], 16, fill=c)
        d.text((x + 30, y0 + 22), w, font=font(20, bold=True), fill=BG)
        d.text((x + 92, y0 + 22), title, font=font(17, bold=True), fill=WHITE)
        d.text((x + 16, y0 + 70), desc, font=font(13), fill=SUB)
        if i < 2:
            ax = x + bw + 2
            d.line([(ax, y0 + 65), (ax + 14, y0 + 65)], fill=LINE, width=2)
            d.polygon([(ax + 18, y0 + 65), (ax + 10, y0 + 59), (ax + 10, y0 + 71)], fill=LINE)

    # bottom — key principle
    rrect(d, [60, 438, 1020, 510], 12, fill=DEEP, outline=ORANGE, width=2)
    d.text((80, 452), "W1 别上动作工具", font=font(17, bold=True), fill=ORANGE_LIGHT)
    d.text((80, 482), "先把答疑 + 转人工跑稳 · 再加动作 · 工程纪律翻倍", font=font(14), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "05_metrics.png"))
    print("[OK] 05_metrics")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
