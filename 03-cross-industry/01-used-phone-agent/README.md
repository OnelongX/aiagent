# 二手手机推荐 + 售卖 Agent —— 2B/2C 双线 + 微信生态全打通

> 实战复盘 · AI 工具栈 · 跨行业平移 第 1 篇
>
> 把绿电电商的工程模式,平移到二手 3C。
> Claude 是大脑,GPT-5 是会计,Gemini 是质检员。

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

## I. 跟绿电电商的 4 个核心差异

承接上一篇绿电电商客服。绿电是**标品 + 长决策**,二手手机是**非标 + 快决策 + 双客群** —— 工程上比绿电更难:

| 维度 | 绿电电商(#5) | 二手手机(本篇) |
|---|---|---|
| SKU | 标品(同型号统一价) | **每台 IMEI 唯一** + 品相分级 |
| 推荐 | 不需要,出方案 | **必须有推荐引擎**(约束 + 库存平衡) |
| 客群 | 单一 2C | **2C + 2B 双线**(零售 + 批发) |
| 渠道 | 网页为主 | **微信生态全打通**(公众号/小程序/企微/视频号) |

---

## II. 业务全流程 · 双流水线

```
┌─── 2C 零售线 ──────────────────────────────────────┐
咨询 → 需求确认 → 推荐 → 看图对比 → 议价 → 下单 → 物流 → 售后
公众号  小程序   微信     图册      客服   支付   顺丰   工单

┌─── 2B 批发线 ──────────────────────────────────────┐
询价 → 资质审核 → 批量报价 → 验货抽检 → 合同 → 采购单 → 账期回款
企微    工单     谈判表格   质检汇总   电子签   ERP    财务
```

**关键设计**:两条线**共享底层**(SKU 库 / 库存 / 物流 / 财务),但 **prompt / 工具组合 / Subagent 完全分离**。零售客户被批发口吻吓跑,批发客户嫌零售啰嗦。

---

## III. 数据特殊性 —— IMEI 唯一 + 12 项检测

```sql
-- 每台手机一行,不是按型号
CREATE TABLE phone_sku (
    imei            VARCHAR(15) PRIMARY KEY,
    model_id        VARCHAR(50),       -- iphone-14-pro-max-256
    color           VARCHAR(20),
    storage         INT,
    condition_grade VARCHAR(10),       -- A+/A/B+/B/C
    battery_health  INT,               -- 76-100
    screen_repaired BOOLEAN,
    motherboard_repaired BOOLEAN,
    water_damaged   BOOLEAN,
    icloud_locked   BOOLEAN,
    inspection_report_id VARCHAR(50),  -- PDF / 图片
    cost_price      DECIMAL,
    list_price      DECIMAL,
    min_floor_price DECIMAL,           -- 议价底线 · Agent 看不到
    days_in_stock   INT,               -- 库龄 · 影响推荐权重
    status          VARCHAR(20)
);
```

**检测报告 = 信任壁垒**。每台至少 12 项检测,**Agent 必须能读懂 PDF/图片**:

```python
@tool("fetch_inspection_report", "拉检测报告",
      {"imei": str})
async def fetch_inspection_report(args):
    # PDF/图片走 Gemini 多模态
    file = genai.upload_file(f"./reports/{args['imei']}.pdf")
    return genai.GenerativeModel("gemini-2.5-pro").generate_content([
        file,
        "提取 JSON:屏幕/外壳/电池/主板/摄像头/接口/无线/通话/进水/换件/系统/iCloud。"
        "每项打分 0-100。"
    ])
```

---

## IV. 推荐引擎 —— 约束匹配 + 库存平衡

**二手手机不是协同过滤**(SKU 唯一,没"买过这台的还买了什么")。是**约束满足 + 库存权重排序**:

```python
@tool("recommend_phones", "推荐手机",
      {"budget_min": float, "budget_max": float,
       "brand": list, "min_ram": int, "min_storage": int,
       "color_pref": list, "min_battery": int,
       "min_condition": str, "user_id": str})
async def recommend_phones(args):
    # 1. 硬约束过滤(SQL)
    candidates = phone_db.execute("""
        SELECT * FROM phone_sku
        WHERE status='在售'
          AND list_price BETWEEN :bmin AND :bmax
          AND brand = ANY(:brands)
          AND storage >= :min_storage
          AND battery_health >= :min_battery
          AND condition_grade <= :min_condition
        LIMIT 200
    """, ...).fetchall()

    # 2. 软偏好打分
    for c in candidates:
        c.score = (
            color_match(c.color, args["color_pref"]) * 0.2 +
            condition_score(c.condition_grade)       * 0.3 +
            price_value_score(c)                     * 0.3 +
            stock_age_boost(c.days_in_stock)         * 0.2   # ← 老库存加权
        )

    # 3. 多样性 rerank
    top = mmr_diversify(candidates, k=5)
    return top
```

**关键创新点 —— 库龄加权**。同样满足条件的两台,**优先推库龄 60+ 天**的。二手手机库龄成本极高,算法主动帮老板清库存。

---

## V. 工具层 · 20 工具 4 组

### A. 共享底层(2B + 2C 都用)

```python
get_phone_detail(imei)            # 单机详情
fetch_inspection_report(imei)     # 检测报告(Gemini)
verify_imei_official(imei)        # 苹果/华为官网真伪查询
get_price_history(model_id)       # 30/90 天价格趋势
get_market_price(model_id)        # 闲鱼/拍拍/转转 比价
check_inventory(model_id, grade)  # 在库统计
```

### B. 2C 零售工具

```python
recommend_phones(...)             # 推荐引擎
compare_devices(imei_list)        # 对比表
calc_trade_in(old_imei)           # 以旧换新估价
apply_huabei(order_total)         # 花呗分期
create_retail_order(...)          # 零售下单
schedule_delivery(order_id)       # 顺丰预约
```

### C. 2B 批发工具

```python
check_buyer_credit(buyer_id)      # 信用线 / 账期 / 历史回款
bulk_quote(model, qty, grade)     # 阶梯报价(100/500/1000 台)
generate_batch_csv(quote_id)      # 出 Excel 报价单
batch_inspection_summary(po_id)   # 整批质检汇总
create_purchase_order(...)        # 采购单(支持账期)
sign_contract_esign(po_id)        # 法大大/e签宝
```

### D. 微信生态工具

```python
wx_send_kf_message(openid, msg)   # 公众号客服消息(48h 窗口)
wx_send_image(openid, image_url)  # 推图
wx_corp_external(...)              # 企微外部联系人
wx_mp_open_chat(...)              # 小程序内置客服
wx_create_payorder(order_id)      # 微信支付
wx_video_account_dm(...)          # 视频号私信
```

---

## VI. Subagent 编排 · 双流水线

```python
agents = {
    # ─── 共享入口 ───
    "triager": AgentDefinition(
        prompt="先 analyze_intent + identify_channel。"
               "channel=公众号/小程序 + intent=买 → retail-flow; "
               "channel=企微 + intent=批量 → wholesale-flow; "
               "已下单要查 → ops-tracker。",
        tools=["analyze_intent", "get_user_profile", "check_buyer_credit"],
        model="haiku"),

    # ─── 2C 零售 ───
    "retail-consultant": AgentDefinition(
        prompt="需求 4 件套必须问全:预算 / 品牌 / 内存 / 用途。"
               "再 recommend_phones 出 3-5 台。"
               "用户挑中后 fetch_inspection_report。"
               "议价上限 = list_price * 0.95(底线在工具里)。",
        tools=["recommend_phones", "get_phone_detail",
               "fetch_inspection_report", "verify_imei_official",
               "compare_devices", "calc_trade_in", "apply_huabei",
               "wx_send_image", "wx_send_kf_message"],
        model="sonnet"),

    "retail-clerk": AgentDefinition(
        prompt="下单前 quote 用户原话 + 确认 IMEI + 总价。"
               "create_retail_order(idempotency_key)。"
               "锁 IMEI 直到付款或超时。",
        tools=["create_retail_order", "wx_create_payorder",
               "schedule_delivery", "cancel_order"],
        model="sonnet"),

    # ─── 2B 批发 ───
    "wholesale-negotiator": AgentDefinition(
        prompt="先 check_buyer_credit。再 bulk_quote 阶梯报价。"
               "议价:每降 1% 需说明库龄/库存压力。"
               "底价由工具返回的 min_floor 决定,Agent 不能突破。",
        tools=["check_buyer_credit", "bulk_quote",
               "generate_batch_csv", "check_inventory",
               "get_market_price"],
        model="sonnet"),

    "wholesale-clerk": AgentDefinition(
        prompt="生成 PO + 合同 · 法大大签字。"
               "确认账期 + 首付 + 验货条款。",
        tools=["create_purchase_order", "sign_contract_esign",
               "batch_inspection_summary"],
        model="sonnet"),

    "ops-tracker": ...,
    "escalator": ...,
}
```

**关键设计**:`triager` 用 **channel + intent 双信号路由**。2C 走小步快跑,2B 走慢工细活。

---

## VII. 微信生态打通 —— 4 触点 1 套 backend

```
公众号 (Service)    → OpenID-A · 48h 客服消息窗口
小程序 (Mini Prog)  → OpenID-A (同公众号) · 内置客服 + 支付
企业微信 (Work)     → External UserID · 1v1 + 群机器人
视频号 (Channels)   → OpenID-A · 私信 + 直播弹幕
              ↓
       统一用户中台 (unionid 串)
              ↓
       Agent SDK orchestrator
```

**核心实现**:

```python
@app.post("/wx/webhook")
async def wx_webhook(msg):
    channel = detect_channel(msg)        # mp / mini / corp / video
    unionid = resolve_unionid(msg)       # 跨平台串号
    text = extract_text(msg)             # 文本/语音 ASR/图片 OCR

    session = redis.get(f"session:{unionid}")
    result = await agent.run(text, session=session, channel=channel)

    if channel == "mp":
        wx_kf.send(openid, result.text)
    elif channel == "corp":
        wx_corp.send_external(external_userid, result.text)
    elif channel == "mini":
        return {"reply": result.text}     # 同步返回
```

**关键纪律 4 条**:

- **OpenID ≠ UnionID** —— 公众号和小程序是不同 OpenID,要靠 UnionID 串
- **48 小时窗口**(公众号客服)—— 超过要走模板消息(企业认证后)
- **企业微信外部联系人** —— 不能主动发,只能用户先开口
- **视频号弹幕** —— 高频弹幕走限流 + 关键词预过滤,不能每条灌给 Claude

---

## VIII. 三引擎模型分配

| 任务 | 推荐 | 原因 |
|---|---|---|
| 检测报告解读(PDF/图) | **Gemini 2.5 Pro** | 多模态 + 表格 |
| 2C 推荐对话 / 共情 | **Claude Sonnet 4.5** | 软调性 + 推理 |
| 2B 阶梯报价谈判 | **GPT-5** | 数字推理 + 结构化 |
| 库存平衡排序 | **不用 LLM** | 写死加权公式 |
| 真伪验证 | **不用 LLM** | 调苹果/华为 API |
| 风控打分 | **GPT-5** | 多变量结构化 |
| 客服话术 | **Claude** | 品牌调性可控 |

---

## IX. 二手手机特有的 7 条工程纪律

| # | 纪律 | 实现 |
|---|---|---|
| 1 | **IMEI 不允许 Agent 拼写** | 用户说"那台金色 128G",必须工具返回 IMEI |
| 2 | **报价底线在数据库** | Agent 看到 list_price,看不到 min_floor_price |
| 3 | **库存锁定**(零售) | 推荐不锁,确认下单瞬间锁 IMEI,5 分钟超时 |
| 4 | **iCloud/SN 锁前置检测** | 推荐结果含 icloud_status,锁机直接过滤 |
| 5 | **批发议价审计** | 每次让价必须工具记录(为啥让),供老板审计 |
| 6 | **2B 信用线硬约束** | 超信用线 → 强制人工 + 担保金 |
| 7 | **退换 SOP 写死** | 7 天无理由仅限"未激活+未拆封",激活后走故障排查 |

---

## X. 3-4 周快速落地

| 周 | 目标 | 交付 |
|---|---|---|
| **W1** | 公众号 + 小程序 + 2C 推荐 | 5 工具(只读)+ recommend_phones + 客服消息 |
| **W2** | 2C 下单 + 微信支付 + 物流 | OMS 接通 · 幂等 · IMEI 锁 · 灰度 ¥3000 上限 |
| **W3** | 2B 批发 + 企业微信 + 阶梯报价 | 信用线 + bulk_quote + 法大大签约 |
| **W4** | 检测报告 OCR + 售后 + 评测 | Gemini 报告 + 工单 + Containment 评测 |

**关键纪律**:**W1 不做推荐**也行,先做"问什么答什么 + 转人工"。Recommend 是质量天花板的活,要花时间做榜单 A/B 测试。

---

## XI. 二手手机特有的 4 个工程坑

### 坑 1:用户问"有没有便宜的"

模糊需求,Agent 只能问回去。**强制对话状态机**:

```
state = "need_more_info"
缺失字段:budget / brand / use_case / storage
缺一个问一个 · 一次只问一个 · 别 5 个一起问
```

### 坑 2:议价回合无限循环

用户:"再便宜 50?" → Agent:"再降 30 行?" → 用户:"50!" → 死循环。

**议价工具内置回合限制**:`max_rounds=3`,超过直接给最终价 + 转人工。

### 坑 3:检测报告 OCR 出错 → 客诉

Gemini 解析 PDF 偶尔把"电池健康 88%"读成"98%"。**双源校验**:OCR 结果 + 数据库登记值不一致 → 强制人工复核。

### 坑 4:微信支付回调 + IMEI 锁定竞态

付款瞬间和 IMEI 锁超时瞬间冲突 → 钱收了但 IMEI 被别人锁走。

**事务流**:`扣库存 → 锁 IMEI → 起支付 → 回调成功 → 真正出库`,任一环节失败 → 全部回滚。

---

## XII. 升华

| 维度 | 绿电电商(#5) | **本篇** |
|---|---|---|
| SKU | 标品 | **每台 IMEI 唯一** |
| 推荐 | 不需要 | **必须有引擎** |
| 客群 | 单一 2C | **2B + 2C 双线** |
| 检测 | 厂保 | **12 项报告 + Gemini 解读** |
| 议价 | 一口价 | **2C 小议 + 2B 阶梯谈判** |
| 渠道 | 网页为主 | **微信生态 4 触点** |
| 模型 | Claude + GPT-5 | **Claude + GPT-5 + Gemini 三引擎** |

**核心认知**:二手手机 Agent 比绿电更难的不是 LLM,是 **三件事**:

1. **数据精度** —— IMEI 唯一 + 12 项检测,数据脏一点客诉爆表
2. **双客群隔离** —— 2C 和 2B 的话术、报价、流程绝对不能混
3. **微信生态琐碎** —— OpenID / UnionID / 48h 窗口 / 外部联系人,每个 API 都有坑

**Claude 是大脑,GPT-5 是会计,Gemini 是质检员。三个角色协作,才能撑起一个能跑的二手手机电商 Agent。**

---

## XIII. 跨行业平移的本质

这一篇是行业落地系列的**「跨行业平移」第 1 篇**。

| 系列 | 篇数 | 主轴 |
|---|---|---|
| 行业落地(#1-#5) | 5 | 在绿电行业建立 SDK 工程模板 |
| 跨行业平移(本篇起) | … | 把模板迁移到 3C / 法律 / 医疗 / 金融 |

**验证一个核心假设**:Claude Agent SDK 沉淀的工程模式(Subagent / Hooks / 双引擎 / State 机 / 工程纪律)是**行业无关的**。换一个行业,只换数据 + 工具,模式照搬。

二手手机 = 第一次跨行业验证,**模式成立**。

接下来法律 / 医疗 / 金融 / 教育,都用这套模板平移即可。

---

实战复盘 · AI 工具栈 · 跨行业平移 第 1 篇
关键词:二手手机 / Claude Agent SDK / GPT-5 / Gemini / 推荐引擎 / 微信生态 / 2B+2C / 双引擎
本文仅供学习参考。
