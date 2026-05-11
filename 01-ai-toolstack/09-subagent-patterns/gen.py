# -*- coding: utf-8 -*-
"""5 images for Subagent 模式深度 · AI 工具栈 #09"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# 紫蓝主题 · 分工协作感
BG       = "#1a1438"
BOX      = "#2a1f5c"
DEEP     = "#0f0a26"
LINE     = "#3d2f7d"
WHITE    = "#ffffff"
SUB      = "#dcd4f4"
LIGHT    = "#a596d4"
DIM      = "#6e5fa0"
PURPLE   = "#a78bfa"
PURPLE_L = "#c4b5fd"
PURPLE_D = "#8b5cf6"
INDIGO   = "#818cf8"
INDIGO_L = "#a5b4fc"
BLUE     = "#60a5fa"
BLUE_L   = "#93c5fd"
CYAN     = "#67e8f9"
TEAL     = "#5eead4"
GREEN    = "#86efac"
EMERALD  = "#34d399"
LIME     = "#bef264"
YELLOW   = "#fde047"
AMBER    = "#fbbf24"
ORANGE   = "#fdba74"
PINK     = "#f9a8d4"
PINK_D   = "#ec4899"
ROSE     = "#fb7185"
RED      = "#f87171"

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
    rrect(d, [60, 50, 240, 88], 19, fill=PURPLE)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 #09", font=font(17, bold=True), fill=PURPLE_L)

    d.text((60, 128), "Subagent 模式深度", font=font(44, bold=True), fill=PURPLE_L)
    d.text((60, 188), "Claude SDK 视角的多 Agent 协作", font=font(22, bold=True), fill=WHITE)
    d.text((60, 226), "5 经典模式 · 3 家对照 · 5 反模式", font=font(18), fill=SUB)

    chips = [
        ("独立 context",    INDIGO_L,  "干净窗口 · 防 bias"),
        ("声明式 .md",      BLUE_L,    "改文件即生效"),
        ("分模型省钱",      EMERALD,   "Haiku 分诊 · 1/5 成本"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(14), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=PURPLE, width=2)
    d.text((80, 444), "Subagent 不是扩展能力 · 是约束能力", font=font(20, bold=True), fill=PURPLE_L)
    d.text((80, 478), "主动给 LLM 戴上专业眼罩 · 才在工业级场景能用", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 实现机制 · .md 文件结构 ============
def img_02():
    img, d = base()
    d.text((60, 40), "Claude SDK · Subagent 实现机制", font=font(26, bold=True), fill=PURPLE_L)
    d.text((60, 78), "反直觉但极简:Markdown 文件 + 4 个关键字段", font=font(15), fill=LIGHT)

    # 文件结构示意
    rrect(d, [60, 116, 540, 480], 14, fill=BOX, outline=INDIGO, width=2)
    d.text((78, 130), "项目根目录/", font=font(17, bold=True), fill=PURPLE_L)
    tree = [
        ("├── .claude/",            PURPLE_L),
        ("│   └── agents/",         PURPLE_L),
        ("│       ├── triager.md",  INDIGO_L),
        ("│       ├── researcher.md",  INDIGO_L),
        ("│       ├── validator.md",   INDIGO_L),
        ("│       ├── specialist.md",  INDIGO_L),
        ("│       └── critic.md",      INDIGO_L),
        ("└── main.py",             SUB),
    ]
    for i, (line, c) in enumerate(tree):
        d.text((78, 162 + i * 26), line, font=mono(15), fill=c)

    # .md 文件结构(右侧)
    rrect(d, [560, 116, 1020, 480], 14, fill=BOX, outline=PINK_D, width=2)
    d.text((578, 130), "researcher.md", font=font(17, bold=True), fill=PINK)
    md = [
        ('---',                                       SUB),
        ('name: researcher',                          AMBER),
        ('description: 联网研究 ...',                  YELLOW),
        ('model: claude-sonnet-4-5',                  EMERALD),
        ('tools:',                                    BLUE_L),
        ('  - WebSearch',                             BLUE_L),
        ('  - WebFetch',                              BLUE_L),
        ('---',                                       SUB),
        ('',                                          WHITE),
        ('你是研究员 Subagent。',                      WHITE),
        ('1. WebSearch 找 3-5 源',                    SUB),
        ('2. WebFetch 读关键 source',                 SUB),
        ('3. 200 字含引用源简报',                     SUB),
        ('4. 不要给建议 · 只归集',                    PINK),
    ]
    for i, (line, c) in enumerate(md):
        d.text((578, 162 + i * 22), line, font=mono(13), fill=c)

    # 底部 4 关键字段
    rrect(d, [60, 500, 1020, 540], 8, fill=DEEP, outline=PURPLE, width=1)
    d.text((80, 512), "4 关键字段:name(标识)/ description(自动路由)/ model(分模型)/ tools(白名单)",
           font=font(13, bold=True), fill=PURPLE_L)

    watermark(d)
    img.save(os.path.join(OUT, "02_mechanism.png"))
    print("[OK] 02_mechanism")


# ============ 03 5 经典模式 ============
def img_03():
    img, d = base()
    d.text((60, 40), "5 个经典 Subagent 模式", font=font(26, bold=True), fill=PURPLE_L)
    d.text((60, 78), "13 篇行业落地反复出现 · 收藏直接抄", font=font(15), fill=LIGHT)

    patterns = [
        ("①", "Triager 分诊员",     "Haiku · 干净 context · 单成本 1/5",   "客服 / 法律 / 医疗 第一步", BLUE_L),
        ("②", "Researcher 研究员",  "联网拿原料 · 主 Agent 别上网",        "事实 / 数据 / 引用源",      EMERALD),
        ("③", "Validator 校验员",   "独立 context 防 bias · 像新人审老员", "合同审查漏判 8% → 1.8%",   AMBER),
        ("④", "Specialist 领域专家", "Prompt 锁能力 · 比主 Agent 更窄",     "法律 / 医疗 / 工艺专家",   PINK),
        ("⑤", "Critic 评审员",      "给改进点 · 不重写 · 循环改稿",         "文案 / 代码 / 方案",       ORANGE),
    ]
    y0 = 116
    for i, (n, name, desc, scene, c) in enumerate(patterns):
        y = y0 + i * 76
        rrect(d, [60, y, 1020, y + 66], 12, fill=BOX, outline=c, width=2)
        rrect(d, [80, y + 12, 300, y + 54], 8, fill=c)
        d.text((96, y + 18), n, font=font(20, bold=True), fill=BG)
        d.text((124, y + 18), name, font=font(18, bold=True), fill=BG)
        d.text((324, y + 12), desc, font=font(14, bold=True), fill=WHITE)
        d.text((324, y + 38), "典型场景:" + scene, font=font(12), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "03_patterns.png"))
    print("[OK] 03_patterns")


# ============ 04 自动路由 vs 显式调用 ============
def img_04():
    img, d = base()
    d.text((60, 40), "调用方式 · 自动路由 vs 显式调用", font=font(26, bold=True), fill=PURPLE_L)
    d.text((60, 78), "评测期显式 · 生产环境自动", font=font(15), fill=LIGHT)

    # 左:自动路由
    rrect(d, [60, 116, 540, 460], 14, fill=BOX, outline=EMERALD, width=2)
    d.text((78, 132), "自动路由(SDK 默认)", font=font(17, bold=True), fill=EMERALD)
    auto = [
        "主 Agent 读所有 .md 的 description",
        "自己决定调哪个 Subagent",
        "",
        "[优点]",
        "  · 声明式 · 加新 Subagent 不改主 prompt",
        "  · 灵活 · 自适应任务",
        "",
        "[缺点]",
        "  · 路由有时不准",
        "  · 调试困难",
        "",
        "写好 description:",
        "  「当 X 时调用 · 返回 Y 格式的 Z」",
        "  越窄越好",
    ]
    for i, line in enumerate(auto):
        d.text((78, 162 + i * 21), line, font=font(13), fill=SUB)

    # 右:显式调用
    rrect(d, [560, 116, 1020, 460], 14, fill=BOX, outline=AMBER, width=2)
    d.text((578, 132), "显式调用(@subagent)", font=font(17, bold=True), fill=AMBER)
    explicit = [
        "在 prompt 里点名调用",
        "@researcher 研究 X · @critic 评审",
        "",
        "[优点]",
        "  · 确定性高",
        "  · 调试方便 · 评测可控",
        "",
        "[缺点]",
        "  · 主 prompt 写死 · 失去声明式",
        "",
        "推荐用法:",
        "  · 评测期 → 显式(可复现)",
        "  · 生产环境 → 自动(灵活)",
        "",
    ]
    for i, line in enumerate(explicit):
        d.text((578, 162 + i * 21), line, font=font(13), fill=SUB)

    rrect(d, [60, 480, 1020, 540], 10, fill=DEEP, outline=PURPLE, width=1)
    d.text((80, 498), "★ 关键洞察:description 决定路由准确率", font=font(15, bold=True), fill=PURPLE_L)
    d.text((80, 520), "好 description = 「当 X 时调用 · 返回 Y 格式的 Z」",
           font=font(13), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "04_routing.png"))
    print("[OK] 04_routing")


# ============ 05 三家对照 ============
def img_05():
    img, d = base()
    d.text((60, 40), "三家多 Agent 协作 · 对照", font=font(26, bold=True), fill=PURPLE_L)
    d.text((60, 78), "Claude / OpenAI / Google · 形态各异 · 该谁强用谁", font=font(15), fill=LIGHT)

    headers = ["维度", "Claude Subagent", "OpenAI Handoff", "Google ADK Seq/Loop"]
    col_x = [60, 220, 480, 760]
    y0 = 122
    rrect(d, [60, y0, 1020, y0 + 34], 8, fill=BOX)
    colors_h = [WHITE, ORANGE, EMERALD, BLUE_L]
    for i, h in enumerate(headers):
        d.text((col_x[i] + 12, y0 + 9), h, font=font(14, bold=True), fill=colors_h[i])

    rows = [
        ("定义形态", ".md 文件",       "Agent(handoffs=)",  "SequentialAgent"),
        ("控制流",   "保持控制权",      "控制权转移",         "强编排流程"),
        ("Context",  "独立 + 干净",     "独立",               "独立 + 共享 state"),
        ("路由",     "description 自动", "handoff 描述",       "无路由 · 只流程"),
        ("类比",     "找专家咨询",      "转介给部门",         "流水线工作流"),
        ("强项",     "轻量 + 声明式",   "工具循环 + Tracing", "复杂流程编排"),
        ("适合",     "分诊 / 研究 / 审核", "客服转移 / 权流转",  "多步串行 / 并行"),
    ]
    for i, (axis, cl, op, gg) in enumerate(rows):
        y = y0 + 38 + i * 44
        rrect(d, [60, y, 1020, y + 38], 8, fill=DEEP, outline=LINE, width=1)
        d.rectangle([60, y, 64, y + 38], fill=PURPLE)
        d.text((col_x[0] + 12, y + 11), axis, font=font(14, bold=True), fill=WHITE)
        d.text((col_x[1] + 12, y + 11), cl,   font=font(13),            fill=ORANGE)
        d.text((col_x[2] + 12, y + 11), op,   font=font(13),            fill=EMERALD)
        d.text((col_x[3] + 12, y + 11), gg,   font=font(13),            fill=BLUE_L)

    rrect(d, [60, 488, 1020, 540], 10, fill=DEEP, outline=PURPLE, width=1)
    d.text((80, 502), "★ 混搭策略:分诊用 Claude · 转移用 OpenAI · 流程用 Google", font=font(14, bold=True), fill=PURPLE_L)
    d.text((80, 522), "一层 LiteLLM 封装 · 三家 SDK 同台演出", font=font(12), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "05_compare.png"))
    print("[OK] 05_compare")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
