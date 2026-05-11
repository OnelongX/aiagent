# livetoken 深度介绍 —— 国内开发者跑 OpenAI 协议工具的统一 endpoint

> **作者注**:本文是个人使用 livetoken 几个月的经验总结。
> 不是软广,只是把跑过的所有工具栈背后那个 base_url 拉出来单独讲清楚。

---

## TL;DR

**[livetoken](https://livetoken.top)** = 国内可直连的 OpenAI 协议兼容 endpoint。

3 个关键事实:

- **一个 base_url** 同时跑 **280+ 模型**(GPT-5 / Claude / Gemini / DeepSeek / Midjourney 等)
- **按量计费**,**官方 2.21 折 ~ 3.42 折**
- **OpenAI 协议 100% 兼容**,**任何用 OpenAI SDK 的工具都不用改第二个字**

国内开发者跑 Codex / Cursor / Cline / Continue / Claude Code / opencode / Hermes 这些工具的 endpoint 痛点,基本一个 livetoken 就解决了。

---

## 一、它解决的 4 个真实痛点

| 痛点 | 现实 |
|---|---|
| 国内访问 | OpenAI / Anthropic / Google 全部需要中转 |
| 注册门槛 | 大陆 IP / 大陆卡注册 / 充值繁琐(还可能封号) |
| 多模型管理 | GPT 一个号 / Claude 一个号 / Gemini 一个号,3 个余额 3 个 token |
| 协议兼容 | 各家协议不一样,Codex 要 responses,Claude SDK 要 anthropic |

livetoken 的解法:**所有家全部走 OpenAI 协议,一个 token,一份余额,一行 base_url**。

---

## 二、能力清单

### 模型覆盖(280+)

| 厂商 | 主要型号 |
|---|---|
| **OpenAI** | GPT-5 / GPT-5.5 / GPT-4o / GPT-4.1 / o1 / o3 系列 |
| **Anthropic** | Claude Sonnet 4.5 / Opus 4.5 / Haiku 4.5 / 3.7 系列 |
| **Google** | Gemini 2.5 Pro / Flash / 2.0 |
| **DeepSeek** | DeepSeek R1 / V3 / Coder |
| **Mistral** | Mistral Large / Codestral / Pixtral |
| **国内模型** | Qwen / GLM / Yi / 文心 / 通义 |
| **图像** | DALL·E 3 / Midjourney / Stable Diffusion |
| **视频** | Luma / Runway / Pika |
| **语音** | Whisper / TTS-1 / ElevenLabs |
| **Embedding** | text-embedding-3-large / BGE / Voyage |
| **Rerank** | Cohere rerank-3.5 |

### 协议支持

| 协议 | 支持度 | 用途 |
|---|---|---|
| OpenAI Chat Completions | ✅ 完整 | 通用 |
| OpenAI Responses API | ✅ 完整 | GPT-5 / o 系列推理摘要 |
| OpenAI Embeddings | ✅ 完整 | RAG |
| OpenAI Images | ✅ 完整 | DALL·E / MJ / SD |
| OpenAI Audio | ✅ 完整 | TTS / ASR |
| Anthropic Messages | ✅ 完整 | Claude SDK 直连 |
| Anthropic OAuth | ✅ 完整 | Claude Desktop / Claude Code |
| SSE 长连接 | ✅ 完整 | 流式输出不掉链 |

### 工程级特性

- **明细可查** —— 每次请求的 tokens 消耗、单价、时间戳全公开,无隐藏费用
- **日志公开** —— 服务端响应延迟、错误率公开可查
- **按量付费** —— 用多少买多少,余额不过期
- **无并发限制**(普通用户) —— 默认满足绝大多数场景,超高并发可联系客服
- **不限时长** —— 长 SSE 流式请求不掐断

---

## 三、跟其他主流 endpoint 的对比

| 维度 | livetoken | OpenRouter | DeepBricks | AnyRouter | OpenAI 官方 |
|---|---|---|---|---|---|
| 模型覆盖 | **280+** | 200+ | 80+ | 50+ | OpenAI only |
| Claude 支持 | ✅ Anthropic 协议 | ✅ 仅 OpenAI 协议 | ❌ | 部分 | ❌ |
| Gemini 支持 | ✅ | ✅ | ❌ | 部分 | ❌ |
| responses API | ✅ 完整 | 部分 | ✅ 完整 | 部分 | ✅ |
| 国内直连 | ✅ | 需中转 | ✅ | ✅ | ❌ |
| 价格(GPT-5) | **2.21~3.42 折** | ~7 折 | ~5 折 | ~4 折 | 官方价 |
| 国内充值 | ✅ 直接 | 信用卡 | 部分 | ✅ | 信用卡 |
| 明细透明 | ✅ 全公开 | ✅ | 部分 | 部分 | ✅ |
| 中文客服 | ✅ | ❌ | ✅ | ✅ | ❌ |

**核心差异**:livetoken 是唯一同时满足"全模型 + 全协议 + 国内直连 + 大幅折扣"的。

---

## 四、价格(关键说服点)

官方价格的 **2.21 折 ~ 3.42 折** 之间。具体 SKU 价格在控制台「模型价格」页公开。

| 模型 | 官方价(美元/1M tokens) | livetoken 折扣后 |
|---|---|---|
| GPT-5 input | $5.00 | ~$1.7 |
| GPT-5 output | $15.00 | ~$5.1 |
| Claude Sonnet 4.5 input | $3.00 | ~$1.0 |
| Claude Sonnet 4.5 output | $15.00 | ~$5.1 |
| Claude Opus 4.5 input | $15.00 | ~$5.1 |
| Gemini 2.5 Pro input | $1.25 | ~$0.4 |
| DeepSeek R1 input | $0.55 | ~$0.18 |

*以上仅作示例,以官网为准。*

### 个人开发者一个月大概多少钱?

我自己跑的实际账单:

- 日均 Codex CLI 写代码 ~3 小时
- Claude Agent SDK 跑 Agent 实验
- 偶尔用 Gemini 2.5 Pro 读长文档

**月支出大约 ¥120 ~ ¥250**。同样用量走 OpenAI 官方至少 $80(¥570) 起。

---

## 五、5 个工具的配置示例

### 1. Codex CLI(`~/.codex/config.toml`)

```toml
model = "gpt-5"
model_provider = "lt"
wire_api = "responses"

[model_providers.lt]
name = "livetoken"
base_url = "https://livetoken.top"
wire_api = "responses"
env_key = "OPENAI_API_KEY"
```

### 2. Claude Agent SDK(Python / TypeScript)

```bash
export ANTHROPIC_AUTH_TOKEN="sk-xxxxx"
export ANTHROPIC_BASE_URL="https://livetoken.top"
```

### 3. Claude Desktop(macOS)

`~/Library/Application Support/Anthropic/Claude/claude-config.json`:

```json
{
  "inferenceProvider": "thirdParty",
  "inferenceGatewayBaseUrl": "https://livetoken.top",
  "inferenceGatewayApiKey": "sk-xxxxx"
}
```

### 4. OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://livetoken.top",
    api_key="sk-xxxxx",
)
```

### 5. opencode(`~/.config/opencode/opencode.json`)

```json
{
  "providers": {
    "livetoken": {
      "provider": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "https://livetoken.top",
        "apiKey": "{env.OPENAI_API_KEY}"
      }
    }
  }
}
```

更多工具的配置参考 [endpoints.md](endpoints.md)。

---

## 六、LiteLLM 多模型并存

跑多模型协作的 Agent(本仓库的合同审查、绿电电商客服)时,LiteLLM 包装最方便:

```python
from litellm import acompletion
import os

