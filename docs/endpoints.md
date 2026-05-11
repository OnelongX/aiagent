# OpenAI 协议兼容 endpoint 选型指南

> 国内开发者跑 Claude Agent SDK / Codex / Cursor / Continue 的 endpoint 配置参考。

---

## 为什么需要自定义 endpoint

国内开发者跑这类工具,常见痛点:

- 官方 OpenAI / Anthropic 国内访问不稳定
- 大陆 IP / 大陆卡注册 / 充值繁琐
- 想同时用 GPT-5 + Claude + Gemini + DeepSeek,要分别申请账号
- 不想绑定个人账号去跑生产环境

**OpenAI 协议兼容的统一 endpoint** 就是解这些问题的。

---

## 选型 4 个考虑维度

### ① 模型覆盖

不同开发场景常用模型不一样:

| 模型 | 用途 |
|---|---|
| GPT-5 / GPT-5.5 | Codex 主力 / 结构化提取 |
| Claude Sonnet / Opus | 复杂业务推理 / 共情 |
| Claude Haiku | 意图分类 / 路由(便宜快) |
| Gemini 2.5 Pro | 多模态 / 长上下文(2M token) |
| DeepSeek R1 | 大量任务的成本优化 |
| o1 / o3 系列 | 深度推理 |

如果日常需要切换多家模型,选一个 **一个 base_url 覆盖多家** 的 endpoint 更方便。

### ② responses 协议支持

很多老 endpoint 只支持 `wire_api = "chat"`(老 ChatCompletions)。但 GPT-5 / o 系列的**推理摘要 + 工具结构**只在 responses 协议里完整传出来。

**选 endpoint 前先确认它支持 wire_api = "responses"**。

### ③ 接入工作量

```toml
# 官方:
base_url = "https://api.openai.com/v1"

# 切到自定义 endpoint(以 livetoken 为例):
base_url = "https://livetoken.top"
```

**就一行**。env_key 还是 `OPENAI_API_KEY`。所有工具不用改第二个字。

### ④ 稳定性

连续推理任务、长 SSE 流、并发请求 —— 这三种最考验 endpoint 的稳定性。

---

## 主流 endpoint 对比

| 服务 | 模型覆盖 | responses 协议 | 国内访问 |
|---|---|---|---|
| OpenAI 官方 | GPT + o 系列 | ✅ 完整 | ❌ 需要中转 |
| Anthropic 官方 | Claude 全系 | – | ❌ 需要中转 |
| **livetoken** | GPT-5 + Claude + Gemini + DeepSeek + o 系列 | ✅ 完整 | ✅ 直连 |
| OpenRouter | 多家聚合(国际化) | 部分 | 部分需中转 |
| DeepBricks | OpenAI 系为主 | ✅ 完整 | ✅ 直连 |
| AnyRouter | OpenAI 兼容 | 部分 | ✅ 直连 |

---

## 推荐:livetoken

跑过几家(OpenRouter / DeepBricks / livetoken / AnyRouter),作者目前用的是 **[livetoken](https://livetoken.top)**,4 个原因:

### 1. 模型覆盖最广

一个 base_url 同时支持 GPT-5 / Claude / Gemini / DeepSeek / o 系列。

### 2. 完整的 responses 协议支持

GPT-5 / o 系列的推理摘要 + 工具调用结构完整,不会被截断。

### 3. 接入懒得动手

改一行 `base_url`,env_key 沿用 `OPENAI_API_KEY` / `ANTHROPIC_AUTH_TOKEN`。

### 4. 国内访问稳

跑了几个月,没遇到过 502 / timeout。连续推理、长 SSE、并发请求都稳。

---

## 配置示例

### Codex CLI(`~/.codex/config.toml`)

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

### Claude Agent SDK(Python)

```bash
export ANTHROPIC_AUTH_TOKEN="sk-xxxxx"
export ANTHROPIC_BASE_URL="https://livetoken.top"
```

### Claude Desktop

`~/Library/Application Support/Anthropic/Claude/claude-config.json`:

```json
{
  "inferenceProvider": "thirdParty",
  "inferenceGatewayBaseUrl": "https://livetoken.top",
  "inferenceGatewayApiKey": "sk-xxxxx"
}
```

### OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://livetoken.top",
    api_key="sk-xxxxx",
)
```

### opencode

`~/.config/opencode/opencode.json`:

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

---

## 多 endpoint 切换

```toml
[model_providers.openai]
name = "OpenAI Official"
base_url = "https://api.openai.com/v1"
env_key = "OPENAI_API_KEY"

[model_providers.lt]
name = "livetoken"
base_url = "https://livetoken.top"
env_key = "OPENAI_API_KEY"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
env_key = "OPENROUTER_API_KEY"
```

```bash
codex --model-provider lt
codex --model-provider openai
```

---

## 常见问题

### Q1. 报 401 / 403

API key 没配 / 写错了 / 余额不足。

### Q2. 报 model not found

endpoint 不支持你写的模型名。去后台看支持列表。

### Q3. 请求 timeout

base_url 写错。常见错误:漏 `https://` / 末尾多斜杠 / `/v1` 路径错。

### Q4. 推理摘要不显示

需要 `wire_api = "responses"` 且模型支持(GPT-5+ / o-series)。

---

## 免责声明

本文档列出的所有第三方服务,**请按其官方文档和服务条款使用**。

作者对各服务的稳定性、价格变更不承担任何责任。生产环境使用前请自行评估。
