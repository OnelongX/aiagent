# -*- coding: utf-8 -*-
"""5 images for AI 防泄密 + 脱敏完整指南 · AI 工具栈 #10"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 600

# 安全主题 · 深蓝 + 警示橙红
BG       = "#0a1118"
BOX      = "#15202e"
DEEP     = "#050a10"
LINE     = "#26384e"
WHITE    = "#ffffff"
SUB      = "#cfd9eb"
LIGHT    = "#94a3c4"
DIM      = "#5b6a87"
AMBER    = "#fbbf24"
AMBER_L  = "#fde047"
AMBER_D  = "#f59e0b"
RED      = "#ef4444"
RED_L    = "#fca5a5"
ROSE     = "#fb7185"
ORANGE   = "#fb923c"
ORANGE_L = "#fdba74"
GREEN    = "#10b981"
GREEN_L  = "#34d399"
EMERALD  = "#6ee7b7"
BLUE     = "#3b82f6"
BLUE_L   = "#60a5fa"
CYAN     = "#22d3ee"
CYAN_L   = "#67e8f9"
PURPLE   = "#a855f7"
PURPLE_L = "#c084fc"
PINK     = "#ec4899"
PINK_L   = "#f9a8d4"
INDIGO_L = "#a5b4fc"

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
    rrect(d, [60, 50, 240, 88], 19, fill=AMBER)
    d.text((78, 56), "实战复盘", font=font(20, bold=True), fill=BG)
    rrect(d, [256, 50, 480, 88], 19, fill=BOX)
    d.text((274, 56), "AI 工具栈 #10", font=font(17, bold=True), fill=AMBER_L)

    d.text((60, 128), "AI 防泄密 + 脱敏指南", font=font(40, bold=True), fill=AMBER_L)
    d.text((60, 188), "4 层防御 + 统一 PII Toolkit", font=font(22, bold=True), fill=WHITE)
    d.text((60, 226), "5 通道泄密 / 5 行业插件 / 私有 LLM 路由", font=font(18), fill=SUB)

    chips = [
        ("5 通道",         RED_L,    "训练 / 上传 / 库 / 注入 / 反向"),
        ("4 层防御",       AMBER_L,  "数据 + 协议 + 模型 + 运维"),
        ("统一 Toolkit",   GREEN_L,  "5 行业插件 · 复制可用"),
    ]
    y = 290
    for i, (kw, c, desc) in enumerate(chips):
        x = 60 + i * 330
        rrect(d, [x, y, x + 310, y + 92], 14, fill=BOX, outline=c, width=2)
        d.text((x + 20, y + 14), kw, font=font(22, bold=True), fill=c)
        d.text((x + 20, y + 52), desc, font=font(13), fill=SUB)

    rrect(d, [60, 426, 1020, 514], 14, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 444), "大模型不是被攻破的 · 是被你用错的", font=font(20, bold=True), fill=AMBER_L)
    d.text((80, 478), "脱敏只是第 1 层 · 4 层防御任一缺失 = 整套失效", font=font(15), fill=LIGHT)
    watermark(d)
    img.save(os.path.join(OUT, "01_hero.png"))
    print("[OK] 01_hero")


# ============ 02 5 个泄密通道 ============
def img_02():
    img, d = base()
    d.text((60, 40), "AI 泄密的 5 个真实通道", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "光做脱敏只能堵住 1.5 个 · 其他 3 个要单独防", font=font(15), fill=LIGHT)

    channels = [
        ("①", "训练样本污染",   "公有云 fine-tune → 数据进训练集",       "三星员工泄漏代码事件 2023", RED),
        ("②", "Prompt 上传",    "API 调用 → endpoint 日志留存 30 天",     "脱敏才能堵住",              ORANGE),
        ("③", "向量库 / RAG",   "chunk 没做 ACL → 跨部门拿数据",          "metadata filter 强制",      PINK),
        ("④", "Prompt Injection", "诱导 LLM 吐出系统提示词 / 上下文",       "20 个攻击模式",             PURPLE),
        ("⑤", "反向输出 leak",   "LLM 自己编出 PII 拼回输出",              "最阴险 · 90% 没防",         CYAN),
    ]
    y0 = 116
    for i, (n, name, desc, threat, c) in enumerate(channels):
        y = y0 + i * 76
        rrect(d, [60, y, 1020, y + 66], 12, fill=BOX, outline=c, width=2)
        rrect(d, [78, y + 14, 280, y + 56], 8, fill=c)
        d.text((96, y + 22), n, font=font(20, bold=True), fill=BG)
        d.text((124, y + 22), name, font=font(17, bold=True), fill=BG)
        d.text((304, y + 12), desc, font=font(14, bold=True), fill=WHITE)
        d.text((304, y + 38), "★ " + threat, font=font(12), fill=c)

    watermark(d)
    img.save(os.path.join(OUT, "02_channels.png"))
    print("[OK] 02_channels")


# ============ 03 4 层防御 ============
def img_03():
    img, d = base()
    d.text((60, 40), "4 层防御体系 · 必须同时上", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "单一层无法防全部 5 个通道 · 任一缺失 = 整套失效", font=font(15), fill=LIGHT)

    layers = [
        ("第 4 层", "运维 / 合规层",       "审计 · 数据流追溯 · 等保 · GDPR · PIPL",   PURPLE),
        ("第 3 层", "模型 / 部署层",       "私有 LLM · vLLM + Qwen · LiteLLM 路由",   BLUE),
        ("第 2 层", "协议 / 工具层",       "Hooks · Guardrails · 输入/输出审查",       AMBER),
        ("第 1 层", "数据层(脱敏)",      "PII 正则 + NER + 分级 · 双重脱敏",        GREEN),
    ]
    y0 = 120
    for i, (level, name, desc, c) in enumerate(layers):
        y = y0 + i * 86
        rrect(d, [60, y, 1020, y + 74], 14, fill=BOX, outline=c, width=2)
        # 层数 tag
        rrect(d, [80, y + 14, 220, y + 60], 10, fill=c)
        d.text((100, y + 24), level, font=font(20, bold=True), fill=BG)
        # 名称 + 描述
        d.text((250, y + 14), name, font=font(20, bold=True), fill=c)
        d.text((250, y + 46), desc, font=font(14), fill=SUB)

    rrect(d, [60, 480, 1020, 540], 10, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 498), "★ 关键认知:5 通道 × 4 层 = 矩阵防御", font=font(14, bold=True), fill=AMBER_L)
    d.text((80, 520), "训练污染靠第 3-4 层 · Prompt 上传靠第 1 层 · Injection 靠第 2 层", font=font(12), fill=LIGHT)

    watermark(d)
    img.save(os.path.join(OUT, "03_defense.png"))
    print("[OK] 03_defense")


# ============ 04 Prompt Injection 防御 ============
def img_04():
    img, d = base()
    d.text((60, 40), "Prompt Injection 攻击与防御", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "输入层 + 输出层双重检测 · 20 个攻击模式", font=font(15), fill=LIGHT)

    # 左:攻击模式
    rrect(d, [60, 116, 540, 480], 14, fill=BOX, outline=RED, width=2)
    d.text((78, 132), "[攻击] 常见 Injection 模式", font=font(17, bold=True), fill=RED_L)
    attacks = [
        "1. 直接破坏指令",
        "   忽略之前 / ignore previous",
        "   忘记所有 / forget everything",
        "",
        "2. 角色越权(Jailbreak)",
        "   扮演 DAN / pretend you are",
        "   developer mode / jailbreak",
        "",
        "3. 系统提示词探测",
        "   你的 system prompt",
        "   你的真实指令 / 初始设定",
        "",
        "4. 标签注入",
        "   </system> 闭合主指令",
        "   ###SYSTEM### 伪造段落",
        "",
        "5. 编码绕过",
        "   base64 / \\x / \\u00 等",
    ]
    for i, line in enumerate(attacks):
        d.text((78, 162 + i * 18), line, font=font(13), fill=SUB)

    # 右:防御代码
    rrect(d, [560, 116, 1020, 480], 14, fill=BOX, outline=GREEN, width=2)
    d.text((578, 132), "[防御] 输入层 + 输出层", font=font(17, bold=True), fill=GREEN_L)
    code = [
        "def hardened_call(user_input):",
        "    # 1. 输入检测 injection",
        "    is_inj, hits = detect_",
        "        prompt_injection(input)",
        "    if is_inj:",
        "        return SAFE_RESPONSE",
        "",
        "    # 2. PII 脱敏后调 LLM",
        "    redacted = redact(input)[0]",
        "    output = llm(redacted)",
        "",
        "    # 3. 输出检测 system leak",
        "    if detect_system_leak(output):",
        "        return SAFE_RESPONSE",
        "",
        "    # 4. 输出检测 reverse leak",
        "    if detect_reverse_leak(output):",
        "        output = redact(output)[0]",
        "    return output",
    ]
    for i, line in enumerate(code):
        d.text((578, 162 + i * 16), line, font=mono(12), fill=SUB)

    rrect(d, [60, 500, 1020, 540], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 513), "★ 核心:Injection 不是 LLM 蠢 · 是你没在协议层堵住", font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "04_injection.png"))
    print("[OK] 04_injection")


# ============ 05 私有 LLM 路由 ============
def img_05():
    img, d = base()
    d.text((60, 40), "涉密走私有 LLM · 通用走公有云", font=font(26, bold=True), fill=AMBER_L)
    d.text((60, 78), "LiteLLM 一行配置 · C3 字段命中自动切换", font=font(15), fill=LIGHT)

    # 流程图:user → redact → c3? → public / private
    boxes = [
        ("用户输入",     90,  150, BLUE_L),
        ("PII 脱敏",     280, 150, AMBER),
        ("C3 sensitive?",470, 150, ORANGE),
    ]
    for name, x, y, c in boxes:
        rrect(d, [x, y, x + 160, y + 80], 10, fill=BOX, outline=c, width=2)
        d.text((x + 16, y + 30), name, font=font(15, bold=True), fill=c)

    # 分叉箭头
    d.line([(630, 190), (700, 130)], fill=LINE, width=3)   # 上:公有
    d.line([(630, 190), (700, 250)], fill=LINE, width=3)   # 下:私有

    # 公有云 LLM
    rrect(d, [700, 90, 1020, 170], 10, fill=BOX, outline=GREEN_L, width=2)
    d.text((720, 102), "[NO] 公有云 LLM", font=font(15, bold=True), fill=GREEN_L)
    d.text((720, 130), "Claude / GPT / Gemini", font=mono(13), fill=SUB)
    d.text((720, 148), "通用问答 / 营销文案", font=font(12), fill=DIM)

    # 私有 LLM
    rrect(d, [700, 220, 1020, 320], 10, fill=BOX, outline=RED, width=2)
    d.text((720, 232), "[YES] 私有 LLM(内网)", font=font(15, bold=True), fill=RED_L)
    d.text((720, 260), "vLLM + Qwen3-14B", font=mono(13), fill=SUB)
    d.text((720, 278), "病历 / 配方 / 征信", font=font(12), fill=AMBER_L)
    d.text((720, 298), "数据不出机房", font=font(12, bold=True), fill=RED_L)

    # C3 字段表
    rrect(d, [60, 360, 1020, 470], 12, fill=DEEP, outline=AMBER, width=2)
    d.text((80, 376), "C3 级敏感字段(任一命中 → 走私有 LLM)", font=font(15, bold=True), fill=AMBER_L)
    c3_fields = [
        ("通用",   "ID_CARD · BANK_CARD",                    GREEN_L),
        ("法律",   "CASE_NO · LAWYER_NO",                    PURPLE_L),
        ("教育",   "STUDENT_ID",                             CYAN_L),
        ("医疗",   "INPATIENT_NO · MEDICAL_NO · INSURANCE_NO", PINK_L),
        ("金融",   "CVV · ACCOUNT_NO · CUSTOMER_NO",         AMBER_L),
        ("制造",   "RECIPE · PATENT · SN · BATCH",            ORANGE_L),
    ]
    for i, (ind, fields, c) in enumerate(c3_fields):
        x = 80 + (i % 3) * 320
        y = 408 + (i // 3) * 28
        d.text((x, y), ind, font=font(13, bold=True), fill=c)
        d.text((x + 50, y), fields, font=mono(12), fill=SUB)

    rrect(d, [60, 490, 1020, 540], 8, fill=DEEP, outline=AMBER, width=1)
    d.text((80, 506), "★ Docker 1 行起 vLLM + Qwen3-14B · 1×A100 80G · 30 tok/s",
           font=font(13, bold=True), fill=AMBER_L)

    watermark(d)
    img.save(os.path.join(OUT, "05_private_llm.png"))
    print("[OK] 05_private_llm")


if __name__ == "__main__":
    img_01()
    img_02()
    img_03()
    img_04()
    img_05()
    print("\n[DONE] 5 images saved to", OUT)