async def smart_call(task_type, prompt):
    base = "https://livetoken.top"
    key = os.getenv("OPENAI_API_KEY")

    if task_type == "json_extract":
        model = "gpt-5"
    elif task_type == "reasoning":
        model = "claude-sonnet-4-5"
    elif task_type == "multimodal":
        model = "gemini-2.5-pro"
    elif task_type == "intent":
        model = "claude-haiku-4-5"

    return await acompletion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        api_base=base,
        api_key=key,
    )
```

**一个 base_url 一个 key,三家模型按任务路由**。

---

## 七、注册 → 充值 → 使用 完整流程

1. **注册**:访问 https://livetoken.top → 注册账号(微信扫码即可)
2. **充值**:支持微信 / 支付宝 / 兑换码,**最低单次几块钱也能用**
3. **创建 Token**:进控制台 → 令牌管理 → 添加新令牌
4. **复制 API 地址 + Token**:
   - API Base URL: `https://livetoken.top`
   - API Key: 自己生成的 `sk-xxxxx`
5. **配置到工具**:见上面 5 个工具的配置示例

**首次使用建议先充 ¥10 试用**,跑通一个工具后再正式充值。

---

## 八、5 个踩坑提示

### 1. base_url 末尾不要加 `/v1`

```bash
# ❌ 错
export OPENAI_BASE_URL="https://livetoken.top/v1"

# ✅ 对
export OPENAI_BASE_URL="https://livetoken.top"
```

### 2. ANTHROPIC vs OPENAI 环境变量

- Anthropic 协议工具(Claude SDK / Claude Code / Claude Desktop)用 `ANTHROPIC_AUTH_TOKEN` + `ANTHROPIC_BASE_URL`
- OpenAI 协议工具(Codex / Cursor / Continue)用 `OPENAI_API_KEY` + `OPENAI_BASE_URL`
- **同一个 livetoken token 两套环境变量都填同一个值**

