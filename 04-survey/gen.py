# -*- coding: utf-8 -*-
"""5 images for AI Agent 全行业落地综述 · 阶段性综述"""

from PIL import Image, ImageDraw, ImageFont
import os

OUT = r"E:\自媒体\Agent行业综述"
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
AMBER_LIGHT = "#fcd34d"
GOLD = "#eab308"
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
ORANGE_LIGHT = "#fdba74"
PINK = "#ec4899"
ROSE = "#f43f5e"
INDIGO = "#6366f1"
VIOLET = "#8b5cf6"
LIME = "#84cc16"
EMERALD = "#10b981"

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

    rrect(d, [60, 50, 240, 88], 19, fill=AMBER)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 500, 88], 19, fill=BOX)
    d.text((274, 56), "13 篇阶段性综述", font=font(17, bold=True), fill=AMBER_LIGHT)

    d.text((60, 124), "AI Agent 全行业", font=font(40, bold=True), fill=AMBER)
    d.text((60, 168), "落地综述", font=font(40, bold=True), fill=AMBER)

    chips = [
        ("找对模型",    GREEN_LIGHT,  "任务 × 模型矩阵"),
        ("打开思维",    PURPLE_LIGHT, "Excel → 工具栈"),
        ("门槛不高",    CYAN_LIGHT,   "3 周 MVP"),
    ]
    y = 250
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(15), fill=SUB)

    # bottom — core thesis
    rrect(d, [60, 374, 1020, 510], 14, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 390), "真正的门槛 · 不在技术 · 在认知", font=font(22, bold=True), fill=AMBER_LIGHT)
    d.text((80, 426), "看见自己行业 20 年的 Excel", font=font(15), fill=SUB)
    d.text((80, 450), "是 6 个工具 / 4 个 Subagent / 5 个 Hooks", font=font(15), fill=SUB)
    d.text((80, 478), "这是 Agent 时代真正稀缺的能力", font=font(15, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02: 行业全景图 ============
def img_02():
    img, d = base()
    d.text((60, 40), "15+ 行业 · Agent 落地全景", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "1 套骨架 · 15 种装填 · 模式行业无关", font=font(15), fill=LIGHT)

    industries = [
        ("法律",       PURPLE,    "合同 / 案例 / 文书"),
        ("医疗",       PINK,      "影像 / 分诊 / 用药"),
        ("金融",       GOLD,      "KYC / 风控 / 投顾"),
        ("教育",       BLUE,      "学情 / 批改 / 家校"),
        ("电商",       ROSE,      "推荐 / 客服 / 下单"),
        ("二手 3C",    TEAL,      "IMEI / 检测 / 微信"),
        ("制造",       CYAN,      "MES / 工艺 / 质检"),
        ("物流",       ORANGE,    "调度 / 异常 / 客服"),
        ("农业",       LIME,      "病虫害 / 施肥 / 预测"),
        ("房地产",     EMERALD,   "看房 / 装修 / 房贷"),
        ("政务",       INDIGO,    "12345 / 办事 / 表格"),
        ("HR",         VIOLET,    "简历 / 面试 / 入职"),
        ("营销",       AMBER_DEEP,"投放 / 文案 / 分群"),
        ("能源",       GREEN,     "光伏 / 调度 / 诊断"),
        ("内容创作",   PURPLE_LIGHT,"写作 / 脚本 / 多平台"),
    ]
    # 5x3 grid
    cols = 5
    bw = 192
    bh = 84
    gx, gy = 12, 12
    start_x = 60
    start_y = 116
    for i, (name, c, desc) in enumerate(industries):
        col = i % cols
        row = i // cols
        x = start_x + col * (bw + gx)
        y = start_y + row * (bh + gy)
        rrect(d, [x, y, x + bw, y + bh], 10, fill=BOX, outline=c, width=2)
        # tag
        rrect(d, [x + 8, y + 8, x + 60, y + 30], 8, fill=c)
        d.text((x + 16, y + 10), name[:4], font=font(13, bold=True), fill=BG)
        d.text((x + 70, y + 10), name, font=font(15, bold=True), fill=c)
        d.text((x + 10, y + 38), desc, font=font(11), fill=SUB)
        # 已写标识
        done_industries = ["能源", "电商", "二手 3C", "内容创作"]
        if name in done_industries:
            d.text((x + bw - 50, y + bh - 22), "已写 ✓", font=font(10, bold=True), fill=GREEN_LIGHT)

    # bottom callout
    rrect(d, [60, 462, 1020, 510], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 478), "每一行 = 1 个工程模板 · 同一套架构 · 不同装填", font=font(17, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "02_landscape.png"))
    print("[OK] 02_landscape")


# ============ 03: 任务×模型矩阵 ============
def img_03():
    img, d = base()
    d.text((60, 40), "任务 × 模型选型矩阵", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "锁单一供应商 = 锁短板 · 按任务分", font=font(15), fill=LIGHT)

    rows = [
        ("长链推理 / 共情 / 合规",  "Claude Sonnet 4.5",     ORANGE),
        ("结构化提取 / 严格 JSON",  "GPT-5",                  GREEN),
        ("多模态 / 图像 / PDF",     "Gemini 2.5 Pro",         BLUE),
        ("长上下文 (2M token)",     "Gemini 2.5 Pro",         BLUE),
        ("意图分类 / 路由",         "Claude Haiku",           ORANGE_LIGHT),
        ("风控 / 多变量评分",       "GPT-5",                  GREEN),
        ("价格 / 数字密集",         "GPT-5",                  GREEN),
        ("召回 / 向量检索",         "Qdrant + BGE-M3",        TEAL),
        ("重排",                    "Cohere rerank-3.5",      CYAN),
        ("规则匹配",                "正则 + 规则引擎",        LIGHT),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80, y0 + 8), "任务", font=font(14, bold=True), fill=AMBER)
    d.text((550, y0 + 8), "首选", font=font(14, bold=True), fill=AMBER)

    for i, (task, model, c) in enumerate(rows):
        y = y0 + 42 + i * 32
        rrect(d, [60, y, 1020, y + 26], 6, fill=DEEP)
        d.rectangle([60, y, 64, y + 26], fill=c)
        d.text((80, y + 5), task, font=font(14, bold=True), fill=WHITE)
        d.text((550, y + 5), model, font=mono(14), fill=c)

    # bottom callout
    rrect(d, [60, 478, 1020, 514], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 488), "一个项目混搭 3-4 个模型是常态 · LiteLLM 一层包就行", font=font(13, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_matrix.png"))
    print("[OK] 03_matrix")


# ============ 04: 5 个工程定律 ============
def img_04():
    img, d = base()
    d.text((60, 40), "5 个行业无关的工程定律", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "13 篇沉淀的规律 · 任何行业都成立", font=font(15), fill=LIGHT)

    laws = [
        ("1", "工具优先",      "LLM 不计算 · 数字/价格/状态全走工具",       ORANGE),
        ("2", "权限在数据层",  "ACL 在向量层 filter · 不在 prompt 限制",     PURPLE),
        ("3", "Subagent 分工", "Haiku 分流 · Sonnet 推理 · 成本压 1/5",      GREEN),
        ("4", "Hooks 守红线",  "价格 / 承诺 / 状态机 · 不让 LLM 决定",       PINK),
        ("5", "评测驱动",      "RAGAS / CSAT / DSAT · 跌 5% block 上线",    CYAN),
    ]
    y0 = 124
    for i, (n, name, desc, c) in enumerate(laws):
        y = y0 + i * 72
        rrect(d, [60, y, 1020, y + 60], 12, fill=BOX, outline=c, width=2)
        # number circle
        d.ellipse([76, y + 14, 124, y + 62], fill=c)
        d.text((90, y + 22), n, font=font(22, bold=True), fill=BG)
        # name
        d.text((148, y + 12), name, font=font(20, bold=True), fill=c)
        # desc
        d.text((148, y + 38), desc, font=font(14), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_laws.png"))
    print("[OK] 04_laws")


# ============ 05: 起步路径 + 5 误区 ============
def img_05():
    img, d = base()
    d.text((60, 40), "起步路径 · 5 个常见误区", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "技术门槛不高 · 唯一稀缺的是产品理解", font=font(15), fill=LIGHT)

    # 起步路径 table (left)
    d.text((60, 110), "从零到 MVP", font=font(17, bold=True), fill=GREEN_LIGHT)
    steps = [
        ("30 min", "装环境"),
        ("10 min", "拿 API key"),
        ("30 min", "Hello World"),
        ("1 h",    "加自定义工具"),
        ("0.5 day","加 Subagent + Hook"),
        ("1-2 day","接数据库"),
        ("2-3 day","接微信/飞书"),
        ("3 周",   "完整 MVP 上线"),
    ]
    y0 = 142
    for i, (t, s) in enumerate(steps):
        y = y0 + i * 34
        rrect(d, [60, y, 510, y + 28], 6, fill=BOX)
        bw = 78
        rrect(d, [68, y + 4, 68 + bw, y + 24], 6, fill=GREEN)
        d.text((76, y + 6), t, font=font(11, bold=True), fill=BG)
        d.text((160, y + 6), s, font=font(14, bold=True), fill=WHITE)

    # 5 误区 (right)
    d.text((550, 110), "5 个常见误区", font=font(17, bold=True), fill=ROSE)
    pitfalls = [
        ("误区 1", "Agent = 一个超大 Prompt"),
        ("误区 2", "模型越大越好"),
        ("误区 3", "评测可以后补"),
        ("误区 4", "越自动越好(其实 60-80% 最优)"),
        ("误区 5", "风格 / 调性调不准"),
    ]
    y0 = 142
    for i, (n, t) in enumerate(pitfalls):
        y = y0 + i * 54
        rrect(d, [550, y, 1020, y + 46], 8, fill=BOX, outline=ROSE, width=1)
        d.text((566, y + 6), n, font=font(12, bold=True), fill=ROSE)
        d.text((566, y + 24), t, font=font(13), fill=SUB)

    # bottom
    rrect(d, [60, 462, 1020, 510], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 478), "唯一稀缺的是产品理解 · 不是算法 · 不是工程", font=font(15, bold=True), fill=AMBER_LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_path.png"))
    print("[OK] 05_path")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
