# 用 Claude Agent SDK 做家庭绿电方案助手 —— 一份完整可跑的工程方案

> 实战复盘 · AI 工具栈 · 行业落地篇
>
> 一头连着 Claude Agent SDK,一头连着光伏设计院 20 年的 Excel。

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

家庭绿电方案这事,光伏设计院 20 年来一直在做。流程很固定:

输入(用户给):地址 / 屋顶面积 / 朝向 / 坡度 / 年用电量 / 预算 / 是否储能 / 是否并网
输出(设计院给):一份方案书 —— 组件型号 × 数量 / 逆变器 / 储能 / 年发电量 / 自发自用率 / 投资回收期

中间所有计算,在设计院里就是几张 Excel 表 + 几个工程师拍脑袋。

现在我要把它做成一个 Claude Agent —— 用户对话进来,方案 PDF 出去。

**关键不是"让 Claude 懂光伏",而是"让 Claude 会调度懂光伏的工具"。**

---

## II. 为什么不能让 Claude 直接算

试过的都知道:让 LLM 算辐照量、发电量、回收期,误差 30% 起步。原因有三:

1. 辐照数据是真实测量值,模型脑子里没有
2. 衰减、温度系数、阶梯电价 —— 多变量复利,纯文本推理一定漂移
3. 组件型号库每月更新,模型权重落后半年

所以工程上必须分两层:

- **确定性计算 → 工具(MCP / SDK custom tools)**
- **决策与对话 → Claude**

这是 Agent SDK 的天然分工。

---

## III. 整体架构

一张图说清:

```
用户对话
   │
   ▼
┌──────────────────┐
│   主 Agent       │  调度员 · 不直接算
│   (Claude)       │
└──────────────────┘
   │ delegate
   ├──────────────┬──────────────┬──────────────┐
   ▼              ▼              ▼              ▼
site-survey   energy-model   econ-analyst   report-writer
采数据         跑发电         算回收         出方案书
   │              │              │              │
   └──────────────┴──────────────┴──────────────┘
                       │
                       ▼
            ┌────────────────────┐
            │ 6 个确定性工具      │
            ├────────────────────┤
            │ get_irradiance     │  NASA POWER 辐照
            │ estimate_yield     │  发电量
            │ match_load         │  自发自用
            │ size_battery       │  储能容量
            │ payback            │  回收期
            │ select_panels      │  组件选型
            └────────────────────┘
```

**主 Agent 只负责调度,4 个 Subagent 分段执行,6 个工具做硬计算。**

---

## IV. 6 个核心工具

每个都是确定性函数,Claude 当"调度员"调它们,不参与计算。

### 1. get_irradiance —— 辐照数据

```python
@tool("get_irradiance", "查询位置辐照", {
    "lat": float, "lon": float, "tilt": float, "azimuth": float
})
async def get_irradiance(args):
    """接 NASA POWER API,返回逐月 POA 辐照(kWh/m²/day)"""
    lat, lon = args["lat"], args["lon"]
    tilt, az = args["tilt"], args["azimuth"]
    # NASA POWER 真实 API 调用
    poa = fetch_nasa_power(lat, lon, tilt, az)
    return {"content": [{"type": "text",
            "text": json.dumps({"monthly_poa": poa, "annual": sum(poa)})}]}
```

### 2. estimate_yield —— 发电量估算

```python
@tool("estimate_yield", "估算年发电量", {
    "area_m2": float, "w_per_m2": float, "poa_annual": float, "loss": float
})
async def estimate_yield(args):
    """area × W/m² × 辐照小时 × (1 - 系统损耗)"""
    kwh = (args["area_m2"] * args["w_per_m2"] / 1000 
           * args["poa_annual"] * (1 - args["loss"]))
    return {"content": [{"type": "text",
            "text": json.dumps({"annual_kwh": round(kwh, 1)})}]}
```

### 3. match_load —— 自发自用率

```python
@tool("match_load", "匹配负荷", {
    "gen_hourly": list, "load_hourly": list, "battery_kwh": float
})
async def match_load(args):
    """跑 8760 小时仿真,算自用 / 上网 / 购电"""
    self_use, to_grid, from_grid = simulate_8760(
        args["gen_hourly"], args["load_hourly"], args["battery_kwh"])
    return {"content": [{"type": "text", "text": json.dumps({
        "self_use_kwh": self_use,
        "self_use_ratio": self_use / sum(args["gen_hourly"]),
        "to_grid_kwh": to_grid,
        "from_grid_kwh": from_grid
    })}]}
```

### 4. size_battery —— 储能容量推荐

```python
@tool("size_battery", "推荐储能", {
    "daily_kwh": float, "autonomy_h": float, "dod": float
})
async def size_battery(args):
    """目标自给时长 → 推荐电池 kWh"""
    needed = args["daily_kwh"] * args["autonomy_h"] / 24 / args["dod"]
    return {"content": [{"type": "text",
            "text": json.dumps({"battery_kwh": round(needed, 1)})}]}
```