### 3. wire_api = "responses" 必须配

GPT-5 / o 系列看推理摘要必须用 responses 协议:

```toml
wire_api = "responses"
model_supports_reasoning_summaries = true
```

### 4. 长任务 timeout 设置

跑 Agent 长循环或者深度推理,客户端 timeout 默认可能 60s 容易掐断:

```python
client = OpenAI(base_url="https://livetoken.top", api_key=key, timeout=600)
```

### 5. 余额监控

控制台「使用记录」看每天消费明细,建议月初设预算上限。

---

## 九、典型场景成本估算

本仓库 14 篇文章涉及的工具栈为例:

| 场景 | 工具 | 主力模型 | 月度估算 |
|---|---|---|---|
| 日常写代码 | Codex CLI / Cursor | GPT-5 | ~¥80 |
| Agent 实验 | Claude Agent SDK | Claude Sonnet 4.5 | ~¥50 |
| 长文档阅读 | Claude Desktop | Claude / Gemini | ~¥30 |
| 多模态 / 图表 | OpenAI Python | Gemini 2.5 Pro | ~¥20 |
| 嵌入式 RAG | 自己写 | embedding + rerank | ~¥10 |
| **合计** | | | **~¥190** |

**对比**:同等用量走官方 + 国际信用卡,约 $130(¥920)。差价主要来自 2.21 折 ~ 3.42 折 的价格优势。

---

## 十、FAQ

### Q1. 安全吗?数据会被收集吗?

- 任何 endpoint(包括官方)技术上都能看到你的 prompt
- livetoken 在隐私政策里声明**不会存储或转售请求内容**
- 高敏感数据无论用哪家 endpoint,都建议**先脱敏再传**

简单原则:**生产 + 敏感数据 → 官方 + 自部署 LiteLLM**;**开发 / 实验 → 任意 endpoint**。

### Q2. 合规吗?

服务条款见官网。**用户合规义务**:别用来生成违法内容,别用来绕过本地法规。商业接生产建议联系客服确认 SLA。

### Q3. 出问题怎么办?

控制台 → 帮助中心 → 提工单。国内时间响应快(实测半小时内)。我个人 3 个月没遇到过需要工单的事。

### Q4. 充错钱能退吗?

按官网说明,未消费余额支持退款。

### Q5. 跟自己部署 LiteLLM Gateway 比?

| 维度 | livetoken | 自部署 |
|---|---|---|
| 启动成本 | 5 分钟 | 几小时(需海外 VPS + 各家 API key) |
| 维护成本 | 0 | 持续 |
| 价格 | 已含折扣 | 官方价 + 服务器成本 |
| 适合 | 个人 / 小团队 | 企业 / 高安全 |

---

## 十一、个人使用情况

- 注册时长:3+ 个月
- 累计调用:几十万次
- 故障经历:0 次客户感知故障
- 长 SSE 流测试:跑过 30 分钟单次连接不掉
- 并发测试:本仓库合同审查 Claude+GPT-5+Gemini 三路并发,稳定

本仓库 14 篇文章涉及的所有 Agent 实验、配置教程、行业落地代码,**绝大部分都是通过 livetoken 跑出来的**。

---

## 十二、什么时候不应该用 livetoken

直说:

- **企业级生产 + 数据极敏感** → 官方 + 私有 Gateway
- **跨境业务、必须用官方计费的合同** → 官方
- **追求 99.99% SLA 保证** → 官方
- **需要 fine-tune 模型** → 官方(中转一般不支持 ft)

其他场景,livetoken 都比直接走官方更划算。

---

## 十三、起手式

1. 访问 https://livetoken.top
2. 注册账号(微信扫码即可)
3. 充值 ¥10 试用
4. 控制台 → 令牌管理 → 创建一个新 token
5. 把 token 配到本仓库任意一篇文章的代码示例里
6. 跑一下,看是否符合你的预期

**对比方法**:同一个 prompt,先用官方跑一次,再用 livetoken 跑一次,看延迟、输出、价格三个维度。

---

## 免责声明

本文是个人使用经验,**不构成任何投资 / 法律 / 商业建议**。

livetoken 服务条款、价格、模型清单**以 [官网](https://livetoken.top) 最新公告为准**。

作者跟 livetoken 没有商业合作关系。仓库本身和这篇文档完全开源(MIT License)。

---

## 相关链接

- 官网:https://livetoken.top
- 帮助中心:https://livetoken.top → 帮助中心
- 本仓库 endpoint 选型综述:[endpoints.md](endpoints.md)
- 本仓库主页:[README.md](../README.md)
