# 企业级知识库 + 客服系统 —— Claude Agent SDK 边界实战

> 实战复盘 · AI 工具栈 · 行业落地篇
>
> 知识库 Q&A 的关键词是"准确"。
> 客服系统的关键词是"边界"。

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

## I. 跟上篇知识库 Q&A 的 5 个根本差异

接续上一篇企业知识库 Q&A。**那是内部员工提问,这是外部客户对话** —— 看着像同一个东西,工程上是两套系统。

| 维度 | 知识库 Q&A | 客服系统 |
|---|---|---|
| 用户 | 内部员工(可信) | 外部客户(不可信 + 情绪化) |
| 任务 | 只答疑 | **答疑 + 动作执行**(查单/退款/开票) |
| 渠道 | 单一(内网) | 多渠道(网页/小程序/微信/邮件) |
| 失败兜底 | "我不知道" | **必须转人工** |
| 评测指标 | RAGAS | **CSAT + AHT + Containment Rate** |

**核心区别**:客服不只是"找答案",还要**执行业务动作**。这条引出整套架构差异。

---

## II. 整体架构(四层)

```
渠道层  Web / 小程序 / 微信 / 邮件 / 飞书
        统一接入 → unified message format
    ↓
状态层  Redis (session memory)
        Postgres (对话历史 + 用户档案)
    ↓
Agent  主 Agent (Claude Sonnet 4.5)
        ├ triager     (Haiku · 意图 + 情绪)
        ├ info-agent  (Sonnet · KB 答疑)
        ├ action-agent(Sonnet · 订单 / 退款 / 开票)
        └ escalator   (Haiku · 转人工)
    ↓
工具层  KB / CRM / OMS / 工单 / Slack / 财务
```

**KB 层完全复用上一篇** —— Qdrant + Cohere Rerank + 引用。客服把它当一个工具调用。

---

## III. 工具层 —— 4 类 12 个

工具按"可逆性"分两大类:

### A. 信息工具(读取 · 无副作用)

```python
# 1. KB 检索(复用上一篇)
@tool("kb_search", "知识库检索"): ...

# 2. 订单查询(必须 ACL!只能查自己的)
@tool("get_order", "查订单详情",
      {"order_id": str, "user_id": str})
async def get_order(args):
    order = oms.get(args["order_id"])
    if order.user_id != args["user_id"]:
        return {"error": "permission_denied"}
    return {"content": [{"type": "text", "text": json.dumps(order)}]}

# 3. 物流查询
@tool("track_shipping", "查物流", {"order_id": str}): ...

# 4. 用户画像(VIP/历史/投诉)
@tool("get_profile", "拉用户档案", {"user_id": str}): ...

# 5. 意图 + 情绪分析(用便宜的 Haiku)
@tool("analyze_intent", "意图分类 + 情绪打分",
      {"text": str, "history": list})
async def analyze_intent(args):
    return {"intent": "refund_request",
            "sentiment": -0.7, "urgency": "high"}
```

### B. 动作工具(写入 · 有副作用 · 必须 guard)

```python
# 6. 退款(必须 guard:金额阈值 + 用户身份)
@tool("issue_refund", "发起退款", {...}): ...

# 7. 改地址(仅未发货)
@tool("update_address", "修改收货地址", {...}): ...

# 8. 发优惠券(限制:面额上限 + 每月配额)
@tool("send_coupon", "发优惠券", {...}): ...

# 9. 开发票
@tool("issue_invoice", "开发票", {...}): ...

# 10. 创建工单(转后端处理)
@tool("create_ticket", "创建工单", {...}): ...

# 11. 转人工(关键工具)
@tool("escalate_to_human", "转人工坐席",
      {"reason": str, "context_summary": str, "queue": str}): ...

# 12. 记录 CSAT
@tool("record_csat", "记满意度评分", {...}): ...
```

**客服跟纯 RAG 的核心差异 —— 一半工具是"动作"**。Agent 不只是"找信息",还在"做事"。

---

## IV. Subagent 分工

```python
agents = {
    "triager": AgentDefinition(
        prompt="第一步先 analyze_intent。"
               "意图分流:answerable → info-agent,"
               "actionable → action-agent,"
               "complaint/angry → escalator。",
        tools=["analyze_intent", "get_profile"],
        model="haiku"),    # ← 用便宜的

    "info-agent": AgentDefinition(
        prompt="只答可知问题。先 kb_search,"
               "找不到立即说不知道并建议转人工。",
        tools=["kb_search", "get_order", "track_shipping"],
        model="sonnet"),

    "action-agent": AgentDefinition(
        prompt="执行业务操作前必须 get_profile + get_order 确认身份。"
               "动作前用户必须明确确认(quote 原话)。"
               "禁止自己拍板金额。",
        tools=["get_order", "get_profile", "issue_refund",
               "update_address", "send_coupon", "issue_invoice",
               "create_ticket"],
        model="sonnet"),

    "escalator": AgentDefinition(
        prompt="生成 200 字摘要 → escalate_to_human。"
               "告知用户排队位置 + 预计等待。",
        tools=["escalate_to_human"],
        model="haiku"),
}
```

**关键设计**:triager 用 Haiku(便宜快),只做分流;info/action 用 Sonnet。**单次对话成本可压到 1/5**。

---

## V. State 管理 —— 多轮对话灵魂

```python
session = {
    "user_id": "u_12345",
    "channel": "weixin",
    "messages": [...],
    "current_intent": "refund",
    "current_order_id": "o_67",
    "sentiment_trend": [-0.2, -0.5, -0.7],  # 情绪下滑曲线
    "tools_called": ["get_order", "kb_search"],
    "human_handoff": false,
}
```

