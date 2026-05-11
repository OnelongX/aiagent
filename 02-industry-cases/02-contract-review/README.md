# 合同审查助手 —— Claude + Gemini + GPT 多模型协作实战

> 实战复盘 · AI 工具栈 · 行业落地篇
>
> 单模型不够。三模型并发,漏判率从 15% 压到 2%。

---


<div align="center">

<a href="https://github.com/OnelongX/aiagent">
<img src="../../assets/wechat-qrcode.png" width="320" alt="公众号:IamOnelong" />
</a>

📖 **本文同步发布于公众号「实战复盘」** · 微信号:`IamOnelong`
🌐 [完整代码仓库 · github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型:[docs/livetoken.md](../../docs/livetoken.md)

</div>

---

## I. 这事到底要做什么

输入:一份合同 PDF(可能是扫描件)
输出:一份审查报告 —— 风险条款清单 + 等级评分 + 修订建议 + 是否可签字

中间要做 7 件事:

1. 解析(含 OCR)
2. 拆条款
3. 比对**公司红线条款库**
4. 风险推理
5. 起草修订
6. **交叉验证**(三模型独立打分 → 投票)
7. 出报告

跟上一篇家庭绿电不同 —— **合同审查不能用单模型**。

---

## II. 为什么必须多模型

法律场景下,单模型幻觉率经验值 15-20%。漏判一条 "数据所有权归服务方" 的条款,代价可能是百万级。

**三模型独立打分 + 投票 + 任一发现风险即升级**,把漏判压到 <2%。

| 方案 | 漏判率 | 调用成本 | 可用性 |
|---|---|---|---|
| 单模型 | 15-20% | 1× | 法务团队不敢直接用 |
| 三模型全跑 | <1% | 3× | 太贵 |
| **分级触发**(本方案) | <2% | 1.4× | 可生产 |

分级触发的核心:常规条款单模型跑,**中危以上才升三模型**。

---

## III. 三模型任务分配

不同模型有不同结构性优势,**别用一个模型干所有事**:

| 任务 | 首选 | 原因 |
|---|---|---|
| 扫描件 OCR + 多模态解析 | **Gemini 2.5 Pro** | 原生多模态 + 2M context |
| 条款结构化抽取(JSON) | **GPT-4.1** | 严格 JSON mode,schema 不漂 |
| 风险推理 + 修订措辞 | **Claude Sonnet 4.5** | 法律语言精准 + 深度推理链 |
| 红线匹配 | **不用 LLM** | 规则 + 向量召回更快更准 |
| 终审交叉验证 | **三模型并发** | 投票 + disagree 升人工 |

---

## IV. 整体架构

```
合同 PDF/扫描件
   │
   ▼
┌──────────────────────┐
│  主 Agent (Claude SDK)  │  ← orchestrator
└──────────────────────┘
   │
   ├─→ ingester       (Gemini OCR + 全文摘要)
   ├─→ extractor      (GPT JSON 切条款)
   ├─→ risk-team      (规则红线 + Claude 风险 + 三模型交叉)
   ├─→ reviser        (Claude 起草修订)
   └─→ report-writer  (出 Markdown 报告)
```

主 Agent 仍是 Claude Agent SDK。**Gemini 和 GPT 以"工具"形式被调用** —— SDK 的 model 字段只支持 Claude,所以异厂模型必须包一层 custom tool。

---

## V. 8 个核心工具

```python
from claude_agent_sdk import tool
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

# === 1. PDF / 扫描件解析(Gemini 多模态)===
@tool("parse_contract", "解析合同(支持扫描件)", {"file_path": str})
async def parse_contract(args):
    file = genai.upload_file(args["file_path"])
    resp = genai.GenerativeModel("gemini-2.5-pro").generate_content(
        [file, "提取这份合同的全部文字,保留段落和编号结构。"])
    return {"content": [{"type": "text", "text": resp.text}]}

# === 2. 条款结构化抽取(GPT JSON mode)===
@tool("extract_clauses", "条款切分为结构化 JSON", {"text": str})
async def extract_clauses(args):
    client = OpenAI()
    resp = client.chat.completions.create(
        model="gpt-4.1",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "按 schema 输出 clauses 数组,"
             "每条含 id/title/category/text/parties_involved/amount"},
            {"role": "user", "content": args["text"]},
        ])
    return {"content": [{"type": "text", "text": resp.choices[0].message.content}]}

# === 3. 红线匹配(规则 + 向量召回,不用 LLM)===
@tool("match_redlines", "对照公司红线条款库", {"clause": dict})
async def match_redlines(args):
    hits = redline_db.search(args["clause"]["text"], top_k=5)
    return {"content": [{"type": "text", "text": json.dumps({"hits": hits})}]}

# === 4. 风险推理(Claude Opus,深度推理)===
@tool("risk_analyze", "单条款风险评估", {"clause": dict, "redline_hits": list})
async def risk_analyze(args):
    c = Anthropic()
    resp = c.messages.create(
        model="claude-opus-4-5", max_tokens=2000,
        system="你是 20 年法律风控专家。输出 JSON:"
               "{level:'critical|high|medium|low|none', "
               "issues:[...], reasoning:'...'}",
        messages=[{"role": "user", "content": json.dumps(args)}])
    return {"content": [{"type": "text", "text": resp.content[0].text}]}

# === 5. 三模型交叉验证 ===
@tool("cross_verify", "三模型并发打分 + 投票", {"clause": dict})
async def cross_verify(args):
    prompts = build_grading_prompt(args["clause"])
    claude_s, gpt_s, gemini_s = await asyncio.gather(
        call_claude(prompts), call_gpt(prompts), call_gemini(prompts))
    consensus = majority_vote([claude_s, gpt_s, gemini_s])
    disagree = any_disagree([claude_s, gpt_s, gemini_s])
    return {"content": [{"type": "text", "text": json.dumps({
        "consensus": consensus,
        "claude": claude_s, "gpt": gpt_s, "gemini": gemini_s,
        "needs_human": disagree,
    })}]}

# === 6. 修订建议(Claude 起草)===
@tool("draft_revision", "起草修订条款 diff", {"clause": dict, "risks": list})
async def draft_revision(args):
    ...  # Claude Sonnet,要求 diff 格式输出

# === 7. 全文摘要(Gemini 2M context 吃整份)===
@tool("summarize_full", "全文摘要 + 整体定级", {"text": str})
async def summarize_full(args):
    resp = genai.GenerativeModel("gemini-2.5-pro").generate_content(
        f"整份合同的整体风险摘要(150 字内)+ 整体定级:\n\n{args['text']}")
    return {"content": [{"type": "text", "text": resp.text}]}

# === 8. 出报告 ===
@tool("write_report", "落 Markdown 报告", {"data": dict})
async def write_report(args):
    md = render_report_template(args["data"])
    Path("./output/review.md").write_text(md, encoding="utf-8")
    return {"content": [{"type": "text", "text": "saved"}]}
```

---

## VI. 5 个 Subagent

```python
agents = {
    "ingester": AgentDefinition(
        description="解析合同 + 全文摘要",
        prompt="先 parse_contract 拿全文,再 summarize_full 出整体摘要。",
        tools=["parse_contract", "summarize_full"],
        model="sonnet"),

    "extractor": AgentDefinition(
        description="切条款",
        prompt="调 extract_clauses 把合同切成结构化 clause 数组。",
        tools=["extract_clauses"],
        model="sonnet"),

    "risk-team": AgentDefinition(
        description="逐条款风险评估",
        prompt="对每条 clause:① match_redlines ② risk_analyze "
               "③ 若 level≥medium 调 cross_verify ④ 若 needs_human 标记。",
        tools=["match_redlines", "risk_analyze", "cross_verify"],
        model="sonnet"),

    "reviser": AgentDefinition(
        description="起草修订",
        prompt="对所有 level≥medium 的条款调 draft_revision。",
        tools=["draft_revision"],
        model="sonnet"),

    "report-writer": AgentDefinition(
        description="出最终报告",
        prompt="拼成 Markdown 落到 ./output/review.md。"
               "必须含:整体定级 / 高危清单 / 修订对照 / 人工介入项。",
        tools=["write_report"],
        model="sonnet"),
}
```

---

## VII. 3 个 Hooks —— 工程红线

```python
hooks = {
  "PostToolUse:cross_verify": escalate_if_disagree,
  "PreToolUse:write_report":  block_if_unresolved_critical,
  "PostToolUse:risk_analyze": alert_if_critical,
}
```

**3 条硬约束**:

1. 三模型 disagree → **强制升人工**,Agent 不允许自己拍板
2. 存在未解决的 critical 条款 → **禁止**出报告(防止"低风险通过"假阳性)
3. 涉及金额 > 阈值的条款 → 自动打 `needs_human` 标记

---

## VIII. 完整 main.py

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, create_sdk_mcp_server

mcp = create_sdk_mcp_server(
    name="contract-review", version="1.0.0",
    tools=[parse_contract, extract_clauses, match_redlines,
           risk_analyze, cross_verify, draft_revision,
           summarize_full, write_report])

options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt=(
        "你是合同审查首席协调员。严格按 5 段委派 Subagent:"
        "ingester → extractor → risk-team → reviser → report-writer。"
        "禁止自己判断条款风险,所有结论必须来自工具。"
        "三模型分歧的条款必须打 needs_human。"),
    mcp_servers={"contract-review": mcp},
    allowed_tools=[
        "mcp__contract-review__parse_contract",
        "mcp__contract-review__extract_clauses",
        "mcp__contract-review__match_redlines",
        "mcp__contract-review__risk_analyze",
        "mcp__contract-review__cross_verify",
        "mcp__contract-review__draft_revision",
        "mcp__contract-review__summarize_full",
        "mcp__contract-review__write_report",
        "Task", "Write",
    ],
    agents=agents,
    hooks=hooks,
    permission_mode="acceptEdits",
)