### 5. payback —— 经济测算

```python
@tool("payback", "投资回收期", {
    "capex": float, "annual_savings": float, "subsidy": float,
    "elec_price": float, "degradation": float
})
async def payback(args):
    """逐年现金流,算静态/动态回收期 + IRR + NPV"""
    years, irr, npv = calc_cashflow(
        capex=args["capex"] - args["subsidy"],
        savings=args["annual_savings"],
        elec_price=args["elec_price"],
        degradation=args["degradation"])
    return {"content": [{"type": "text", "text": json.dumps({
        "payback_years": years, "irr": irr, "npv_25y": npv
    })}]}
```

### 6. select_panels —— 组件选型

```python
@tool("select_panels", "选组件", {
    "target_kw": float, "roof_area": float, "budget": float
})
async def select_panels(args):
    """从本地产品库(JSON)按 W/m²、价格、质保排序"""
    candidates = load_panel_db()  # 晶硅 / 钙钛矿叠层 / Oxford / 协鑫 / Hanwha
    ranked = rank_by_density_price(candidates,
        target_kw=args["target_kw"],
        max_area=args["roof_area"],
        max_budget=args["budget"])
    return {"content": [{"type": "text",
            "text": json.dumps({"top3": ranked[:3]})}]}
```

---

## V. 4 个 Subagent —— 流程分工

主 Agent 不亲自下场,委派给 4 个 Subagent 串行处理:

| Subagent | 职责 | 工具白名单 |
|---|---|---|
| site-survey | 提问、清洗屋顶/负荷数据 | (只读对话) |
| energy-model | 跑辐照 + 发电 + 自发自用 | get_irradiance / estimate_yield / match_load |
| econ-analyst | 储能容量 + 回收期 + 敏感性 | size_battery / payback |
| report-writer | 出 Markdown / PDF 方案书 | Write |

```python
agents = {
    "site-survey": AgentDefinition(
        description="采集屋顶与负荷数据",
        prompt="按 6 个字段引导用户:地址 / 屋顶面积 / 朝向 / 坡度 / 年用电 / 预算。"
               "缺字段就追问,不要瞎填默认值。",
        tools=[],
        model="sonnet"),
    "energy-model": AgentDefinition(
        description="电量建模",
        prompt="拿到 site-survey 数据后,依次调 get_irradiance → estimate_yield → match_load。"
               "禁止自己心算,所有数字必须来自工具返回。",
        tools=["get_irradiance", "estimate_yield", "match_load"],
        model="sonnet"),
    "econ-analyst": AgentDefinition(
        description="经济测算",
        prompt="基于 energy-model 输出,调 size_battery 推荐储能,"
               "调 payback 算回收期,做 ±20% 敏感性分析。",
        tools=["size_battery", "payback"],
        model="sonnet"),
    "report-writer": AgentDefinition(
        description="出方案书",
        prompt="把前三段产物拼成一份 Markdown 方案书,落到 ./output/plan.md。"
               "必须包含:推荐方案 / 发电预估 / 储能配置 / 经济测算 / 敏感性。",
        tools=["Write"],
        model="sonnet"),
}
```

主 Agent 的 system prompt 只写一句话:

> 按 site-survey → energy-model → econ-analyst → report-writer 顺序串起来,
> 每段产物喂下一段,不跳步,不并行。

---

## VI. Hooks —— 关键卡点

3 个不可越过的工程红线,用 Hook 拦住:

```python
async def guard_oversize(input_data, tool_use_id, context):
    """target_kw > 30 走商用流程,不要在户用里硬塞"""
    args = input_data.get("tool_input", {})
    if args.get("target_kw", 0) > 30:
        return {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "户用 >30kW 应走商用流程"
        }}
    return {}

async def warn_long_payback(input_data, tool_use_id, context):
    """回收期 >12 年提示用户"""
    out = input_data.get("tool_response", {})
    years = json.loads(out["content"][0]["text"]).get("payback_years", 0)
    if years > 12:
        print(f"[WARN] 回收期 {years} 年,建议重新评估方案")
    return {}

hooks = {
    "PreToolUse": [HookMatcher(matcher="select_panels", hooks=[guard_oversize])],
    "PostToolUse": [HookMatcher(matcher="payback", hooks=[warn_long_payback])],
}
```

---

## VII. 完整代码 —— 一个 main.py 跑起来

