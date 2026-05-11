# -*- coding: utf-8 -*-
"""5 images for 绿电电商客服系统 - 集大成篇"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\绿电电商客服"
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
CYAN_LIGHT = "#22d3ee"
ORANGE = "#fb923c"
ORANGE_LIGHT = "#fdba74"
PINK = "#ec4899"
PINK_LIGHT = "#f472b6"
ROSE = "#f43f5e"
ROSE_LIGHT = "#fb7185"
LIME = "#84cc16"
TEAL = "#14b8a6"

# Claude 橙 · GPT-5 绿
CLAUDE_C = "#fb923c"
GPT_C    = "#4ade80"

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

    rrect(d, [60, 50, 240, 88], 19, fill=PINK)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 560, 88], 19, fill=BOX)
    d.text((274, 56), "行业落地集大成 · 5/5 收官", font=font(15, bold=True), fill=AMBER)

    d.text((60, 128), "绿电电商客服系统", font=font(40, bold=True), fill=AMBER)
    d.text((60, 184), "Claude + GPT-5 双引擎", font=font(26, bold=True), fill=WHITE)
    d.text((60, 220), "下单闭环", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("方案 + 报价", CYAN,        "复用 #1"),
        ("下单 + 支付", PINK,        "OMS 集成"),
        ("售后 + 工单", PURPLE,      "全链路"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=PINK, width=2)
    d.text((80, 442), "前 4 篇的能力 · 在这里熔合", font=font(22, bold=True), fill=PINK_LIGHT)
    d.text((80, 478), "Agent 接 OMS · 工程纪律是 RAG 的 3 倍", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 业务全流程 ============
def img_02():
    img, d = base()
    d.text((60, 40), "业务全流程", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "从咨询到并网 · 一个 Agent 全跑完", font=font(15), fill=LIGHT)

    # 8 stages horizontal
    stages = [
        ("咨询",    CYAN),
        ("出方案",  CYAN_LIGHT),
        ("报价",    BLUE_LIGHT),
        ("下单",    PINK),
        ("支付",    ROSE),
        ("排施工",  ORANGE),
        ("发货安装", ORANGE_LIGHT),
        ("售后",    PURPLE),
    ]
    y0 = 150
    bw = 110
    gap = 12
    start_x = 60
    for i, (name, c) in enumerate(stages):
        x = start_x + i * (bw + gap)
        rrect(d, [x, y0, x + bw, y0 + 60], 10, fill=BOX, outline=c, width=2)
        d.text((x + 14, y0 + 18), name, font=font(15, bold=True), fill=c)
        # arrow between
        if i < len(stages) - 1:
            ax = x + bw + 2
            d.line([(ax, y0 + 30), (ax + 8, y0 + 30)], fill=LINE, width=2)
            d.polygon([(ax + 10, y0 + 30), (ax + 4, y0 + 26), (ax + 4, y0 + 34)], fill=LINE)

    # zones underneath
    d.text((60, 240), "三段工程纪律分区", font=font(17, bold=True), fill=AMBER)
    zones = [
        ("咨询 → 报价",      "复用 #1 方案助手 · 只读 · 无副作用",     CYAN,    60, 480),
        ("下单 → 支付",      "工程纪律重区 · 库存/价格/支付/审计",     PINK,    560, 1020),
    ]
    for label, desc, c, x1, x2 in zones:
        rrect(d, [x1, 282, x2, 360], 12, fill=DEEP, outline=c, width=2)
        d.text((x1 + 16, 294), label, font=font(15, bold=True), fill=c)
        d.text((x1 + 16, 320), desc, font=font(13), fill=SUB)

    # 售后 zone
    rrect(d, [60, 374, 1020, 444], 12, fill=DEEP, outline=PURPLE, width=2)
    d.text((76, 386), "售后:长尾客服 · 工单 · 转人工带摘要", font=font(15, bold=True), fill=PURPLE_LIGHT)
    d.text((76, 414), "复用 #4 通用客服骨架 + 边界 Hooks", font=font(13), fill=SUB)

    # bottom
    rrect(d, [60, 462, 1020, 510], 14, fill=DEEP, outline=PINK, width=2)
    d.text((80, 478), "一旦用户说我要买,钱就要动 —— 这是关键分界点", font=font(15, bold=True), fill=PINK_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "02_flow.png"))
    print("[OK] 02_flow")


# ============ 03: 7 个对接系统 ============
def img_03():
    img, d = base()
    d.text((60, 40), "7 个对接系统", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "API + DB 两条线 · 写操作只走 API", font=font(15), fill=LIGHT)

    systems = [
        ("OMS",   "订单中心",  "API 写 + DB 读",     PINK),
        ("WMS",   "库存",       "API only · 实时",    ROSE),
        ("PMS",   "商品 · 价格", "DB + Redis 缓存",   BLUE),
        ("CRM",   "用户档案",   "DB + API 混合",      PURPLE),
        ("支付网关","起单 · 退款","API only",          ORANGE),
        ("物流",   "档期 · 追踪", "API · 5min 缓存",  CYAN),
        ("KB",    "政策 · FAQ", "Qdrant(复用 #3)",   GREEN),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 36], 8, fill=BOX)
    d.text((80, y0 + 9), "系统", font=font(15, bold=True), fill=AMBER)
    d.text((230, y0 + 9), "用途", font=font(15, bold=True), fill=AMBER)
    d.text((480, y0 + 9), "接法", font=font(15, bold=True), fill=AMBER)
    d.text((780, y0 + 9), "纪律", font=font(15, bold=True), fill=AMBER)

    notes = [
        "事务 · 联动 · 风控",
        "毫秒级变化 · 不缓存",
        "缓存命中率 > 90%",
        "PII 脱敏 · ACL",
        "Agent 不付款",
        "档期 5min 内可信",
        "向量召回",
    ]

    for i, ((name, use, how, c), note) in enumerate(zip(systems, notes)):
        y = y0 + 50 + i * 48
        rrect(d, [60, y, 1020, y + 40], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 40], fill=c)
        d.text((80, y + 12), name, font=mono(15), fill=c)
        d.text((230, y + 12), use, font=font(14, bold=True), fill=WHITE)
        d.text((480, y + 12), how, font=mono(12), fill=SUB)
        d.text((780, y + 12), note, font=font(13), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_systems.png"))
    print("[OK] 03_systems")


# ============ 04: 18 工具 4 类 ============
def img_04():
    img, d = base()
    d.text((60, 40), "18 工具 · 4 类", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "信息 / 动作 / 分析 / 复用 #1", font=font(15), fill=LIGHT)

    # 4 categories
    cats = [
        ("A 信息", BLUE,    [
            "get_pricing", "check_inventory", "get_subsidy",
            "get_installer_capacity", "get_user_profile", "get_user_orders",
        ]),
        ("B 动作", PINK,    [
            "create_order", "request_payment", "apply_coupon",
            "schedule_installation", "cancel_order", "update_address",
            "create_aftersale_ticket", "escalate_to_human",
        ]),
        ("C 分析", PURPLE,  [
            "analyze_intent", "check_risk",
        ]),
        ("D 复用 #1", CYAN, [
            "generate_plan (内含方案助手 4 Subagent + 6 工具)",
            "· get_irradiance / estimate_yield / match_load",
            "· size_battery / payback / select_panels",
        ]),
    ]
    # 2x2 layout
    layout = [
        (60, 114, 510, 268),     # A
        (530, 114, 1020, 320),   # B
        (60, 290, 510, 380),     # C
        (530, 344, 1020, 510),   # D
    ]
    for (name, c, items), (x1, y1, x2, y2) in zip(cats, layout):
        rrect(d, [x1, y1, x2, y2], 12, fill=BOX, outline=c, width=2)
        # header
        rrect(d, [x1, y1, x1 + 110, y1 + 32], 8, fill=c)
        d.text((x1 + 12, y1 + 6), name, font=font(16, bold=True), fill=BG)
        # items
        for j, item in enumerate(items):
            d.text((x1 + 16, y1 + 44 + j * 22), "· " + item, font=mono(12), fill=SUB)

    # bottom callout
    rrect(d, [60, 400, 510, 510], 12, fill=DEEP, outline=PINK, width=2)
    d.text((76, 416), "核心差异", font=font(15, bold=True), fill=PINK_LIGHT)
    d.text((76, 444), "8 个动作工具", font=font(14, bold=True), fill=WHITE)
    d.text((76, 470), "Agent 不只是找信息", font=font(13), fill=SUB)
    d.text((76, 490), "还在执行真实业务", font=font(13), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_tools.png"))
    print("[OK] 04_tools")


# ============ 05: 双引擎 + 3 周 ============
def img_05():
    img, d = base()
    d.text((60, 40), "Claude + GPT-5 双引擎", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "按任务分 · 不要二选一", font=font(15), fill=LIGHT)

    # 任务分配表
    tasks = [
        ("主对话 / 推理",      "Claude Sonnet 4.5",   CLAUDE_C),
        ("方案生成 / 售后情绪", "Claude Sonnet 4.5",   CLAUDE_C),
        ("下单参数提取",       "GPT-5",                GPT_C),
        ("价格 / 数字密集",    "GPT-5",                GPT_C),
        ("风控判断",           "GPT-5",                GPT_C),
        ("意图分类",           "Haiku / GPT-5 mini",   LIGHT),
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

    # 3 weeks
    d.text((60, 304), "3 周落地路线", font=font(17, bold=True), fill=AMBER)
    weeks = [
        ("W1", "咨询 + 出方案 + 报价(只读)", "复用 #1 + PMS / KB",          CYAN),
        ("W2", "下单 + 支付链接 + 查单",       "OMS + 风控 + 二次确认 · 灰度 ¥1000", PINK),
        ("W3", "售后 + 改单 + 评测 + 灰度",    "工单 + Containment · 灰度 5% · 放开 ¥5万", GREEN),
    ]
    y0 = 340
    bw = 320
    for i, (w, title, desc, c) in enumerate(weeks):
        x = 60 + i * (bw + 20)
        rrect(d, [x, y0, x + bw, y0 + 138], 12, fill=BOX, outline=c, width=2)
        rrect(d, [x + 16, y0 + 16, x + 76, y0 + 50], 16, fill=c)
        d.text((x + 30, y0 + 22), w, font=font(20, bold=True), fill=BG)
        d.text((x + 92, y0 + 22), title[:11], font=font(15, bold=True), fill=WHITE)
        # multi line desc
        words = desc.split(" · ")
        for j, w in enumerate(words):
            d.text((x + 16, y0 + 64 + j * 22), "· " + w, font=font(12), fill=SUB)
        if i < 2:
            ax = x + bw + 2
            d.line([(ax, y0 + 70), (ax + 14, y0 + 70)], fill=LINE, width=2)
            d.polygon([(ax + 18, y0 + 70), (ax + 10, y0 + 64), (ax + 10, y0 + 76)], fill=LINE)

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