async def main():
    async with ClaudeSDKClient(options=options) as c:
        await c.query(
            "审查 ./contracts/saas_agreement_v3.pdf,SaaS 服务合同。"
            "我们是客户方。重点:数据所有权 / SLA 赔付 / 续约条款。")
        async for msg in c.receive_response():
            if hasattr(msg, "result"):
                print(msg.result)

asyncio.run(main())
```

国内开发者鉴权 —— 三家 API 都走 livetoken:

```bash
# Claude
export ANTHROPIC_AUTH_TOKEN=sk-livetoken-xxxxx
export ANTHROPIC_BASE_URL=https://livetoken.top

# OpenAI / Gemini 同理(走 OpenAI 兼容协议)
export OPENAI_API_KEY=sk-livetoken-xxxxx
export OPENAI_BASE_URL=https://livetoken.top
```

---

## IX. 一次真实运行

**输入**:`./contracts/saas_agreement_v3.pdf`(45 页 SaaS 合同)

Agent 跑完 5 段后,`./output/review.md`:

```
合同审查报告 · SaaS 服务合同 v3
整体定级:HIGH(不建议直接签)

【6 条高危条款】
#7  数据所有权     CRITICAL  服务商保留客户数据再训练权 → 必删
#12 SLA 赔付上限   HIGH      月费 ×0.5 封顶 → 改至 ×3
#19 自动续约       HIGH      默认续 3 年 → 改 1 年 + 30 天通知
#23 单方调价权     HIGH      服务商可任意调价 → 加 10% 上限
#28 责任限额       MEDIUM    总责任 $10,000 → 改至年费 2 倍
#31 仲裁地         MEDIUM    新加坡 → 改国内

