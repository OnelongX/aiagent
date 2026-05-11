# 绿电电商客服系统 —— Claude + GPT-5 双引擎下单闭环

> 实战复盘 · AI 工具栈 · 行业落地集大成
>
> 把方案助手 + 客服骨架 + 真实电商纪律 三层叠加。
> Agent 接 OMS,工程纪律的复杂度是 RAG 的 3 倍。

---


<div align="center">

<a href="https://github.com/OnelongX/aiagent">
<img src="../../assets/wechat-qrcode.png" width="160" alt="公众号:iamonelong" />
</a>

📖 **本文同步发布于公众号「实战复盘」** · 微信号:`iamonelong`
🌐 [完整代码仓库 · github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型:[docs/livetoken.md](../../docs/livetoken.md)

</div>

---

## I. 这是行业落地系列的集大成篇

承接前 4 篇:

| # | 篇目 | 解决的问题 |
|---|---|---|
| 1 | 家庭绿电方案助手 | 出方案(不下单) |
| 2 | 合同审查助手 | 多模型协作降漏判 |
| 3 | 企业知识库 Q&A | 内部检索 + 评测 |
| 4 | 企业客服系统 | 通用客服骨架(无业务) |
| **5** | **绿电电商客服(本篇)** | **方案 + 报价 + 下单 + 售后 全闭环** |

**本篇是把前 4 篇能力熔合的集大成 ——** 用户进来咨询,Agent 出方案、报价、下单、追单、售后,全流程在一个 Agent SDK 编排器里。

---

## II. 业务全流程

```
咨询  →  出方案  →  报价  →  下单  →  支付  →  排施工  →  并网  →  售后
        ↑ 复用 #1                ↑ 工程纪律重区          ↑ 长尾客服
        4 Subagent              库存/价格/支付/审计
```

跟纯 KB 客服最大的不同:**一旦用户说"我要买",钱就要动**。这条引出整套工程纪律。

---

## III. 真实系统对接 —— API + DB 两条线

电商后端不可能全自己造,典型公司至少接 7 个系统:

| 系统 | 接什么 | 接法 |
|---|---|---|
| **OMS** 订单中心 | 下单 / 改单 / 查单 | REST API(写)+ DB 只读副本(查) |
| **WMS / 库存** | 实时库存 / 预占 | REST API(必须实时,不缓存) |
| **PMS** 商品中心 | 价格 / SKU / 套餐 | DB 直连 + Redis 价格缓存 |
| **CRM** 用户中心 | 用户档案 / 历史 / VIP | DB + API 混合 |
| **支付网关** | 起单 / 回调 / 退款 | API only |
| **物流** | 物流 / 安装档期 | API(可缓存 5 分钟) |
| **KB** | 政策 / FAQ / 补贴 | Qdrant(复用 #3) |

**关键纪律**:**写操作只走 API,不直连 DB**。Agent 不能 `INSERT INTO orders` —— OMS 还有事务、库存联动、风控规则。

---

## IV. 工具层 —— 18 工具 4 类

### A. 信息工具(读 · 无副作用)

```python
@tool("get_pricing", "查实时报价",
      {"items": list, "region": str, "user_id": str})
async def get_pricing(args):
    """直接查 PMS + 应用区域/会员折扣"""
    pricing = pms_db.execute("""
        SELECT sku, base_price, region_factor, member_discount
        FROM v_realtime_pricing
        WHERE sku = ANY(:skus) AND region = :region
    """, skus=args["items"], region=args["region"]).fetchall()
    return {"content":[{"type":"text","text":json.dumps(pricing)}]}

@tool("check_inventory", "查实时库存", {...})
async def check_inventory(args):
    # 走 WMS API,不走 DB,毫秒级变化
    resp = await wms_api.get(f"/inventory/{args['sku']}")
    return ...

@tool("get_subsidy", "查当地补贴政策", {...})
@tool("get_installer_capacity", "查施工档期", {...})
@tool("get_user_profile", "拉用户档案", {...})
@tool("get_user_orders", "查历史订单", {...})

# 复用 #1 的 6 工具(方案助手内部)
get_irradiance / estimate_yield / match_load /
size_battery / payback / select_panels
```

### B. 动作工具(写 · 必须 guard)

```python
@tool("create_order", "创建订单",
      {"user_id": str, "items": list, "address": dict,
       "expected_total": float, "idempotency_key": str})
async def create_order(args):
    # 1. 重新拉价(不信 Agent 传的)
    server_price = await recompute_price(args["items"], args["user_id"])
    if abs(server_price - args["expected_total"]) > 0.01:
        return {"error": "price_changed", "new_price": server_price}
    # 2. 幂等性
    existing = oms_db.find_by_idempotency(args["idempotency_key"])
    if existing:
        return {"order_id": existing.id, "status": "duplicate"}
    # 3. 预占库存 5 分钟
    reservation = await wms_api.reserve(args["items"], ttl=300)
    # 4. 真正下单
    order = await oms_api.create(
        user_id=args["user_id"],
        items=args["items"],
        address=args["address"],
        total=server_price,
        reservation_id=reservation.id)
    return {"order_id": order.id}

@tool("request_payment", "发起支付链接",
      {"order_id": str, "channel": str})
async def request_payment(args):
    """Agent 不能完成支付,只能起链接"""
    url = await pay_gateway.create_link(args["order_id"], args["channel"])
    return {"pay_url": url, "expires_in": 900}

@tool("apply_coupon", "用券", {...})
@tool("schedule_installation", "排施工", {...})
@tool("cancel_order", "取消订单(仅未支付)", {...})
@tool("update_address", "改地址(仅未发货)", {...})
@tool("create_aftersale_ticket", "建售后工单", {...})
@tool("escalate_to_human", "转人工", {...})
```

### C. 分析 + 风控工具

```python
@tool("analyze_intent", "意图 + 情绪", {...})
@tool("check_risk", "风控打分",
      {"user_id": str, "session_id": str})
# 同 IP 多账号 / 高频下单 / IP 风险库 / 设备指纹
```

### D. 复用方案助手(consultant 子流程)

```python
@tool("generate_plan", "生成绿电方案",
      {"region": str, "roof_m2": float, "annual_kwh": float, ...})
async def generate_plan(args):
    """内部跑 #1 的 4 Subagent + 6 工具"""
    plan = await plan_agent.run(args)
    return {"plan_id": plan.id, "summary": plan.summary, "skus": plan.skus}
```

---

## V. Subagent 编排(5 段流水线)

```python
agents = {
    "triager": AgentDefinition(
        prompt="先 analyze_intent + get_user_profile + check_risk。"
               "新客户咨询 → consultant; 已有方案要下单 → order-clerk; "
               "已下单要查/改 → ops-tracker; 投诉 → escalator。",
        tools=["analyze_intent", "get_user_profile",
               "get_user_orders", "check_risk"],
        model="haiku"),

    "consultant": AgentDefinition(
        prompt="generate_plan → 出方案。"
               "再 get_pricing + get_subsidy + get_installer_capacity 拼报价单。",
        tools=["generate_plan", "get_pricing", "get_subsidy",
               "get_installer_capacity", "check_inventory"],
        model="sonnet"),

    "order-clerk": AgentDefinition(
        prompt="下单前必须 quote 用户原话 + 等明确'确认'。"
               "create_order 传 idempotency_key。"
               "再 request_payment 给支付链接。"
               "禁止替用户支付。",
        tools=["create_order", "apply_coupon",
               "request_payment", "cancel_order"],
        model="sonnet"),

    "ops-tracker": AgentDefinition(
        prompt="查单 / 改地址 / 排施工 / 物流追踪。"
               "已发货后改地址必须转人工。",
        tools=["get_user_orders", "track_shipping",
               "schedule_installation", "update_address",
               "create_aftersale_ticket"],
        model="sonnet"),

    "escalator": AgentDefinition(
        prompt="结构化摘要 → escalate_to_human。",
        tools=["escalate_to_human"],
        model="haiku"),
}
```

---

## VI. Claude vs GPT-5 任务分配 —— 双引擎

**不要二选一,按任务分**:

| 任务 | 推荐 | 原因 |
|---|---|---|
| **主对话 / 推理** | Claude Sonnet 4.5 | 长链推理 + 共情 + 合规语言 |
| **下单参数提取** | GPT-5 | tool_calls 准 · JSON 严格 |
| **价格 / 数字密集** | GPT-5 | 数字处理强 · 不漂 |
| **方案生成 / 售后情绪** | Claude | 软调性 + 引用准 |
| **意图分类** | Haiku / GPT-5 mini | 谁便宜用谁 |
| **风控判断** | GPT-5 | 结构化推理 + 多变量打分 |

**实现 —— Multi-provider gateway**:

```python
from litellm import acompletion

async def smart_call(task_type, prompt, **kwargs):
    if task_type in ("order_param_extract", "risk_score", "pricing"):
        model = "gpt-5"
    elif task_type in ("plan_draft", "aftersale_reply"):
        model = "claude-sonnet-4-5"
    elif task_type == "intent":
        model = "claude-haiku" if cheap else "gpt-5-mini"
    return await acompletion(model=model, messages=[...], **kwargs)
```

Agent SDK 主流程用 Claude(SDK 原生),工具内部按任务调 LiteLLM 走 GPT-5。**主流程 + 工具双引擎,各取所长**。

---

## VII. 下单流程 6 条工程纪律

最容易出生产事故的一段:

| # | 纪律 | 实现 |
|---|---|---|
| 1 | **价格防篡改** | `create_order(expected_total)` 服务端重算,Agent 传的价只比对 |
| 2 | **库存预占** | 创建订单瞬间锁 5 分钟,超时释放 |
| 3 | **幂等性** | `idempotency_key = session_id + plan_id` |
| 4 | **二次确认** | 调 `create_order` 前 quote 原话 + 等"确认" |
| 5 | **Agent 不付款** | 只起支付链接,用户在站外完成 |
| 6 | **风控前置** | triager 必先 `check_risk` |

```python
hooks = {
  # 价格变了 → 强制重新报价
  "PostToolUse:create_order":
      replan_pricing if parsed(r).get("error")=="price_changed",

  # 单笔 > ¥5 万 → 必须人工审批
  "PreToolUse:create_order":
      deny_or_ticket if expected_total > 50000,

  # 风控异常 → 直接转人工
  "PostToolUse:check_risk":
      force_escalate if score > 0.7,

  # 已支付订单改地址 → 必须转人工
  "PreToolUse:update_address":
      escalate if order_status == "paid",

  # Agent 想"承诺补偿 X 元" → 拦截改写
  "PostToolUse:generate_response":
      rewrite if forbidden_promise,
}
```

---

## VIII. State 机硬约束

状态机绝不能让 LLM 自由跳转,**写死在工具层**:

```
咨询 → 已出方案 → 已下单 → 已支付 → 已排单 → 已发货 → 已安装 → 已并网 → 已完成
                                          │
                                          ├→ 取消 (仅未支付)
                                          ├→ 退款 (仅未发货)
                                          └→ 售后工单 (任意状态)
```

工具内部硬校验:

```python
async def cancel_order(args):
    order = await oms_api.get(args["order_id"])
    if order.status not in ("pending_payment",):
        return {"error": "cannot_cancel", "current": order.status,
                "hint": "已支付订单需走退款流程"}
    ...
```

LLM 看不到 DB,**只能从工具返回拿状态**。Prompt injection 再花哨,状态机都不会被突破。

---

## IX. 数据安全 3 道防线

电商场景攻击向量比 KB 多得多:

| 防线 | 实现 |
|---|---|
| **1. ACL 在工具层** | `get_order(order_id, user_id)` 内部强校验 `order.user_id == user_id` |
| **2. 价格服务端重算** | Agent 传 expected_total 仅 cross-check,**不直接扣款** |
| **3. 敏感字段脱敏** | 工具返回的手机号/地址/身份证全 mask,Agent 看不到原文 |

**永远不要在 prompt 里写**"如果用户说退 1000 就退 1000"。退款金额必须从 `get_order` 工具来,不从对话历史来。

---

## X. 3 周落地路线

| 周 | 目标 | 交付 |
|---|---|---|
| **W1** | 咨询 + 出方案 + 报价(只读) | 复用 #1 + 接 PMS / KB |
| **W2** | 下单 + 支付链接 + 订单查询 | OMS / WMS / 支付网关接通 · 幂等 + 风控 + 二次确认 |
| **W3** | 售后 + 改单 + 物流 + 评测 + 灰度 | 工单 + Containment 评测 + 灰度 5% 流量 |

**关键纪律**:

- W1 绝不上 `create_order`
- W2 上线时金额上限 ¥1000(灰度)
- W3 才放开 ¥50000 + 全量

---

## XI. 三个工程坑

### 坑 1:别让 Agent 计算订单金额

错:Agent 自己算"方案 A 8 块板 × ¥1500 = ¥12000,减优惠券 ¥500 = ¥11500"
对:**只调 `get_pricing` 拿,只调 `apply_coupon` 抵扣,自己一个加法都不算**

LLM 算 8×1500 都可能错,何况叠加优惠券、阶梯折扣、税。所有计算下推到 PMS。

### 坑 2:重单是头号生产事故

用户在 30 秒内点了两次"下单",Agent 跑了两遍 `create_order` → 真扣两单。

**强制 idempotency_key**:`session_id + plan_id` 做 key,服务端 unique index。重复请求返回原订单 ID。

### 坑 3:售前 / 售后 prompt 必须分离

售后场景的 prompt 跟下单完全不同(共情 vs 严谨)。强烈建议:

- 售前 / 下单 → session_type=`presale`,prompt 严谨
- 售后 / 投诉 → session_type=`aftersale`,prompt 软调性
- 切换由 `triager` 显式做,不让 Agent 自己漂

---

## XII. 升华

| 维度 | #1 方案 | #4 通用客服 | **本篇** |
|---|---|---|---|
| 目标 | 出方案 | 答疑 + 转人工 | **方案 + 报价 + 下单 + 售后** |
| 工具数 | 6 | 12 | **18 + 复用 #1 全部** |
| 工程红线 | 数字必走工具 | 承诺监控 | **价格防篡改 + 幂等 + 状态机** |
| 失败兜底 | "我不知道" | 转人工 | **降级到出报价单,不下单** |
| 模型架构 | Claude 单家 | Claude 单家 | **Claude + GPT-5 双引擎** |

**核心认知**:把 Agent 接入 OMS,工程纪律的复杂度是上一篇的 3 倍。

**真正的难点不在 LLM,在 OMS / 库存 / 支付网关稳不稳**。LLM 再聪明,OMS 一个并发 bug,全线崩。

**绿电电商客服系统 = 方案助手 + 客服骨架 + 真实电商工程纪律**。三层叠加,缺一不可。

---

行业落地子系列 5 篇收官:

| # | 关键词 | 工程模式 |
|---|---|---|
| 1 | 确定性 | 单模型 + 工具调度 |
| 2 | 降漏判 | 多模型协作 + 分级触发 |
| 3 | 准确 | 数据 + 权限 + 评测 |
| 4 | 克制 | State + 路由 + 边界 |
| **5** | **闭环** | **熔合前 4 篇 + 接真实业务系统** |

从单工具调度,到多模型协作,到 RAG,到客服骨架,到完整电商闭环 —— **Claude Agent SDK 的行业纵深图谱完整了**。

下一步,跨行业平移:法律 / 医疗 / 金融 / 教育,模式完全一样。

---

实战复盘 · AI 工具栈 · 行业落地集大成
关键词:Claude Agent SDK · GPT-5 · 电商客服 · OMS 集成 · 双引擎 · 下单闭环 · 幂等性 · 价格防篡改 · 状态机
本文仅供学习参考。