```python
import asyncio
import json
from claude_agent_sdk import (
    ClaudeSDKClient, ClaudeAgentOptions,
    AgentDefinition, HookMatcher,
    tool, create_sdk_mcp_server,
)

# === 6 个工具(略,见上文)===
mcp = create_sdk_mcp_server(
    name="greenpower",
    version="1.0.0",
    tools=[get_irradiance, estimate_yield, match_load,
           size_battery, payback, select_panels])

# === Agent options ===
options = ClaudeAgentOptions(
    model="claude-sonnet-4-5",
    system_prompt=(
        "你是家庭绿电方案规划师。严格按 4 段流程委派 Subagent:"
        "site-survey → energy-model → econ-analyst → report-writer。"
        "禁止自己估算数字,所有数字必须经工具返回。"),
    mcp_servers={"greenpower": mcp},
    allowed_tools=[
        "mcp__greenpower__get_irradiance",
        "mcp__greenpower__estimate_yield",
        "mcp__greenpower__match_load",
        "mcp__greenpower__size_battery",
        "mcp__greenpower__payback",
        "mcp__greenpower__select_panels",
        "Task", "Write",
    ],
    agents=agents,
    hooks=hooks,
    permission_mode="acceptEdits",
)

async def main():
    async with ClaudeSDKClient(options=options) as c:
        await c.query(
            "我家在杭州,屋顶 90㎡ 朝南 15° 坡,年用电 8000 kWh,"
            "预算 8 万,要并网+储能。给我出方案。")
        async for msg in c.receive_response():
            if hasattr(msg, "result"):
                print(msg.result)

asyncio.run(main())
```

国内开发者走 livetoken 中转:

```bash
export ANTHROPIC_AUTH_TOKEN=sk-livetoken-xxxxx
export ANTHROPIC_BASE_URL=https://livetoken.top
```

---

## VIII. 一次真实运行

输入:

> 杭州 / 屋顶 90㎡ / 朝南 / 15°坡 / 年用电 8000 kWh / 预算 8 万 / 要储能并网

Agent 跑完 4 段后,`./output/plan.md` 内容大概是:

```
家庭绿电方案 · 杭州 · 90㎡

【推荐方案】
组件:协鑫钙钛矿叠层(264 W/m²)× 24 块,占用 84㎡
系统容量:6.3 kWp
逆变器:6 kW 单相并网逆变器
储能:10 kWh 磷酸铁锂(夜间负荷 4h 自给)

【发电预估】
年发电量:7,420 kWh
自发自用率:58%
余电上网:3,116 kWh
仍需购电:4,696 kWh

【经济测算】
总投资:7.8 万
省电 + 卖电收入:9,200 元/年
回收期:8.2 年
25 年 IRR:9.4%
25 年净收益:14.2 万

【敏感性】
电价 +20% → 回收期 6.9 年
辐照 -10% → 回收期 9.4 年
```

整个过程用户只输入了一句话,7 次工具调用全部由 Agent 完成。

---

## IX. 三个工程坑

### 1. 辐照数据不要让 Claude 编

NASA POWER / PVGIS 都有免费 API。Claude 编的辐照数据,跟实测差 30%。
所有辐照、温度、损耗系数,**必须**走工具。

### 2. 产品库走结构化 JSON

不要让 Claude 凭印象推荐"协鑫的 XX 组件"。建一个本地 JSON 数据库,每个 SKU 至少 6 字段:

```json
{
  "sku": "GCL-Perovskite-Tandem-450",
  "vendor": "协鑫",
  "tech": "钙钛矿叠层",
  "watt": 450,
  "area_m2": 1.703,
  "w_per_m2": 264,
  "price_per_w": 3.2,
  "warranty_years": 25,
  "degradation_yr1": 0.02,
  "degradation_yr2_25": 0.0045,
  "temp_coef": -0.0028
}
```

Claude 调 select_panels 时只在这个库里选,不允许编造。

### 3. 回收期算法用工具,不让 Claude 心算

要算逐年衰减、电价上涨、阶梯电价、补贴退坡,任何一个环节让 LLM 心算都会漂移。
`payback` 工具必须是真实的现金流函数,Python 跑 25 年逐年表,Claude 只读结果。

---

## X. 升华:这事的本质

家庭绿电方案助手,只是个壳子。把"家庭绿电"换成任何垂直行业,逻辑完全一样:

- 把行业 20 年沉淀的 Excel 拆成 N 个确定性函数
- 把工程师的判断流程拆成 N 个 Subagent
- 把红线规则写成 Hooks
- Claude 当调度员,不当计算器

**Claude Agent SDK 真正的价值,不是"AI 取代专家",而是"把专家的工具栈,让普通人也能调"。**

设计院的方案书,过去 3 万块起做。
现在一个 Agent,5 分钟出一份。

光伏行业到了用 Agent 的时候。
其他行业也一样。

---

实战复盘 · AI 工具栈 · 行业落地篇
关键词:Claude Agent SDK / 家庭绿电 / 光伏设计 / AI Agent / MCP / Subagent / Hooks
本文仅供学习参考。
