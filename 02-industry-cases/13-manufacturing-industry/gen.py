# -*- coding: utf-8 -*-
"""5 images for 制造行业 AI 落地 · 行业落地 #13"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# 制造主题 · 钢铁 + 工业橙
BG       = "#18181b"
BOX      = "#27272a"
DEEP     = "#0a0a0d"
LINE     = "#3f3f46"
WHITE    = "#ffffff"
SUB      = "#e4e4e7"
LIGHT    = "#a1a1aa"
DIM      = "#71717a"
ORANGE   = "#f97316"
ORANGE_L = "#fdba74"
STEEL    = "#94a3b8"
INFO     = "#38bdf8"
INFO_L   = "#7dd3fc"
SAFE     = "#10b981"
SAFE_L   = "#34d399"
WARN     = "#fbbf24"
WARN_L   = "#fde047"
DANGER   = "#ef4444"
DANGER_L = "#fca5a5"
PURPLE   = "#a855f7"

REG  = r"C:\Windows\Fonts\msyh.ttc"
BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


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
    rrect(d, [60, 50, 240, 88], 8, fill=ORANGE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 8, fill=BOX)
    d.text((274, 56), "行业落地 #13", font=font(17, bold=True), fill=ORANGE_L)

    d.text((60, 128), "制造行业 AI 落地", font=font(42, bold=True), fill=ORANGE_L)
    d.text((60, 188), "MES / 工艺 / 质检 ·", font=font(26, bold=True), fill=WHITE)
    d.text((60, 222), "6 大场景 + 物理边界", font=font(26, bold=True), fill=WHITE)

    chips = [
        ("MES 只读",        INFO_L,    "AI 查 · 不写"),
        ("物理边界",        WARN_L,    "推荐越界自动拦"),
        ("配方机密",        DANGER_L,  "脱敏后再进 LLM"),
    ]
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, 296, x + 310, 388], 6, fill=BOX, outline=c, width=2)
        d.text((x + 20, 310), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, 348), desc, font=font(15), fill=SUB)

    rrect(d, [60, 432, 1020, 514], 6, fill=DEEP, outline=ORANGE, width=2)
    d.text((80, 448), "制造行业 AI · 不是会建议 · 是懂得物理边界", font=font(20, bold=True), fill=ORANGE_L)
    d.text((80, 482), "签字权在工艺工程师 / QC / 维修组 · AI 消化重复性查询和初判", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 SCOPE ============
def img_02():
    img, d = base()
    d.text((60, 40), "6 大场景闭环", font=font(26, bold=True), fill=ORANGE_L)
    d.text((60, 78), "MES → 工艺 → 质检 → 设备 → 排程 → SOP · 数据 / 指令双向但严格分流", font=font(15), fill=LIGHT)

    scenarios = [
        ("📊", "MES 数据问答",     "自然语言 → MES 实数据",       "全员",       INFO),
        ("⚙️", "工艺参数推荐",    "历史最优 + 物理边界硬阻断",     "工艺工程师", ORANGE),
        ("🔍", "质检视觉",         "AI 初判 · QC 终判盖章",        "QC",         WARN),
        ("🛠️", "PdM 预测性维护",  "健康度评分 + 维护窗",          "维修组",     STEEL),
        ("📅", "排程辅助",         "订单 × 产线 × 截止日",         "计划员",     SAFE),
        ("📚", "SOP / ECN 知识",  "引用必须带版本 + 生效日",       "操作工",     PURPLE),
    ]
    y0 = 110
    for i, (icon, name, desc, target, c) in enumerate(scenarios):
        y = y0 + i * 72
        rrect(d, [60, y, 1020, y + 62], 6, fill=BOX, outline=c, width=2)
        d.text((78, y + 14), icon, font=font(28), fill=c)
        d.text((140, y + 10), name, font=font(20, bold=True), fill=c)
        d.text((140, y + 38), desc, font=font(13), fill=SUB)
        bw = tw(d, target, font(12, bold=True)) + 16
        rrect(d, [1020 - bw - 14, y + 20, 1020 - 14, y + 42], 4, fill=DEEP)
        d.text((1020 - bw - 8, y + 22), target, font=font(12, bold=True), fill=c)
    watermark(d)
    img.save(os.path.join(OUT, "02_scope.png"))
    print("[OK] 02_scope")


# ============ 03 CHALLENGES ============
def img_03():
    img, d = base()
    d.text((60, 40), "制造行业 AI · 8 个独特挑战", font=font(26, bold=True), fill=ORANGE_L)
    d.text((60, 78), "其他行业没有的硬约束 · 触红线 = 烧设备 / 安全事故 / 客户索赔", font=font(15), fill=LIGHT)

    challenges = [
        ("工艺机密保护",     "★★★★★", "配方 / BOM 不能进公有云 LLM 明文",         DANGER),
        ("物理边界硬约束",   "★★★★★", "温度/压力/时间越界 = 烧设备",              DANGER),
        ("质检不出结论",     "★★★★★", "AI 提示 + QC 工程师盖章",                   WARN),
        ("MES 写操作",       "★★★★★", "AI 默认只读 · 写必须人工授权",              WARN),
        ("SOP 版本一致",     "★★★★",  "引用必须带版本号 + 生效日期",                INFO),
        ("ECN 影响评估",     "★★★★",  "在制品 / 已交付 / BOM / QC 四个维度",        PURPLE),
        ("良率不能编",       "★★★★",  "必须接 MES · 不允许 LLM 自由发挥",           STEEL),
        ("多车间行级权限",   "★★★",   "WS-A 用户不能看 WS-B 数据",                  SAFE),
    ]
    y0 = 110
    for i, (name, stars, desc, c) in enumerate(challenges):
        y = y0 + i * 54
        rrect(d, [60, y, 1020, y + 46], 6, fill=BOX, outline=c, width=2)
        d.rectangle([60, y, 64, y + 46], fill=c)
        d.text((80, y + 6), name, font=font(15, bold=True), fill=WHITE)
        d.text((80, y + 26), desc, font=font(12), fill=SUB)
        d.text((1020 - 100, y + 14), stars, font=font(13, bold=True), fill=c)
    watermark(d)
    img.save(os.path.join(OUT, "03_challenges.png"))
    print("[OK] 03_challenges")


# ============ 04 RULES ============
def img_04():
    img, d = base()
    d.text((60, 40), "7 条制造工程纪律", font=font(26, bold=True), fill=ORANGE_L)
    d.text((60, 78), "全场景共通 · 跟 ISO 9001 / IATF 16949 / EHS 对齐", font=font(15), fill=LIGHT)

    rules = [
        ("1", "安全熔断",          "关键词 → 不进 LLM · 推 EHS / 119",        DANGER),
        ("2", "工艺签字栏",        "推荐 / 质检 / 排程 强制注入",             WARN),
        ("3", "物理边界 hard",     "PROCESS_BOUNDARIES 表 · 越界拦截",        ORANGE),
        ("4", "配方机密脱敏",      "RECIPE_SECRET 正则 + 商业秘密标记",       INFO),
        ("5", "MES 只读",          "AI 不直接修改 · 写必须人工",              STEEL),
        ("6", "SOP/ECN 引用",      "必带 doc_id + 版本号 + 生效日期",         PURPLE),
        ("7", "建议性软化",        "10 个绝对化禁词 · 强建议性降置信度",      SAFE),
    ]
    y0 = 110
    for i, (n, name, desc, c) in enumerate(rules):
        y = y0 + i * 64
        rrect(d, [60, y, 1020, y + 54], 6, fill=BOX, outline=c, width=2)
        d.rectangle([76, y + 10, 114, y + 46], fill=c)
        d.text((83, y + 14), n, font=font(17, bold=True), fill=BG)
        d.text((132, y + 8), name, font=font(17, bold=True), fill=c)
        d.text((132, y + 32), desc, font=font(13), fill=SUB)
    watermark(d)
    img.save(os.path.join(OUT, "04_rules.png"))
    print("[OK] 04_rules")


# ============ 05 DATA FLOW ============
def img_05():
    img, d = base()
    d.text((60, 40), "数据流:MES → AI → 签字 → 执行", font=font(24, bold=True), fill=ORANGE_L)
    d.text((60, 76), "全链 4 个签字栏 · AI 失效 · 工艺照样能跑(不依赖 AI)", font=font(14), fill=LIGHT)

    # 5 节点
    nodes = [
        ("📡\nMES/SCADA",     90,  170, INFO,    "实数据"),
        ("🔒\n脱敏 + 边界",   290, 170, WARN,    "机密保护"),
        ("🤖\nAI 辅助",       490, 170, ORANGE,  "提示 / 初判"),
        ("✍️\n工程师签字",    690, 170, SAFE,    "担责"),
        ("📋\n下发 MES",      890, 170, PURPLE,  "可追溯"),
    ]
    for icon_name, x, y, c, note in nodes:
        rrect(d, [x, y, x + 140, y + 130], 6, fill=BOX, outline=c, width=2)
        lines = icon_name.split("\n")
        d.text((x + 50, y + 14), lines[0], font=font(28), fill=c)
        d.text((x + 18, y + 60), lines[1], font=font(14, bold=True), fill=c)
        d.text((x + 18, y + 92), note, font=font(11), fill=SUB)

    # 箭头
    for i in range(4):
        x1 = 90 + i * 200 + 140
        x2 = 90 + (i + 1) * 200
        d.line([(x1, 235), (x2 - 4, 235)], fill=LINE, width=3)
        d.polygon([(x2, 235), (x2 - 10, 230), (x2 - 10, 240)], fill=LINE)

    # 安全熔断旁路
    rrect(d, [60, 380, 1020, 450], 6, fill=DEEP, outline=DANGER, width=2)
    d.text((80, 396), "🚨 安全旁路:任何节点检测到事故关键词 → 跳过 AI · 直接 EHS",
           font=font(15, bold=True), fill=DANGER_L)
    d.text((80, 422), "(明火 / 燃爆 / 化学品溅出 / 人员受伤 / 急停 / 全线停机)",
           font=font(13), fill=LIGHT)

    # 底部说明
    rrect(d, [60, 488, 1020, 540], 4, fill=DEEP, outline=ORANGE, width=1)
    d.text((80, 500), "核心:AI 是车间数字化的 1 个工位 · 不是大脑 · 不是替代",
           font=font(14, bold=True), fill=ORANGE_L)
    d.text((80, 520), "拔掉 AI · 工艺 / 质检 / 维修依然按 SOP 跑 · 这才是合规姿势",
           font=font(12), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_flow.png"))
    print("[OK] 05_flow")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
