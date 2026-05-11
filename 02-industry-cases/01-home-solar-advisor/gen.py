# -*- coding: utf-8 -*-
"""5 images for 家庭绿电方案助手 - Claude Agent SDK"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\家庭绿电助手"
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
GREEN = "#22c55e"
GREEN_LIGHT = "#4ade80"
AMBER = "#fbbf24"
RED = "#ef4444"
PURPLE = "#a855f7"
BLUE = "#3b82f6"
CYAN = "#06b6d4"
ORANGE = "#fb923c"
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

    rrect(d, [60, 50, 240, 88], 19, fill=GREEN)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 506, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 · 行业落地", font=font(17, bold=True), fill=AMBER)

    d.text((60, 132), "家庭绿电方案助手", font=font(40, bold=True), fill=AMBER)
    d.text((60, 188), "用 Claude Agent SDK 替代", font=font(26, bold=True), fill=WHITE)
    d.text((60, 224), "光伏设计院的 Excel", font=font(26, bold=True), fill=WHITE)

    # 3 selling points
    chips = [
        ("6 工具", GREEN, "确定性计算"),
        ("4 Subagent", BLUE, "流程分工"),
        ("3 Hooks", AMBER, "工程红线"),
    ]
    y = 300
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(16), fill=SUB)

    # bottom callout
    rrect(d, [60, 432, 1020, 510], 14, fill=DEEP, outline=GREEN, width=2)
    d.text((80, 448), "用户一句话 → 7 次工具调用 → 一份方案 PDF", font=font(20, bold=True), fill=GREEN_LIGHT)
    d.text((80, 478), "设计院 3 万的方案书,Agent 5 分钟出", font=font(15), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: ARCHITECTURE ============
def img_02():
    img, d = base()
    d.text((60, 40), "整体架构", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "主 Agent 调度 · Subagent 分工 · 工具硬算", font=font(15), fill=LIGHT)

    # user
    rrect(d, [440, 110, 640, 154], 12, fill=BLUE)
    d.text((478, 120), "用户对话", font=font(20, bold=True), fill=WHITE)

    # arrow
    d.line([(540, 156), (540, 184)], fill=LINE, width=2)
    d.polygon([(540, 192), (534, 184), (546, 184)], fill=LINE)

    # main agent
    rrect(d, [400, 196, 680, 258], 12, fill=BOX, outline=AMBER, width=2)
    d.text((430, 208), "主 Agent (Claude)", font=font(20, bold=True), fill=AMBER)
    d.text((430, 234), "调度员 · 不直接算", font=font(13), fill=SUB)

    # 4 subagents row
    sub_y = 304
    subs = [
        ("site-survey", "采数据", CYAN),
        ("energy-model", "跑发电", GREEN),
        ("econ-analyst", "算回收", AMBER),
        ("report-writer", "出方案", PURPLE),
    ]
    for i, (name, role, c) in enumerate(subs):
        x = 60 + i * 250
        # connector
        d.line([(540, 260), (x + 110, 296)], fill=LINE, width=1)
        rrect(d, [x, sub_y, x + 220, sub_y + 78], 10, fill=BOX, outline=c, width=2)
        d.text((x + 14, sub_y + 12), name, font=mono(15), fill=c)
        d.text((x + 14, sub_y + 38), role, font=font(15, bold=True), fill=WHITE)
        # down arrow
        d.line([(x + 110, sub_y + 80), (x + 110, sub_y + 108)], fill=LINE, width=2)

    # 6 tools row
    tool_y = 420
    rrect(d, [60, tool_y, 1020, tool_y + 100], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((76, tool_y + 12), "6 个确定性工具 (MCP)", font=font(15, bold=True), fill=GREEN)
    tools = [
        "get_irradiance", "estimate_yield", "match_load",
        "size_battery", "payback", "select_panels"
    ]
    for i, t in enumerate(tools):
        col = i % 3
        row = i // 3
        x = 80 + col * 320
        y = tool_y + 44 + row * 26
        d.text((x, y), "· " + t, font=mono(14), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "02_architecture.png"))
    print("[OK] 02_architecture")


# ============ 03: SIX TOOLS ============
def img_03():
    img, d = base()
    d.text((60, 40), "6 个核心工具", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "每个都是确定性函数 · Claude 当调度员", font=font(15), fill=LIGHT)

    rows = [
        ("get_irradiance",  "辐照数据",   "lat,lon,tilt,azi",          "POA kWh/m²/day",  CYAN),
        ("estimate_yield",  "发电量估算", "area,W/m²,POA,loss",        "annual_kwh",      GREEN),
        ("match_load",      "自发自用率", "gen_hourly,load,battery",   "self_use_ratio",  TEAL),
        ("size_battery",    "储能推荐",   "daily_kwh,autonomy,dod",    "battery_kwh",     LIME),
        ("payback",         "经济测算",   "capex,savings,elec_price",  "years,IRR,NPV",   AMBER),
        ("select_panels",   "组件选型",   "target_kw,roof,budget",     "top3 SKU",        ORANGE),
    ]
    y0 = 130
    # header
    rrect(d, [60, y0, 1020, y0 + 36], 8, fill=BOX)
    d.text((80, y0 + 9), "工具", font=font(15, bold=True), fill=AMBER)
    d.text((260, y0 + 9), "用途", font=font(15, bold=True), fill=AMBER)
    d.text((430, y0 + 9), "输入", font=font(15, bold=True), fill=AMBER)
    d.text((720, y0 + 9), "输出", font=font(15, bold=True), fill=AMBER)

    for i, (name, use, args, out, c) in enumerate(rows):
        y = y0 + 50 + i * 60
        rrect(d, [60, y, 1020, y + 50], 8, fill=DEEP)
        d.rectangle([60, y, 64, y + 50], fill=c)
        d.text((80, y + 16), name, font=mono(15), fill=c)
        d.text((260, y + 16), use, font=font(16, bold=True), fill=WHITE)
        d.text((430, y + 16), args, font=mono(13), fill=SUB)
        d.text((720, y + 16), out, font=mono(13), fill=GREEN_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_six_tools.png"))
    print("[OK] 03_six_tools")


# ============ 04: SUBAGENTS ============
def img_04():
    img, d = base()
    d.text((60, 40), "4 个 Subagent 串行", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "主 Agent 委派 · 各管一段 · 不跳步不并行", font=font(15), fill=LIGHT)

    stages = [
        ("1", "site-survey",   "采集屋顶 + 负荷数据",        "无工具,纯对话",                CYAN),
        ("2", "energy-model",  "跑辐照 + 发电 + 自发自用",   "get_irradiance / estimate_yield / match_load", GREEN),
        ("3", "econ-analyst",  "储能容量 + 回收期",          "size_battery / payback",         AMBER),
        ("4", "report-writer", "出 Markdown 方案书",         "Write",                          PURPLE),
    ]
    y = 130
    for i, (num, name, role, tools, c) in enumerate(stages):
        ry = y + i * 100
        rrect(d, [60, ry, 1020, ry + 84], 12, fill=BOX, outline=c, width=2)
        # step circle
        d.ellipse([78, ry + 22, 122, ry + 66], fill=c)
        d.text((90 if num != "1" else 92, ry + 28), num, font=font(24, bold=True), fill=BG)
        # name + role
        d.text((146, ry + 14), name, font=mono(18), fill=c)
        d.text((146, ry + 44), role, font=font(17, bold=True), fill=WHITE)
        # tools
        d.text((620, ry + 14), "工具白名单", font=font(13), fill=DIM)
        d.text((620, ry + 38), tools, font=mono(12), fill=SUB)
        # arrow between
        if i < 3:
            d.line([(540, ry + 86), (540, ry + 98)], fill=LINE, width=2)
            d.polygon([(540, ry + 100), (534, ry + 92), (546, ry + 92)], fill=LINE)

    watermark(d)
    img.save(os.path.join(OUT, "04_subagents.png"))
    print("[OK] 04_subagents")


# ============ 05: WALKTHROUGH ============
def img_05():
    img, d = base()
    d.text((60, 40), "一次真实运行", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "杭州 · 90㎡ · 8000 kWh/年 · 预算 8 万", font=font(15), fill=LIGHT)

    # input box
    rrect(d, [60, 116, 520, 248], 12, fill=DEEP, outline=BLUE, width=2)
    d.text((80, 130), "输入", font=font(15, bold=True), fill=BLUE)
    inputs = [
        "地址:杭州",
        "屋顶:90㎡ / 朝南 / 15° 坡",
        "年用电:8000 kWh",
        "预算:8 万",
        "需求:并网 + 储能",
    ]
    for i, line in enumerate(inputs):
        d.text((80, 158 + i * 18), line, font=font(13), fill=SUB)

    # arrow
    d.line([(540, 182), (572, 182)], fill=AMBER, width=3)
    d.polygon([(580, 182), (570, 176), (570, 188)], fill=AMBER)

    # output box
    rrect(d, [600, 116, 1020, 248], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((620, 130), "Agent 输出方案", font=font(15, bold=True), fill=GREEN)
    outputs = [
        "组件:协鑫钙钛矿叠层 ×24 块",
        "系统容量:6.3 kWp",
        "储能:10 kWh 磷酸铁锂",
        "总投资:7.8 万",
    ]
    for i, line in enumerate(outputs):
        d.text((620, 158 + i * 20), line, font=font(13), fill=SUB)

    # key metrics
    d.text((60, 276), "关键指标", font=font(17, bold=True), fill=AMBER)
    metrics = [
        ("年发电", "7,420 kWh", GREEN),
        ("自发自用率", "58%", CYAN),
        ("回收期", "8.2 年", AMBER),
        ("25年 IRR", "9.4%", ORANGE),
        ("25年净收益", "14.2 万", LIME),
    ]
    for i, (k, v, c) in enumerate(metrics):
        x = 60 + i * 192
        rrect(d, [x, 308, x + 180, 388], 10, fill=BOX, outline=c, width=2)
        d.text((x + 14, 318), k, font=font(13), fill=DIM)
        d.text((x + 14, 344), v, font=font(20, bold=True), fill=c)

    # summary callout
    rrect(d, [60, 416, 1020, 510], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((80, 428), "整个过程用户只说一句话", font=font(17, bold=True), fill=GREEN_LIGHT)
    d.text((80, 458), "Agent 跑完 4 段 · 调用 7 次工具 · 5 分钟出方案", font=font(15), fill=SUB)
    d.text((80, 482), "传统设计院流程:报价 3 万,周期 2 周", font=font(13), fill=DIM)

    watermark(d)
    img.save(os.path.join(OUT, "05_walkthrough.png"))
    print("[OK] 05_walkthrough")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
