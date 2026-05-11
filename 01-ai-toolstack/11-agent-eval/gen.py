# -*- coding: utf-8 -*-
"""8 images for Agent Eval 体系完整指南 · AI 工具栈 #11"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# 评测主题 · 蓝紫 + 多色(4 工具各一色)
BG       = "#0a1228"
BOX      = "#182240"
DEEP     = "#050a18"
LINE     = "#2a3960"
WHITE    = "#ffffff"
SUB      = "#cfd9eb"
LIGHT    = "#94a3c4"
DIM      = "#5b6a87"
INDIGO   = "#818cf8"
INDIGO_L = "#a5b4fc"
PURPLE   = "#a855f7"      # RAGAS
PURPLE_L = "#c084fc"
CYAN     = "#22d3ee"      # Phoenix
CYAN_L   = "#67e8f9"
GREEN    = "#10b981"      # Langfuse
GREEN_L  = "#34d399"
AMBER    = "#fbbf24"      # OpenAI Tracing
AMBER_L  = "#fde047"
ORANGE   = "#fb923c"
ORANGE_L = "#fdba74"
PINK_L   = "#f9a8d4"
RED      = "#ef4444"
RED_L    = "#fca5a5"

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
    rrect(d, [60, 50, 240, 88], 19, fill=INDIGO)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 #11", font=font(17, bold=True), fill=INDIGO_L)

    d.text((60, 128), "Agent Eval 体系", font=font(42, bold=True), fill=INDIGO_L)
    d.text((60, 188), "RAGAS / Phoenix / Langfuse / OpenAI", font=font(22, bold=True), fill=WHITE)
    d.text((60, 226), "四方对照 + 3 层指标金字塔 + CI 集成", font=font(18), fill=SUB)

    # 4 工具 chip
    chips = [
        ("RAGAS",          PURPLE_L, "RAG 4 指标 · 行业标准"),
        ("Phoenix",        CYAN_L,   "OTel 原生 · 框架最广"),
        ("Langfuse",       GREEN_L,  "开源 traces · UI 最赞"),
        ("OpenAI Tracing", AMBER_L,  "SDK 自带 · 零配置"),
    ]
    y = 290
    cw = 230
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * (cw + 10)
        rrect(d, [x, y, x + cw, y + 92], 12, fill=BOX, outline=c, width=2)
        d.text((x + 16, y + 14), kw, font=font(20, bold=True), fill=c)
        d.text((x + 16, y + 52), desc, font=font(12), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=INDIGO, width=2)
    d.text((80, 444), "没评测就没生产 · 跌 5% 自动 block 上线", font=font(20, bold=True), fill=INDIGO_L)
    d.text((80, 478), "AI 应用核心竞争力不是 prompt 写得好 · 是 eval 跑得勤", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 3 层指标金字塔 ============
def img_02():
    img, d = base()
    d.text((60, 40), "3 层指标金字塔 · 任何 AI 应用都成立", font=font(26, bold=True), fill=INDIGO_L)
    d.text((60, 78), "底层稳了 · 业务指标才会稳", font=font(15), fill=LIGHT)

    # 金字塔(倒三角)
    levels = [
        (3, "业务指标 · 最终判官",      "CSAT / FCR / 转化率 / 营收",                            350, 130, AMBER),
        (2, "Agent 行为指标",          "工具调用正确率 / 步数 / Containment / Token / 延迟",   220, 280, ORANGE),
        (1, "RAG / LLM 输出质量",      "Faithfulness / Relevancy / Precision / Recall · Toxicity", 90, 430, GREEN),
    ]
    for n, name, desc, x, y, c in levels:
        w = 1080 - 2 * x
        rrect(d, [x, y, x + w, y + 100], 16, fill=BOX, outline=c, width=2)
        # 层数 badge
        rrect(d, [x + 20, y + 18, x + 80, y + 78], 12, fill=c)
        d.text((x + 38, y + 28), f"#{n}", font=font(22, bold=True), fill=BG)
        d.text((x + 100, y + 22), name, font=font(18, bold=True), fill=c)
        d.text((x + 100, y + 52), desc, font=font(13), fill=SUB)

    # 工具标注
    d.text((900, 140), "← 业务系统", font=font(13), fill=AMBER_L)
    d.text((780, 290), "← Phoenix / Langfuse", font=font(13), fill=ORANGE_L)
    d.text((730, 440), "← RAGAS 强项", font=font(13), fill=GREEN_L)

    watermark(d)
    img.save(os.path.join(OUT, "02_pyramid.png"))
    print("[OK] 02_pyramid")


# ============ 03 RAGAS · 4 核心指标 ============
def img_03():
    img, d = base()
    d.text((60, 40), "RAGAS · 4 个核心指标", font=font(26, bold=True), fill=PURPLE_L)
    d.text((60, 78), "生成端 2 个 + 检索端 2 个 · 记住口诀", font=font(15), fill=LIGHT)

    # 左:生成端
    rrect(d, [60, 124, 540, 460], 14, fill=BOX, outline=GREEN, width=2)
    d.text((78, 138), "生成端(防 LLM 出错)", font=font(17, bold=True), fill=GREEN_L)
    gen = [
        ("①  Faithfulness",       "答案是否忠于检索到的 context",   "防编造"),
        ("②  Answer Relevancy",   "答案是否回应了问题",             "防答非所问"),
    ]
    for i, (name, desc, tag) in enumerate(gen):
        y = 180 + i * 130
        rrect(d, [78, y, 522, y + 116], 10, fill=DEEP, outline=GREEN_L, width=1)
        d.text((92, y + 14), name, font=font(18, bold=True), fill=GREEN_L)
        d.text((92, y + 48), desc, font=font(14), fill=WHITE)
        rrect(d, [92, y + 78, 92 + 96, y + 104], 6, fill=GREEN)
        d.text((104, y + 82), tag, font=font(13, bold=True), fill=BG)

    # 右:检索端
    rrect(d, [560, 124, 1020, 460], 14, fill=BOX, outline=AMBER, width=2)
    d.text((578, 138), "检索端(防向量库出错)", font=font(17, bold=True), fill=AMBER_L)
    ret = [
        ("③  Context Precision", "检索 chunk 里有用的多吗",   "防废料"),
        ("④  Context Recall",    "该召回的 chunk 都召回了吗", "防漏召"),
    ]
    for i, (name, desc, tag) in enumerate(ret):
        y = 180 + i * 130
        rrect(d, [578, y, 1002, y + 116], 10, fill=DEEP, outline=AMBER_L, width=1)
        d.text((592, y + 14), name, font=font(18, bold=True), fill=AMBER_L)
        d.text((592, y + 48), desc, font=font(14), fill=WHITE)
        rrect(d, [592, y + 78, 592 + 96, y + 104], 6, fill=AMBER)
        d.text((604, y + 82), tag, font=font(13, bold=True), fill=BG)

    rrect(d, [60, 478, 1020, 528], 8, fill=DEEP, outline=PURPLE, width=1)
    d.text((80, 492), "★ 13 篇行业落地里 4 篇 RAG 重 · 全部用 RAGAS(#03 / #07 / #08 / 综述)",
           font=font(13, bold=True), fill=PURPLE_L)

    watermark(d)
    img.save(os.path.join(OUT, "03_ragas.png"))
    print("[OK] 03_ragas")


# ============ 04 Phoenix ============
def img_04():
    img, d = base()
    d.text((60, 40), "Phoenix · OTel 原生 + 4 能力", font=font(26, bold=True), fill=CYAN_L)
    d.text((60, 78), "Arize 出品 · 自托管 + 商业云双轨 · 框架覆盖最广", font=font(15), fill=LIGHT)

    abilities = [
        ("Traces",     "全链路追踪 · LLM/Tool/Retriever 调用", CYAN_L),
        ("Evals",      "内置 LLM-as-Judge · 跟 RAGAS 对齐",   GREEN_L),
        ("Experiments","A/B 同 prompt 不同模型 · 出报表",      AMBER_L),
        ("Datasets",   "测试集管理 · golden 版本化",           PURPLE_L),
    ]
    y0 = 120
    for i, (name, desc, c) in enumerate(abilities):
        y = y0 + i * 76
        rrect(d, [60, y, 1020, y + 66], 12, fill=BOX, outline=c, width=2)
        rrect(d, [80, y + 12, 280, y + 54], 8, fill=c)
        d.text((96, y + 22), name, font=font(20, bold=True), fill=BG)
        d.text((304, y + 22), desc, font=font(15, bold=True), fill=WHITE)

    # 集成示例
    rrect(d, [60, 440, 1020, 540], 10, fill=DEEP, outline=CYAN, width=1)
    d.text((80, 456), "30+ 内置框架 instrumentor:", font=font(13, bold=True), fill=CYAN_L)
    d.text((80, 480), "OpenAI · Anthropic · Gemini · LangChain · Llama Index · DSPy · CrewAI ...", font=mono(13), fill=SUB)
    d.text((80, 508), "★ 跟 Datadog / Grafana / ELK 通过 OTel 一行接入", font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "04_phoenix.png"))
    print("[OK] 04_phoenix")


# ============ 05 Langfuse ============
def img_05():
    img, d = base()
    d.text((60, 40), "Langfuse · 开源 traces 王者 + Prompt 管理", font=font(26, bold=True), fill=GREEN_L)
    d.text((60, 78), "Self-host Docker 一行 · UI 最产品化 · 50K traces/月免费", font=font(15), fill=LIGHT)

    abilities = [
        ("Tracing",            "全链路追踪 · UI 最产品化 · 给非工程师看也友好", GREEN_L),
        ("Scoring",            "多维度打分 · 人工 + LLM Judge + 自定义",      AMBER_L),
        ("Prompt Management",  "Prompt 版本化 · 改 UI 不改代码 · 杀手锏",    PURPLE_L),
        ("Datasets",           "黄金集管理 · 关联 traces 看回归",            CYAN_L),
    ]
    y0 = 120
    for i, (name, desc, c) in enumerate(abilities):
        y = y0 + i * 76
        rrect(d, [60, y, 1020, y + 66], 12, fill=BOX, outline=c, width=2)
        rrect(d, [80, y + 12, 320, y + 54], 8, fill=c)
        d.text((96, y + 22), name, font=font(18, bold=True), fill=BG)
        d.text((342, y + 22), desc, font=font(14, bold=True), fill=WHITE)

    rrect(d, [60, 440, 1020, 540], 10, fill=DEEP, outline=GREEN, width=1)
    d.text((80, 456), "★ 重监管行业首选(法/医/金/制):", font=font(13, bold=True), fill=GREEN_L)
    d.text((80, 480), "Prompt 版本审计 + 人工 scoring + 自托管 + audit log · 合规全打钩", font=font(13), fill=SUB)
    d.text((80, 508), "docker run -p 3000:3000 langfuse/langfuse:latest  · 一行起服务", font=mono(12), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "05_langfuse.png"))
    print("[OK] 05_langfuse")


# ============ 06 OpenAI Tracing ============
def img_06():
    img, d = base()
    d.text((60, 40), "OpenAI Tracing · Agents SDK 零配置内置", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "什么都不用配 · 自动上传 platform.openai.com/traces", font=font(15), fill=LIGHT)

    # 左:用法(代码)
    rrect(d, [60, 116, 540, 480], 14, fill=BOX, outline=GREEN, width=2)
    d.text((78, 132), "用法 · 真的什么都不用配", font=font(16, bold=True), fill=GREEN_L)
    code = [
        "from agents import Agent, Runner",
        "",
        "agent = Agent(",
        '    name="助手",',
        '    model="gpt-5",',
        ")",
        "",
        "result = Runner.run_sync(",
        '    agent, "你好"',
        ")",
        "",
        "# 跑完看:",
        "# platform.openai.com/traces",
        "",
        "# 涉密关闭:",
        "OPENAI_AGENTS_DISABLE_",
        "    TRACING=1",
    ]
    for i, line in enumerate(code):
        d.text((78, 162 + i * 19), line, font=mono(13), fill=SUB)

    # 右:对照表
    rrect(d, [560, 116, 1020, 480], 14, fill=BOX, outline=RED, width=2)
    d.text((578, 132), "[警告] 涉密场景的限制", font=font(16, bold=True), fill=RED_L)
    warns = [
        ("✗", "强绑定 OpenAI 平台", RED_L),
        ("✗", "数据自动上传云端", RED_L),
        ("✗", "只覆盖 OpenAI Agents SDK", RED_L),
        ("✗", "Claude / Gemini 不管", RED_L),
        ("", "", WHITE),
        ("→", "开发调试可用 · 涉密生产关掉", AMBER_L),
        ("→", "替代方案:Langfuse 自托管", GREEN_L),
        ("→", "或 Phoenix 自托管", CYAN_L),
        ("→", "改 SDK 跑 set_trace_processors", INDIGO_L),
    ]
    for i, (mark, line, c) in enumerate(warns):
        y = 162 + i * 30
        d.text((578, y), mark, font=font(16, bold=True), fill=c)
        d.text((610, y), line, font=font(14), fill=c)

    rrect(d, [60, 500, 1020, 540], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 514), "★ 学习曲线 0 分钟 · 但跟 [#10 防泄密] 冲突 · 涉密生产必关",
           font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "06_openai_tracing.png"))
    print("[OK] 06_openai_tracing")


# ============ 07 四方对照矩阵 ============
def img_07():
    img, d = base()
    d.text((60, 40), "四方对照 · 本文最重要的一张表", font=font(26, bold=True), fill=INDIGO_L)
    d.text((60, 78), "选哪个 / 怎么混搭 · 一图说清", font=font(15), fill=LIGHT)

    # header
    headers = ["维度", "RAGAS", "Phoenix", "Langfuse", "OpenAI"]
    col_x   = [60, 250, 430, 620, 820]
    head_c  = [WHITE, PURPLE_L, CYAN_L, GREEN_L, AMBER_L]
    y0 = 116
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    for i, h in enumerate(headers):
        d.text((col_x[i] + 12, y0 + 8), h, font=font(13, bold=True), fill=head_c[i])

    rows = [
        ("RAG 评测",    "★★★★★", "★★★★",  "★★★",   "—"),
        ("Agent traces","—",      "★★★★",  "★★★★★","★★★★"),
        ("LLM Judge",   "★★★★",  "★★★★★","★★★",  "—"),
        ("Prompt 管理", "—",      "★★",    "★★★★★","—"),
        ("OTel 原生",   "—",      "★★★★★","★★★",  "—"),
        ("开源",        "是",     "是",    "是",    "否"),
        ("自托管",      "本地",   "Docker","Docker","云端"),
        ("涉密兼容",    "是",     "是",    "是",    "否"),
        ("学习曲线",    "10 min", "1 h",   "30 min","0"),
    ]
    for i, (axis, r, p, l, o) in enumerate(rows):
        y = y0 + 38 + i * 36
        rrect(d, [60, y, 1020, y + 30], 5, fill=DEEP)
        d.rectangle([60, y, 64, y + 30], fill=INDIGO)
        d.text((col_x[0] + 12, y + 7), axis, font=font(13, bold=True), fill=WHITE)
        d.text((col_x[1] + 12, y + 7), r,    font=font(13),            fill=PURPLE_L)
        d.text((col_x[2] + 12, y + 7), p,    font=font(13),            fill=CYAN_L)
        d.text((col_x[3] + 12, y + 7), l,    font=font(13),            fill=GREEN_L)
        d.text((col_x[4] + 12, y + 7), o,    font=font(13),            fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "07_compare.png"))
    print("[OK] 07_compare")


# ============ 08 决策树 ============
def img_08():
    img, d = base()
    d.text((60, 40), "怎么选 · 决策树", font=font(26, bold=True), fill=INDIGO_L)
    d.text((60, 78), "按场景 + 涉密性 + 框架兼容性 · 6 种推荐组合", font=font(15), fill=LIGHT)

    scenarios = [
        ("纯 RAG / 知识库",      "RAGAS + Langfuse",                "RAG 4 指标 + traces",        PURPLE_L),
        ("Agent · 开发期",        "OpenAI Tracing(免费)/ Langfuse", "零配置 · 快速调试",          AMBER_L),
        ("Agent · 生产非涉密",    "Phoenix / Langfuse",              "OTel 接入 · UI 友好",        CYAN_L),
        ("Agent · 涉密 (法/医/金/制)", "Langfuse 自托管(关掉 OpenAI)", "合规 + 自托管 + audit",    GREEN_L),
        ("全栈应用 · 多模型混搭", "Phoenix",                          "30+ 框架 instrumentor",      CYAN_L),
        ("大企业 · 已有 ELK / Grafana", "Phoenix(OTel 原生)",        "现成监控栈一行接入",         CYAN_L),
    ]
    y0 = 120
    for i, (scene, pick, reason, c) in enumerate(scenarios):
        y = y0 + i * 64
        rrect(d, [60, y, 1020, y + 54], 12, fill=BOX, outline=c, width=2)
        rrect(d, [78, y + 8, 380, y + 46], 8, fill=c)
        d.text((90, y + 17), scene, font=font(15, bold=True), fill=BG)
        d.text((400, y + 6), "→ " + pick, font=font(15, bold=True), fill=WHITE)
        d.text((400, y + 30), reason, font=font(12), fill=SUB)

    rrect(d, [60, 504, 1020, 540], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 516), "★ 多数项目最终是 2-3 个工具混搭 · 不是非此即彼",
           font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "08_decision.png"))
    print("[OK] 08_decision")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    img_06()
    img_07()
    img_08()
    print("\n[DONE] 8 images saved to", OUT)
