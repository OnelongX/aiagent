# -*- coding: utf-8 -*-
"""5 images for Production Agent 部署 · AI 工具栈 #12"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# Production 主题 · 深蓝 + 青蓝(infrastructure)
BG       = "#051428"
BOX      = "#0e2244"
DEEP     = "#020a18"
LINE     = "#1f3a60"
WHITE    = "#ffffff"
SUB      = "#cfd9eb"
LIGHT    = "#94a8c4"
DIM      = "#5b6a87"
CYAN     = "#06b6d4"
CYAN_L   = "#67e8f9"
CYAN_D   = "#0891b2"
TEAL     = "#14b8a6"
BLUE     = "#3b82f6"
BLUE_L   = "#60a5fa"
INDIGO_L = "#a5b4fc"
GREEN    = "#10b981"
GREEN_L  = "#34d399"
EMERALD  = "#6ee7b7"
AMBER    = "#fbbf24"
AMBER_L  = "#fde047"
ORANGE   = "#fb923c"
ORANGE_L = "#fdba74"
RED      = "#ef4444"
RED_L    = "#fca5a5"
PURPLE_L = "#c084fc"
PINK_L   = "#f9a8d4"

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
    rrect(d, [60, 50, 240, 88], 19, fill=CYAN)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 #12", font=font(17, bold=True), fill=CYAN_L)

    d.text((60, 128), "Production Agent 部署", font=font(40, bold=True), fill=CYAN_L)
    d.text((60, 188), "K8s + HPA + 灰度 + 回滚", font=font(22, bold=True), fill=WHITE)
    d.text((60, 226), "6 维差异 + 3 层版本 + 5 事故复盘", font=font(18), fill=SUB)

    chips = [
        ("token QPS",       AMBER_L,   "不是 RPS · HPA 用 KEDA"),
        ("多 endpoint",     GREEN_L,   "LiteLLM 自动 fallback"),
        ("3 层版本",        PURPLE_L,  "代码 / Prompt / 模型"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(13), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=CYAN, width=2)
    d.text((80, 444), "AI Agent = SRE + MLOps + Prompt Engineering 三者交集", font=font(20, bold=True), fill=CYAN_L)
    d.text((80, 478), "任一维度想偷懒 · 生产就在哪一维度炸", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 6 维差异 ============
def img_02():
    img, d = base()
    d.text((60, 40), "Production Agent · 跟传统 Web 的 6 维差异", font=font(24, bold=True), fill=CYAN_L)
    d.text((60, 78), "AI Agent 多 6 个独特维度 · 任一没处理生产就炸", font=font(15), fill=LIGHT)

    headers = ["维度", "传统 Web", "AI Agent", "工程对策"]
    col_x = [60, 220, 440, 700]
    y0 = 122
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    for i, h in enumerate(headers):
        d.text((col_x[i] + 12, y0 + 8), h, font=font(13, bold=True), fill=CYAN_L)

    rows = [
        ("流量单位",   "RPS",         "token QPS",          "HPA 用 token throughput"),
        ("依赖",       "DB / Cache",  "+ LLM endpoint",     "LiteLLM 多 endpoint fallback"),
        ("失败模式",   "5xx",         "+ 限流 + 漂移",       "retry + 健康检查 + circuit breaker"),
        ("版本管理",   "代码",         "+ Prompt + 模型",    "3 层独立回滚"),
        ("成本",       "服务器固定",   "token 易爆炸",       "budget 限流 + 全局告警"),
        ("测试",       "单元 / 集成",  "+ Eval(#11)",        "CI 跑 eval · 跌 5% block"),
    ]
    colors_v = [WHITE, LIGHT, AMBER_L, GREEN_L]
    for i, row in enumerate(rows):
        y = y0 + 38 + i * 50
        rrect(d, [60, y, 1020, y + 44], 8, fill=DEEP, outline=LINE, width=1)
        d.rectangle([60, y, 64, y + 44], fill=CYAN)
        for j, val in enumerate(row):
            d.text((col_x[j] + 12, y + 14), val, font=font(13, bold=True if j == 0 else False), fill=colors_v[j])

    watermark(d)
    img.save(os.path.join(OUT, "02_diff.png"))
    print("[OK] 02_diff")


# ============ 03 3 种部署形态 ============
def img_03():
    img, d = base()
    d.text((60, 40), "3 种部署形态 · 按规模选", font=font(26, bold=True), fill=CYAN_L)
    d.text((60, 78), "PoC → 中流量 → 涉密大规模", font=font(15), fill=LIGHT)

    # (n, name, scope, deploy, deploy_is_mono, color)
    forms = [
        ("A", "单实例 Docker",   "< 10 RPS / PoC / 内部 demo",      "docker compose up",          True,  GREEN_L),
        ("B", "K8s + HPA",      "10-1000 RPS / 多租户 / 生产中流量", "kubectl apply -f manifests/", True,  CYAN_L),
        ("C", "混合云 + 私有 LLM","涉密 + 大规模 · 法/医/金/制",      "公网 K8s + 内网 vLLM",        False, ORANGE_L),
    ]
    y0 = 124
    for i, (n, name, scope, deploy, deploy_mono, c) in enumerate(forms):
        y = y0 + i * 120
        rrect(d, [60, y, 1020, y + 100], 14, fill=BOX, outline=c, width=2)
        rrect(d, [80, y + 18, 160, y + 80], 12, fill=c)
        d.text((110, y + 36), n, font=font(36, bold=True), fill=BG)
        d.text((190, y + 16), name, font=font(22, bold=True), fill=c)
        d.text((190, y + 50), "适合:" + scope, font=font(14), fill=WHITE)
        d.text((190, y + 74), "部署:" + deploy, font=(mono(13) if deploy_mono else font(13)), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "03_topology.png"))
    print("[OK] 03_topology")


# ============ 04 自动伸缩 · 3 信号 ============
def img_04():
    img, d = base()
    d.text((60, 40), "自动伸缩 · 不只看 CPU", font=font(26, bold=True), fill=CYAN_L)
    d.text((60, 78), "LLM 调用是 I/O 等待 · CPU 几乎不动 · 用 KEDA + 自定义指标", font=font(15), fill=LIGHT)

    signals = [
        ("inflight_llm_requests", "当前在飞 LLM 请求数",         "> 5/pod 扩容",   "主信号",    CYAN_L),
        ("p95_latency_ms",         "长尾延迟 · 用户体验指标",      "> 5000ms 扩容",  "副信号",    AMBER_L),
        ("llm_429_rate",           "上游限流率",                   "> 1% 扩容 + 切换", "故障信号", RED_L),
    ]
    y0 = 124
    for i, (metric, desc, threshold, tag, c) in enumerate(signals):
        y = y0 + i * 96
        rrect(d, [60, y, 1020, y + 80], 14, fill=BOX, outline=c, width=2)
        # mono 名字
        rrect(d, [80, y + 16, 460, y + 48], 8, fill=DEEP, outline=c, width=1)
        d.text((92, y + 21), metric, font=mono(15), fill=c)
        # tag
        rrect(d, [480, y + 16, 600, y + 48], 8, fill=c)
        d.text((500, y + 24), tag, font=font(13, bold=True), fill=BG)
        # desc + 阈值
        d.text((80, y + 56), desc, font=font(13), fill=SUB)
        d.text((600, y + 56), threshold, font=font(13, bold=True), fill=c)

    rrect(d, [60, 432, 1020, 540], 12, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 448), "★ 扩快缩慢:扩容窗口 30s · 缩容窗口 300s · 避免抖动", font=font(14, bold=True), fill=AMBER_L)
    d.text((80, 476), "★ KEDA(Kubernetes Event Driven Autoscaling)从 Prometheus 拉指标", font=font(13), fill=SUB)
    d.text((80, 504), "★ HPA 兜底:CPU 70% 也扩(自定义指标失效时)", font=font(13), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "04_scaling.png"))
    print("[OK] 04_scaling")


# ============ 05 灰度发布 ============
def img_05():
    img, d = base()
    d.text((60, 40), "3 种灰度策略 · 按改动大小选", font=font(26, bold=True), fill=CYAN_L)
    d.text((60, 78), "Canary 主推 · Blue-Green 重构 · Feature Flag Prompt 灰度", font=font(15), fill=LIGHT)

    strategies = [
        ("A", "Canary 金丝雀",    "权重逐步放量 · 5% → 25% → 50% → 100%", "日常改动 · 推荐",   GREEN_L),
        ("B", "Blue-Green 蓝绿", "两套环境 · Service selector 切换",      "重构 / 改架构",     BLUE_L),
        ("C", "Feature Flag",    "改配置不发版 · 按用户分群",              "Prompt 灰度首选",   AMBER_L),
    ]
    y0 = 116
    for i, (n, name, mechanism, scene, c) in enumerate(strategies):
        y = y0 + i * 80
        rrect(d, [60, y, 1020, y + 68], 12, fill=BOX, outline=c, width=2)
        rrect(d, [78, y + 14, 138, y + 54], 10, fill=c)
        d.text((100, y + 24), n, font=font(20, bold=True), fill=BG)
        d.text((158, y + 12), name, font=font(18, bold=True), fill=c)
        d.text((158, y + 38), mechanism, font=font(13), fill=WHITE)
        # 场景 chip
        bw = tw(d, scene, font(12, bold=True)) + 16
        rrect(d, [1020 - bw - 14, y + 24, 1020 - 14, y + 50], 6, fill=DEEP, outline=c, width=1)
        d.text((1020 - bw - 8, y + 28), scene, font=font(12, bold=True), fill=c)

    # 灰度命令示例
    rrect(d, [60, 380, 1020, 540], 12, fill=DEEP, outline=GREEN, width=2)
    d.text((80, 396), "Canary 操作 · 5 步放量", font=font(15, bold=True), fill=GREEN_L)
    # ASCII 命令用 mono · 含中文用 msyh
    cmds = [
        ("kubectl annotate ingress agent-api-canary \\", True),
        ('    nginx.ingress.kubernetes.io/canary-weight="5" --overwrite', True),
        ("", True),
        ("# 观察 10 分钟 + 跑 smoke eval(#11)· 通过 → 升 25%", False),
        ("# 任一档失败 · 权重回 0 · 完成回滚", False),
    ]
    for i, (line, is_mono) in enumerate(cmds):
        d.text((80, 422 + i * 22), line, font=(mono(13) if is_mono else font(13)), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "05_canary.png"))
    print("[OK] 05_canary")


# ============ 06 3 层版本管理 ============
def img_06():
    img, d = base()
    d.text((60, 40), "AI Agent 特有 · 3 层版本管理", font=font(26, bold=True), fill=CYAN_L)
    d.text((60, 78), "传统 Web 只有代码版本 · AI Agent 有 3 层 · 独立可观察 + 独立回滚", font=font(15), fill=LIGHT)

    # (layer, tool, tool_is_mono, freq, rollback, how, color)
    layers = [
        ("代码",   "Git tag + K8s rollout",      True,  "周",   "1 分钟",   "rolling update",      BLUE_L),
        ("Prompt", "Langfuse 版本管理(#11)",    False, "日",   "10 秒",    "改 UI 不用 deploy",   GREEN_L),
        ("模型",   "LiteLLM 配置 + 钉死小版本",  False, "月",   "1 分钟",   "改 yaml 即生效",      AMBER_L),
    ]

    y0 = 124
    rrect(d, [60, y0, 1020, y0 + 32], 8, fill=BOX)
    headers = ["层", "工具", "改的频率", "回滚速度", "怎么改"]
    col_x = [60, 200, 440, 600, 760]
    for i, h in enumerate(headers):
        d.text((col_x[i] + 12, y0 + 8), h, font=font(13, bold=True), fill=CYAN_L)

    for i, (layer, tool, tool_mono, freq, rollback, how, c) in enumerate(layers):
        y = y0 + 38 + i * 56
        rrect(d, [60, y, 1020, y + 48], 8, fill=DEEP, outline=c, width=2)
        rrect(d, [76, y + 12, 188, y + 38], 6, fill=c)
        d.text((100, y + 16), layer, font=font(15, bold=True), fill=BG)
        d.text((col_x[1] + 12, y + 16), tool, font=(mono(13) if tool_mono else font(13)), fill=WHITE)
        d.text((col_x[2] + 12, y + 16), freq, font=font(13), fill=SUB)
        d.text((col_x[3] + 12, y + 16), rollback, font=font(13, bold=True), fill=c)
        d.text((col_x[4] + 12, y + 16), how, font=font(12), fill=LIGHT)

    rrect(d, [60, 380, 1020, 540], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 396), "★ 钉死模型小版本(防自动漂移)", font=font(15, bold=True), fill=AMBER_L)
    # 含中文的用 msyh
    examples = [
        ("[NO] LLM_MODEL=claude-sonnet-4-5", True),
        ("    供应商可能换底层 · 不要这样写", False),
        ("[OK] LLM_MODEL=claude-sonnet-4-5-20250220", True),
        ("    钉死小版本号 · 防自动漂移", False),
        ("", True),
        ("★ 3 层 ConfigMap 单独标记 · Prometheus 各自打 label · 出事知道改了哪层", False),
    ]
    for i, (line, is_mono) in enumerate(examples):
        color = AMBER_L if line.strip().startswith("★") else SUB
        f = mono(13) if is_mono else font(13)
        d.text((80, 422 + i * 18), line, font=f, fill=color)

    watermark(d)
    img.save(os.path.join(OUT, "06_versions.png"))
    print("[OK] 06_versions")


# ============ 07 回滚策略 ============
def img_07():
    img, d = base()
    d.text((60, 40), "回滚策略 · 3 层独立 + 自动触发", font=font(26, bold=True), fill=CYAN_L)
    d.text((60, 78), "代码 / Prompt / 模型 · 谁错了回谁 · 不要全部重新 deploy", font=font(15), fill=LIGHT)

    # (name, speed, cmd, is_pure_ascii_cmd, color)
    rollbacks = [
        ("代码回滚",   "K8s 自带 · 1 分钟",           "kubectl rollout undo deployment/agent-api",   True,  BLUE_L),
        ("Prompt 回滚","Langfuse UI · 10 秒(不发版)", "langfuse.get_prompt() 自动拉最新 · 不用 deploy", False, GREEN_L),
        ("模型回滚",   "LiteLLM 配置 · 1 分钟",       "改 litellm-config.yaml 的 model 字段",          False, AMBER_L),
    ]
    y0 = 116
    for i, (name, speed, cmd, is_mono, c) in enumerate(rollbacks):
        y = y0 + i * 90
        rrect(d, [60, y, 1020, y + 78], 12, fill=BOX, outline=c, width=2)
        rrect(d, [78, y + 14, 280, y + 64], 8, fill=c)
        d.text((96, y + 26), name, font=font(20, bold=True), fill=BG)
        d.text((300, y + 12), "速度:" + speed, font=font(14, bold=True), fill=WHITE)
        # 纯 ASCII 命令用 mono · 含中文的用 msyh
        d.text((300, y + 42), cmd, font=(mono(12) if is_mono else font(12)), fill=SUB)

    # 自动 rollback 流程
    rrect(d, [60, 400, 1020, 540], 12, fill=DEEP, outline=RED, width=2)
    d.text((80, 416), "★ 自动 rollback · 部署后 5 分钟 smoke eval 自动跑", font=font(15, bold=True), fill=RED_L)
    # 含中文 → 用 msyh
    flow = [
        "1. kubectl set image     → 部署 v2",
        "2. sleep 300             → 等流量铺开",
        "3. run smoke eval        → 跑黄金集 30 条",
        "4. on failure            → kubectl rollout undo · 自动回 v1",
        "5. alert slack           → 通知人审",
    ]
    for i, line in enumerate(flow):
        d.text((80, 444 + i * 18), line, font=font(13), fill=SUB)

    watermark(d)
    img.save(os.path.join(OUT, "07_rollback.png"))
    print("[OK] 07_rollback")


# ============ 08 可观测性三件套 ============
def img_08():
    img, d = base()
    d.text((60, 40), "可观测性三件套 · Metrics / Logs / Traces", font=font(26, bold=True), fill=CYAN_L)
    d.text((60, 78), "缺一不可 · 出事故第一时间能定位", font=font(15), fill=LIGHT)

    pillars = [
        ("Metrics", "Prometheus + Grafana",
         "RPS · token QPS · 成本 · 错误率 · p95 / p99 延迟",
         "看趋势 + 触发告警",            BLUE_L),
        ("Logs",    "Loki / ELK",
         "错误堆栈 · 用户对话(必脱敏)· 关键事件",
         "看细节 + 复盘根因",            GREEN_L),
        ("Traces",  "Langfuse / Phoenix(#11)",
         "单次对话全链路 · LLM / Tool / Subagent 调用",
         "看单次执行 + 调试",            AMBER_L),
    ]
    y0 = 116
    for i, (name, tool, what, why, c) in enumerate(pillars):
        y = y0 + i * 102
        rrect(d, [60, y, 1020, y + 90], 14, fill=BOX, outline=c, width=2)
        rrect(d, [78, y + 14, 220, y + 76], 10, fill=c)
        d.text((100, y + 36), name, font=font(20, bold=True), fill=BG)
        d.text((240, y + 12), "工具:" + tool, font=mono(13), fill=WHITE)
        d.text((240, y + 38), "看什么:" + what, font=font(13), fill=SUB)
        d.text((240, y + 62), "用途:" + why, font=font(13, bold=True), fill=c)

    rrect(d, [60, 432, 1020, 540], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 448), "★ Grafana 必看 8 个面板", font=font(15, bold=True), fill=AMBER_L)
    panels = [
        "1. RPS / 2. token QPS / 3. 成本¥/h / 4. p95-p99 延迟",
        "5. 错误率 / 6. endpoint 健康 / 7. 每用户成本 top10 / 8. Eval 滚动得分",
    ]
    for i, line in enumerate(panels):
        d.text((80, 476 + i * 22), line, font=font(13), fill=SUB)
    d.text((80, 520), "★ 日志必脱敏(参考 #10)· mapping 永不持久化", font=font(13, bold=True), fill=RED_L)

    watermark(d)
    img.save(os.path.join(OUT, "08_observability.png"))
    print("[OK] 08_observability")


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