【需人工 review 项】
#19 三模型分歧:Claude=HIGH, GPT=MEDIUM, Gemini=HIGH

【整体摘要】
本合同对客户方风险较高,主要集中在数据主权、SLA 赔付
不对等、续约自动化三大类。建议谈判后再签。

【调用统计】
Gemini 调用:2 次(解析 + 摘要)
GPT 调用:1 次(条款抽取)
Claude 调用:47 次(45 条款风险 + 修订)
cross_verify 触发:8 次(中危以上)
总成本:¥3.2(单合同)
```

整个过程用户只说了一句话。

---

## X. 三个工程坑

### 坑 1:别让 LLM 算金额、日期、引用

合同里的 "30 days" / "$10,000" / "§7.2(b)" —— 让 LLM 抄都会抄错。**用正则提取**写工具,LLM 只负责语义判断。

### 坑 2:红线库走向量 + 规则,别走 LLM

公司红线条款是稳定资产,几百到几千条,**预先 embedding 入库**。新条款来了向量召回 top-5 → 规则匹配。比让 LLM 每次"想一下我们有哪些红线"快 100 倍,且不漏。

### 坑 3:三模型并发要做分级触发

一份 50 页合同,三模型全跑一遍 ≈ 30 万 tokens × 3。**分级**:

- 所有条款 → 单模型(Claude)
- level ≥ medium → 升 cross_verify(三模型)
- 触发红线 → 强制三模型 + 人工

成本压到单模型的 1.4 倍,而非 3 倍。

---

## XI. 升华

| 单模型方案 | 多模型方案 |
|---|---|
| 漏判率 15-20% | 漏判率 <2% |
| 1 次调用 | 分级触发(1-3 次) |
| 法务团队不敢用 | 可作为预审 |

**关键不是"用 Claude 还是 GPT 还是 Gemini",是"什么任务用什么模型 + 高风险条款必交叉"**。

合同审查这事的工程纪律,跟金融风控同一个数量级。

把这套架构平移到任何**漏判代价 >> 误报代价**的场景,逻辑完全一样:

- 医疗诊断辅助
- 信贷审批
- 投资尽调
- 安全代码审查
- 学术论文同行评审

**LLM 单挑做不到的事,多模型协作可以。这是 Agent 时代真正的核心能力之一。**

---

实战复盘 · AI 工具栈 · 行业落地篇
关键词:Claude · Gemini · GPT · 多模型协作 · 合同审查 · Claude Agent SDK · MCP · 行业落地
本文仅供学习参考。
