# -*- coding: utf-8 -*-
"""6 images for 13 篇行业落地综述 · 阶段性综述(收官)"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

BG     = "#0f172a"
BOX    = "#1e293b"
DEEP   = "#0b1220"
LINE   = "#334155"
WHITE  = "#ffffff"
SUB    = "#cbd5e1"
LIGHT  = "#94a3b8"
DIM    = "#64748b"
AMBER  = "#fbbf24"
AMBER_D = "#f59e0b"
AMBER_L = "#fcd34d"
GOLD   = "#eab308"
RED    = "#ef4444"
RED_L  = "#fca5a5"
GREEN  = "#22c55e"
GREEN_L = "#4ade80"
PURPLE = "#a855f7"
PURPLE_L = "#c084fc"
BLUE   = "#3b82f6"
BLUE_L = "#60a5fa"
CYAN   = "#06b6d4"
CYAN_L = "#22d3ee"
TEAL   = "#14b8a6"
ORANGE = "#fb923c"
ORANGE_L = "#fdba74"
PINK   = "#ec4899"
ROSE   = "#f43f5e"
INDIGO = "#6366f1"
VIOLET = "#8b5cf6"
LIME   = "#84cc16"
EMERALD = "#10b981"
STEEL  = "#94a3b8"

REG  = r"C:\Windows\Fonts\msyh.ttc"
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
    return img, ImageDraw.Draw(img)


def watermark(d):
    d.text((W - 180, H - 32), "实战复盘", font=font(14), fill=DIM)


# ============ 01 HERO ============
def img_01():
    img, d = base()
    rrect(d, [60, 50, 240, 88], 19, fill=AMBER)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 500, 88], 19, fill=BOX)
    d.text((274, 56), "13 篇收官 · 综述", font=font(17, bold=True), fill=AMBER_L)

    d.text((60, 124), "13 篇行业落地综述", font=font(40, bold=True), fill=AMBER)
    d.text((60, 174), "工程模式行业无关 · 红线决定形态", font=font(22, bold=True), fill=WHITE)

    chips = [
        ("骨架不变",     GREEN_L,   "1 套 FastAPI + 7 router"),
        ("数据红线变",   ORANGE_L,  "13 个领域 13 套红线"),
        ("熔断先行",     RED_L,     "应急 / 反诈 / 安全不进 LLM"),
    ]
    y = 250
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(14), fill=SUB)

    # bottom thesis
    rrect(d, [60, 374, 1020, 510], 14, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 390), "13 篇验证的核心结论", font=font(22, bold=True), fill=AMBER_L)
    d.text((80, 426), "同一套骨架撑住 13 个领域(法/教/医/金/制 + 8 篇)", font=font(15), fill=SUB)
    d.text((80, 450), "5 大重监管行业红线对照 · 8 种 AI 应用形态", font=font(15), fill=SUB)
    d.text((80, 478), "门槛不在技术 · 在认知 · 在你看不看得见红线", font=font(15, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 LANDSCAPE 13 篇 ============
def img_02():
    img, d = base()
    d.text((60, 40), "13 篇行业落地 · 全景表", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "8 篇带完整可跑代码(⭐)· 5 篇工具调度概念", font=font(15), fill=LIGHT)

    cases = [
        ("#1",  "绿电方案",      ORANGE_L,  "工具调度"),
        ("#2",  "合同审查",      PURPLE_L,  "多模型"),
        ("#3",  "知识库 Q&A",    BLUE_L,    "RAG"),
        ("#4",  "企业客服",      TEAL,      "Hooks"),
        ("#5",  "电商客服",      ROSE,      "下单闭环"),
        ("#6",  "全栈工作台 ⭐", GREEN_L,   "Vue+FastAPI"),
        ("#7",  "Vectorless ⭐", CYAN_L,    "PageIndex"),
        ("#8",  "学生论文 ⭐",   LIME,      "学术诚信"),
        ("#9",  "法律 ⭐",       PURPLE,    "执业责任"),
        ("#10", "教育 ⭐",       EMERALD,   "未成年保护"),
        ("#11", "医疗 ⭐",       PINK,      "急救熔断"),
        ("#12", "金融 ⭐",       GOLD,      "反诈+适当性"),
        ("#13", "制造 ⭐",       ORANGE,    "物理边界"),
    ]
    cols, bw, bh, gx, gy = 5, 192, 96, 12, 12
    start_x, start_y = 60, 116
    for i, (num, name, c, tag) in enumerate(cases):
        col, row = i % cols, i // cols
        x = start_x + col * (bw + gx)
        y = start_y + row * (bh + gy)
        rrect(d, [x, y, x + bw, y + bh], 10, fill=BOX, outline=c, width=2)
        rrect(d, [x + 8, y + 8, x + 56, y + 30], 6, fill=c)
        d.text((x + 14, y + 10), num, font=font(13, bold=True), fill=BG)
        d.text((x + 66, y + 10), name, font=font(14, bold=True), fill=c)
        d.text((x + 10, y + 38), tag, font=font(12), fill=SUB)
        d.text((x + 10, y + 62), "完整可跑" if "⭐" in name else "概念示例",
               font=font(10, bold=True), fill=GREEN_L if "⭐" in name else DIM)

    rrect(d, [60, 462, 1020, 510], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 478), "1 套骨架 · 13 种装填 · 模式行业无关 · 红线行业有关", font=font(17, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "02_landscape.png"))
    print("[OK] 02_landscape")


# ============ 03 5 大重监管红线对照(新)============
def img_03():
    img, d = base()
    d.text((60, 40), "5 大重监管行业 · 红线对照(最大干货)", font=font(22, bold=True), fill=AMBER)
    d.text((60, 76), "复制此表 = 你公司给法务 / 合规的一页 brief", font=font(14), fill=LIGHT)

    industries = [
        ("法律",  PURPLE,  "执业责任",       "律师签字",       "12 禁词",     "不下结论"),
        ("教育",  EMERALD, "未成年 + 双减",   "教师签字",       "8 标签词",    "不贴标签"),
        ("医疗",  PINK,    "执业 + 生命",     "医师签字",       "11 绝对词",   "不下诊断"),
        ("金融",  GOLD,    "持牌 + 投保",     "合规专员签字",   "16 荐股词",   "不荐股"),
        ("制造",  ORANGE,  "物理 + 工艺密",   "工艺 + QC 双签", "10 绝对词",   "不越边界"),
    ]

    headers = ["行业", "核心红线", "签字栏", "软化词数", "AI 不能"]
    col_x = [60, 200, 380, 560, 730]
    y_h = 122
    rrect(d, [60, y_h, 1020, y_h + 34], 6, fill=BOX, outline=LINE, width=1)
    for i, h in enumerate(headers):
        d.text((col_x[i] + 12, y_h + 9), h, font=font(13, bold=True), fill=AMBER)

    y0 = 168
    for r, (name, c, redline, signoff, soften, cannot) in enumerate(industries):
        y = y0 + r * 60
        rrect(d, [60, y, 1020, y + 52], 6, fill=BOX, outline=c, width=2)
        rrect(d, [72, y + 10, 188, y + 42], 6, fill=c)
        d.text((84, y + 16), name, font=font(15, bold=True), fill=BG)
        d.text((col_x[1] + 12, y + 16), redline, font=font(13, bold=True), fill=WHITE)
        d.text((col_x[2] + 12, y + 16), signoff, font=font(13), fill=SUB)
        d.text((col_x[3] + 12, y + 16), soften,  font=font(13), fill=SUB)
        d.text((col_x[4] + 12, y + 16), cannot,  font=font(13, bold=True), fill=c)

    rrect(d, [60, 488, 1020, 528], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 500), "5 行 = 5 个 AI 项目的开工清单 · 缺一不可", font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "03_redlines.png"))
    print("[OK] 03_redlines")


# ============ 04 任务×模型矩阵 ============
def img_04():
    img, d = base()
    d.text((60, 40), "任务 × 模型选型矩阵", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "锁单一供应商 = 锁短板 · 按任务分配 · 一个项目 3-4 模型常态", font=font(15), fill=LIGHT)

    rows = [
        ("长链推理 / 共情 / 合规",  "Claude Sonnet 4.5",  ORANGE),
        ("结构化提取 / 严格 JSON",  "GPT-5",              GREEN),
        ("多模态 / 图像 / PDF",     "Gemini 2.5 Pro",     BLUE),
        ("长上下文 (2M token)",     "Gemini 2.5 Pro",     BLUE),
        ("意图分类 / 路由",         "Claude Haiku",       ORANGE_L),
        ("风控 / 多变量评分",       "GPT-5",              GREEN),
        ("价格 / 数字密集",         "走数据库",           STEEL),
        ("召回 / 向量检索",         "Qdrant + BGE-M3",    TEAL),
        ("重排",                    "Cohere rerank-3.5",  CYAN),
        ("规则匹配",                "正则 + 规则引擎",    LIGHT),
    ]
    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    d.text((80, y0 + 8), "任务", font=font(14, bold=True), fill=AMBER)
    d.text((550, y0 + 8), "首选", font=font(14, bold=True), fill=AMBER)
    for i, (task, model, c) in enumerate(rows):
        y = y0 + 42 + i * 30
        rrect(d, [60, y, 1020, y + 26], 6, fill=DEEP)
        d.rectangle([60, y, 64, y + 26], fill=c)
        d.text((80, y + 5), task, font=font(13, bold=True), fill=WHITE)
        d.text((550, y + 5), model, font=mono(13), fill=c)

    rrect(d, [60, 478, 1020, 514], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 488), "工艺机密 / 病历 / 征信 → 私有部署 LLM(vLLM + 7B 开源)", font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "04_matrix.png"))
    print("[OK] 04_matrix")


# ============ 05 6 工程定律 ============
def img_05():
    img, d = base()
    d.text((60, 40), "6 大行业无关的工程定律", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "原 5 条 + #9-#13 新加第 6 条:红线先于功能", font=font(15), fill=LIGHT)

    laws = [
        ("1", "工具优先",       "LLM 不计算 · 数字/价格/状态全走工具",       ORANGE),
        ("2", "权限在数据层",   "向量库 filter + 行级 RBAC · 不靠 Prompt",   PURPLE),
        ("3", "Subagent 分工",  "Haiku 分流 · Sonnet 推理 · 成本压 1/5",     GREEN),
        ("4", "Hooks 守红线",   "价格 / 承诺 / 状态机 · LLM 在规则内自由",   PINK),
        ("5", "评测驱动",       "RAGAS / CSAT / DSAT · 跌 5% block 上线",   CYAN),
        ("6", "红线先于功能",   "熔断不进 LLM · 签字栏强制 · 硬边界阻断",    RED),
    ]
    y0 = 116
    for i, (n, name, desc, c) in enumerate(laws):
        y = y0 + i * 64
        rrect(d, [60, y, 1020, y + 54], 12, fill=BOX, outline=c, width=2)
        d.ellipse([76, y + 12, 124, y + 60], fill=c)
        d.text((90, y + 20), n, font=font(22, bold=True), fill=BG)
        d.text((148, y + 8), name, font=font(20, bold=True), fill=c)
        d.text((148, y + 34), desc, font=font(13), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "05_laws.png"))
    print("[OK] 05_laws")


# ============ 06 起步路径 + 5 误区 ============
def img_06():
    img, d = base()
    d.text((60, 40), "起步路径 · 5 个常见误区", font=font(26, bold=True), fill=AMBER)
    d.text((60, 78), "技术门槛不高 · 唯一稀缺的是产品理解", font=font(15), fill=LIGHT)

    d.text((60, 110), "从零到 MVP", font=font(17, bold=True), fill=GREEN_L)
    steps = [
        ("30 min", "装环境"),
        ("10 min", "拿 API key"),
        ("30 min", "Hello World"),
        ("1 h",    "加自定义工具"),
        ("0.5 day","加 Subagent + Hook"),
        ("1-2 day","接数据库"),
        ("2-3 day","接微信 / 飞书"),
        ("3 周",   "完整 MVP 上线"),
    ]
    y0 = 142
    for i, (t, s) in enumerate(steps):
        y = y0 + i * 34
        rrect(d, [60, y, 510, y + 28], 6, fill=BOX)
        rrect(d, [68, y + 4, 146, y + 24], 6, fill=GREEN)
        d.text((76, y + 6), t, font=font(11, bold=True), fill=BG)
        d.text((160, y + 6), s, font=font(14, bold=True), fill=WHITE)

    d.text((550, 110), "5 个常见误区", font=font(17, bold=True), fill=ROSE)
    pitfalls = [
        ("误区 1", "Agent = 一个超大 Prompt"),
        ("误区 2", "模型越大越好"),
        ("误区 3", "评测可以后补"),
        ("误区 4", "越自动越好(60-80% 最优)"),
        ("误区 5", "涉密用公有云 LLM(应私有部署)"),
    ]
    y0 = 142
    for i, (n, t) in enumerate(pitfalls):
        y = y0 + i * 54
        rrect(d, [550, y, 1020, y + 46], 8, fill=BOX, outline=ROSE, width=1)
        d.text((566, y + 6), n, font=font(12, bold=True), fill=ROSE)
        d.text((566, y + 24), t, font=font(13), fill=SUB)

    rrect(d, [60, 462, 1020, 510], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 478), "唯一稀缺的是产品理解 · 不是算法 · 不是工程", font=font(15, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "06_path.png"))
    print("[OK] 06_path")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    img_06()
    print("\n[DONE] 6 images saved to", OUT)