每次 Claude 调用,**system prompt 里塞当前 session state 摘要**,不是塞整段历史(token 浪费)。

---

## VI. Hooks —— 5 条工程红线

```python
hooks = {
  # 1. 情绪触底 → 强制转人工
  "PostToolUse:analyze_intent":
      force_escalate if sentiment < -0.6,

  # 2. 退款金额 > ¥500 → 必须人工审批
  "PreToolUse:issue_refund":
      deny_or_ticket if amount > 500,

  # 3. 连续 3 轮 KB miss → 转人工
  "PostToolUse:kb_search":
      escalate if miss_streak >= 3,

  # 4. 用户明确说"找人工" → 立即转
  "PreToolUse:*":
      escalate if "找人工" in last_user_msg,

  # 5. 禁止承诺(措辞监控)
  "PostToolUse:generate_response":
      rewrite if contains_forbidden_promise,
      # 禁词:"保证 X 天内"、"一定退"、"承诺补偿 N 元"
}
```

**第 5 条最容易被忽视**:LLM 会"为了让用户满意"乱许诺。**承诺监控必须自动化**,不能靠 prompt 自觉。

---

## VII. 转人工流程 —— 体验关键

转人工不是甩锅,是**带上下文交接**。

Bad case:用户跟 AI 说了 5 轮,转人工后人工再问一遍 → 用户立刻爆炸。

正确做法:

```python
async def escalate_to_human(args):
    # 1. 生成结构化摘要(给坐席看,不给用户看)
    summary = {
        "user": session["user_id"],
        "profile_brief": "VIP / 3 年老客户 / 上月投诉过",
        "channel": session["channel"],
        "issue_summary": "..."(Claude 生成 50 字),
        "attempts": ["kb_search × 2 都没找到", "查了 order_o_67"],
        "sentiment": "下降中(-0.7)",
        "user_actual_ask": "...",
    }
    # 2. 路由到合适队列(售前/售后/VIP)
    queue = route_queue(summary)
    # 3. 推 Slack/飞书 + 会话链接
    notify_human(queue, summary, session_url)
    # 4. 告知用户
    return f"已为您转接 {queue} 专员,排队第 {pos},预计 {wait} 分钟"
```

**坐席侧打开就是结构化摘要 + 完整对话历史 + 已尝试方案。平均 AHT 能压 40%。**

---

## VIII. 评测体系 —— 客服 4 指标

跟纯 RAG 评测完全不同:

| 指标 | 含义 | 合格线 |
|---|---|---|
| **CSAT** | Customer Satisfaction(1-5) | > 4.2 |
| **Containment Rate** | AI 独立解决率(不转人工) | > 60% |
| **AHT** | Average Handle Time(秒) | < 180s |
| **FCR** | First Contact Resolution | > 75% |

**特别注意 DSAT 闭环**:评分 ≤ 2 的会话自动落 review 队列,T+1 人工抽检 → 找 prompt / KB / 工具问题。

---

## IX. 3 周快速落地

| 周 | 目标 | 交付 |
|---|---|---|
| **W1** | 单渠道 + 答疑 | 网页客服 + KB + 转人工兜底 |
| **W2** | 动作工具 + 多渠道 | 订单/物流 + 微信/小程序 |
| **W3** | 退款审批 + 评测 + 灰度 | 退款 hook + CSAT + 灰度 5% |

**W1 别上动作工具**。先把"答疑 + 兜底转人工"跑稳,**再加动作**。动作工具一上线,工程纪律(身份核验/金额上限/审计)立马翻倍。

---

## X. 三个工程坑

### 坑 1:Action 工具必须二次确认

错:用户说"帮我退款"→ Agent 直接调 `issue_refund`
对:Agent 调之前必须 **quote 用户原话** + **询问明确确认**:

> "您要退款的是订单 #o_67,金额 ¥328,对吗?回复'确认'后处理。"

### 坑 2:身份核验不能省

外部用户不可信。**任何 Action 工具调用前**:

1. 检查 `user_id` 跟 session 一致
2. 工具内部再校验 `order.user_id == user_id`
3. VIP/敏感操作需短信二次验证

LLM 不能负责安全,**安全在工具层**。

### 坑 3:别让 Claude 翻译"客服话术"

错:Agent 自己润色出来一句话给用户
对:**常用话术固定模板**(开场白/拒绝/转人工),Agent 只填空。

这一条让品牌调性可控、合规可控、法律取证可控。**LLM 越自由,商业风险越大**。

---

## XI. 升华

| 维度 | 知识库 Q&A | 客服系统 |
|---|---|---|
| 核心架构 | 检索 + 生成 | **State + 路由 + 动作 + 升级** |
| 工具类型 | 信息 | **信息 + 动作 + 分析 + 升级** |
| 评测 | RAGAS | **CSAT / Containment / AHT** |
| 失败兜底 | "我不知道" | **转人工带上下文** |
| 工程红线 | 引用 + ACL | **承诺监控 + 金额 + 二次确认** |

**关键认知**:客服系统是 KB + CRM + 工单 + 人工坐席的**编排器**。Claude 是大脑,但要的不是"聪明",要的是"克制" —— 不许承诺、不许越权、不许自由发挥。

KB Q&A 的关键词是"准确"。
**客服系统的关键词是"边界"**。

---

实战复盘 · AI 工具栈 · 行业落地篇
关键词:企业客服 / Claude Agent SDK / Containment Rate / CSAT / 转人工 / Action Tool / Subagent / Hooks
本文仅供学习参考。
