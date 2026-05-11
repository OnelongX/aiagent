# opencode 配置完整教程 —— 开源 AI 编程 CLI · 一个工具跑遍 75+ 模型

> **TL;DR**:opencode 是 **开源 AI 编程 CLI**——跟 Codex / Claude Code 同类,但 **不绑厂商 + 75+ 模型聚合 + 完全开源**。本文从安装到自定义 provider 接入全拆 + 实战 livetoken 接入。**核心杀招**:一个 opencode 同时跑 GPT / Claude / Gemini / DeepSeek / Qwen,真正的"AI 编程通用 CLI"。


<div align="center">

<a href="https://github.com/OnelongX/aiagent">
<img src="../../assets/wechat-qrcode.png" width="320" alt="公众号:IamOnelong" />
</a>

📖 **本文同步发布于公众号「实战复盘」** · 微信号:`IamOnelong`
🌐 [完整代码仓库 · github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型:[docs/livetoken.md](../../docs/livetoken.md)

</div>

---

承接 AI 编程工具栈系列前 3 篇:

- 系列 1:Codex CLI 配置完整教程
- 系列 2:Codex 三端通用配置
- 系列 3:Claude 全家桶配置教程

**这一篇是第 4 个 AI 编程引擎** —— **opencode**。

---

## 一、opencode 是什么 —— 跟 Codex / Claude Code 的差别

3 个工具同类,但定位不同:

| 维度 | Codex | Claude Code | opencode |
|---|---|---|---|
| 厂商 | OpenAI | Anthropic | sst.dev / 社区 |
| **开源** | ❌ 闭源 | ❌ 闭源 | **✓ 开源(Go)** |
| 主要模型 | GPT 系列 | Claude 系列 | **任意 75+ provider** |
| 协议 | Responses API | Messages API | **OpenAI 兼容(可适配任意)** |
| 自定义 provider | 单 provider | 单 provider | **多 provider 共存** |
| 多端 | CLI / 桌面 / VS Code | CLI / 桌面 / VS Code | TUI / CLI / 多端 |

**opencode 最大特点**:**通用**——跟 Codex / Claude Code 不同,**它不绑特定厂商**。

可以同时配:
- OpenAI 官方
- Anthropic 官方
- Gemini
- DeepSeek
- Llama / Qwen 本地或云端
- **任何 OpenAI 兼容服务**

---

## 二、安装

### 方式 1:Homebrew(推荐)

```bash
brew install anomalyco/tap/opencode
```

**注意**:用 `anomalyco/tap` 这个 tap,**比官方 Homebrew formula 更新更快**——新功能 / 新 model 支持先在这里出。

### 方式 2:npm 全局

```bash
npm install -g opencode-ai
```

### 方式 3:install 脚本

```bash
curl -fsSL https://opencode.ai/install | bash
```

### 验证

```bash
opencode --version
```

**输出版本号 = 装好了**。

---

## 三、首次启动

```bash
cd 你的项目目录
opencode
```

进入 **TUI 界面**(终端图形化交互)——长得跟 Codex / Claude Code 类似,但**界面更花哨**(opencode 是 Go 写的,UI 用了 Bubble Tea 框架)。

### 第一次进入要做的事

```
/connect
```

输入 `/connect` 命令 —— opencode 列出**已知的所有 provider**(OpenAI / Anthropic / Gemini / DeepSeek / Groq / 等等)。

选一个 → 输入 API key → 自动写入配置。

或者选 **"Other"** → 输入自定义 provider ID → 走第三方接入(下面讲)。

---

## 四、配置文件详解

### 配置文件位置

| 范围 | 路径 |
|---|---|
| **全局** | `~/.config/opencode/opencode.json` |
| **项目** | `<project>/opencode.json` |

**项目 config 优先级高于全局**——同一项目里可以指定不同 provider / 模型。

### 最简配置(只用 OpenAI 官方)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "openai": {
      "options": {
        "apiKey": "sk-xxxxx"
      }
    }
  }
}
```

### 完整结构

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "openai/gpt-5",
  "provider": {
    "openai": { "options": { "apiKey": "..." } },
    "anthropic": { "options": { "apiKey": "..." } },
    "custom-relay": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "My Relay",
      "options": { "baseURL": "https://livetoken.top" },
      "models": {
        "gpt-5.5": { "name": "GPT-5.5" },
        "claude-sonnet-4": { "name": "Claude Sonnet 4" }
      }
    }
  }
}
```

### 关键字段

| 字段 | 说明 |
|---|---|
| `$schema` | JSON schema 验证(VS Code 会自动提示)|
| `model` | 默认模型(格式 `provider/model-name`)|
| `provider` | 所有提供商的配置块 |
| `provider.X.npm` | 用哪个 AI SDK 适配器 |
| `provider.X.options.apiKey` | API key |
| `provider.X.options.baseURL` | 自定义 endpoint |
| `provider.X.models` | 该 provider 下可见的模型清单 |

---

## 五、自定义 Provider 接入(关键技术段)

opencode 的强项 —— **任何 OpenAI 兼容服务**都能接入。

### 通用模板

```json
"my-provider": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "My Provider",
  "options": {
    "baseURL": "https://your-endpoint.com",
    "apiKey": "sk-xxxxx"
  },
  "models": {
    "model-name-1": { "name": "Display Name 1" },
    "model-name-2": { "name": "Display Name 2" }
  }
}
```

3 个关键参数:

| 参数 | 说明 |
|---|---|
| `npm` | 永远填 `@ai-sdk/openai-compatible`(适配 OpenAI 兼容 API) |
| `options.baseURL` | 第三方 endpoint **根 URL**(部分聚合服务 /v1 由后端处理) |
| `options.apiKey` | API key(也可以用 env 变量) |

### env 变量替代写死 key

写死 API key 容易被误传 Git。**用环境变量更安全**:

```json
"my-provider": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "My Provider",
  "options": {
    "baseURL": "https://your-endpoint.com",
    "apiKey": "{env:MY_PROVIDER_KEY}"
  }
}
```

然后:

```bash
export MY_PROVIDER_KEY="sk-xxxxx"
```

opencode 启动时自动展开 `{env:...}` 变量。

---

## 六、实战:livetoken 接 opencode

> **不是广告**,是说一下我配置时的实际选择。

我配 Codex 用 livetoken,配 Claude Code 也用 livetoken(参考前 3 篇)。**配 opencode 继续用同一个 token**——4 个具体原因:

### 1. 一个 token 跑遍 75+ 模型

opencode 设计就是多模型聚合,**livetoken 也是多模型聚合**——天作之合。

我在 opencode 里配的模型:

```json
"livetoken": {
  "npm": "@ai-sdk/openai-compatible",
  "name": "Livetoken",
  "options": {
    "baseURL": "https://livetoken.top",
    "apiKey": "{env:LIVETOKEN_API_KEY}"
  },
  "models": {
    "gpt-5.5": { "name": "GPT-5.5" },
    "gpt-5": { "name": "GPT-5" },
    "claude-sonnet-4": { "name": "Claude Sonnet 4" },
    "claude-opus-4": { "name": "Claude Opus 4" },
    "gemini-2.5-pro": { "name": "Gemini 2.5 Pro" },
    "deepseek-r1": { "name": "DeepSeek R1" },
    "qwen-3-coder": { "name": "Qwen3 Coder" }
  }
}
```

**一个 provider 块,7 个模型同时可用**——在 opencode TUI 里 `/model` 命令切换。

### 2. base_url 不需要 /v1

注意 `"baseURL": "https://livetoken.top"`(根 URL,不带 /v1)——livetoken 后端**自动路由**所有 OpenAI 兼容路径。

### 3. opencode 工具调用 / 多 agent 都正常

opencode 比 Codex / Claude Code 多支持的:
- **Subagent / Task 工具**(类似 Claude Code 的 subagent)
- **MCP 接入**(opencode 也支持 MCP)
- **本地模型**(可以同时配 Ollama / vLLM 跑本地)

第三方代理服务**经常会丢这些功能的语义**——livetoken 这边都正常。

### 4. 同一个 token 跑 Codex + Claude Code + opencode

最杀招:

```bash
# 一个 token 同时配 3 套 AI 编程引擎
export OPENAI_API_KEY="sk-livetoken-xxxxx"        # Codex 用
export ANTHROPIC_AUTH_TOKEN="sk-livetoken-xxxxx"  # Claude Code 用
export ANTHROPIC_BASE_URL="https://livetoken.top"

export LIVETOKEN_API_KEY="sk-livetoken-xxxxx"     # opencode 用
```

**3 套 AI 编程引擎 + 同一个余额** = AI 编程工具栈极致方案。

---

## 七、给 Codex / Claude Code 用户的迁移建议

如果你已经在用 Codex 或 Claude Code,**要不要换 opencode?**

### 别换 —— 继续用 Codex / Claude Code 的场景

- 重度依赖 **Codex Plan 模式 + 沙箱**
- 重度依赖 **Claude Code 的 CLAUDE.md 项目记忆 + Subagent**
- VS Code 扩展使用频率高(opencode 的 IDE 集成还在迭代)

### 推荐换 / 加装 opencode 的场景

- 想 **一个 CLI 跑多个模型**(GPT + Claude + DeepSeek 等)
- 想 **本地模型 + 云端模型混用**(Ollama + livetoken)
- 想 **完全开源**(可审计 / 可魔改)
- 团队部署:opencode 因为开源,**审计 / 内网部署更友好**

### 最实用方案 —— 3 个全装

我自己 3 个都装:

| 工具 | 主要场景 |
|---|---|
| **Codex** | 写代码 / Plan 模式 / VS Code 内嵌 |
| **Claude Code** | 重构 / 长上下文 / Subagent 协作 |
| **opencode** | 多模型对比 / 本地模型 / 团队场景 |

**3 个工具都用 livetoken token** —— 切换无成本。

---

## 八、3 套预设(复制即用)

### 预设 1:开发主力(GPT-5.5 + Claude Sonnet 双模型)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "livetoken/gpt-5.5",
  "provider": {
    "livetoken": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Livetoken",
      "options": {
        "baseURL": "https://livetoken.top",
        "apiKey": "{env:LIVETOKEN_API_KEY}"
      },
      "models": {
        "gpt-5.5": { "name": "GPT-5.5" },
        "claude-sonnet-4": { "name": "Claude Sonnet 4" }
      }
    }
  }
}
```

### 预设 2:多模型试用(7 模型矩阵)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "livetoken/claude-sonnet-4",
  "provider": {
    "livetoken": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Livetoken",
      "options": {
        "baseURL": "https://livetoken.top",
        "apiKey": "{env:LIVETOKEN_API_KEY}"
      },
      "models": {
        "gpt-5.5": { "name": "GPT-5.5" },
        "gpt-5": { "name": "GPT-5" },
        "claude-sonnet-4": { "name": "Claude Sonnet 4" },
        "claude-opus-4": { "name": "Claude Opus 4" },
        "gemini-2.5-pro": { "name": "Gemini 2.5 Pro" },
        "deepseek-r1": { "name": "DeepSeek R1" },
        "qwen-3-coder": { "name": "Qwen3 Coder" }
      }
    }
  }
}
```

进入 opencode 后用 `/model` 命令切换。

### 预设 3:本地 + 云端混合

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ollama/llama-3.3",
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Ollama Local",
      "options": {
        "baseURL": "http://localhost:11434/v1",
        "apiKey": "ollama"
      },
      "models": {
        "llama-3.3": { "name": "Llama 3.3 (local)" },
        "qwen-3": { "name": "Qwen 3 (local)" }
      }
    },
    "livetoken": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Livetoken",
      "options": {
        "baseURL": "https://livetoken.top",
        "apiKey": "{env:LIVETOKEN_API_KEY}"
      },
      "models": {
        "claude-sonnet-4": { "name": "Claude Sonnet 4 (cloud)" }
      }
    }
  }
}
```

**本地跑 Ollama + 云端跑 livetoken** —— 简单任务用本地省钱,复杂任务切到云端。

---

## 九、常见问题

### Q1. opencode 启动报 `provider not found`

`provider` 块名没对上 `model` 字段的前缀。

例:`"model": "livetoken/gpt-5.5"` 必须有 `"provider": { "livetoken": {...} }`。

### Q2. 调用报 401 / 403

API key 不对。检查:
- `apiKey` 字段是不是写对
- 用 `{env:VAR}` 的话,环境变量是不是真有

```bash
echo $LIVETOKEN_API_KEY
```

### Q3. timeout / 连接失败

`baseURL` 写错了。常见错误:
- 写成 `"baseURL": "https://livetoken.top/"` (末尾斜杠)
- 写成 `"baseURL": "livetoken.top"`(漏 https://)
- 写成 `"baseURL": "https://livetoken.top/v1/"`(有的服务不需要 /v1)

### Q4. opencode 跟 Codex / Claude Code 配置冲突吗?

**不冲突**——3 个工具的配置文件路径完全不同:

- Codex: `~/.codex/config.toml`
- Claude Code: `~/.claude/settings.json`
- opencode: `~/.config/opencode/opencode.json`

3 套独立。**API key 可以共用**(都指向 livetoken),但配置互不影响。

### Q5. /model 命令为啥列不全所有模型

`provider.X.models` 里没列出来。**opencode 只显示你在 config 里明确声明的模型**,不会自动从 livetoken 拉模型清单。

要新模型 → 加进 `models` 块。

### Q6. opencode 支持 MCP 吗?

支持。在 config 里加 `"mcp"` 块:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]
    }
  }
}
```

跟 Claude Desktop 的 MCP 配置语法一致。

---

## 十、留言钩子

跟着教程跑一遍配置过程,**任何环节卡住、报错、配不通**,都可以在评论区留言:

- 哪一步卡住的
- 完整报错信息
- 你用的是哪个第三方服务

我看到会回复。

也欢迎留言:
- 你 Codex / Claude Code / opencode 哪个用得多
- 想看哪些实战教程(MCP 进阶 / Subagent / 多 agent 协作 / 本地模型部署)
- 团队部署 opencode 有什么坑

**评论区见**。

---

## 升华

> Codex + Claude Code + opencode = AI 编程工具栈三件套
>
> 一个 livetoken token · 跑遍 3 套引擎 · 共享余额
>
> **国内 AI 编程工作流的极致方案**

3 套 + 1 token = 你的工具栈应该是这样:

| 任务 | 推荐 | 模型 |
|---|---|---|
| 写代码 / VS Code 实时 | **Codex** | GPT-5.5 |
| 重构 / Plan 模式 | **Claude Code** | Claude Sonnet |
| 多模型对比 / 本地模型混用 | **opencode** | 任意 |

**3 个工具 + 75+ 模型 + 1 个 token** —— 没有更精简的方案了。

---

## 附录:Codex + Claude Code + opencode 三引擎一键配置

```bash
#!/bin/bash
# 三引擎一键配置脚本

# 1. 安装 3 个 CLI
npm install -g @openai/codex
npm install -g @anthropic-ai/claude-code
brew install anomalyco/tap/opencode

# 2. 设置环境变量(写入 ~/.zshrc)
cat <<EOF >> ~/.zshrc
export OPENAI_API_KEY="sk-livetoken-xxxxx"
export ANTHROPIC_AUTH_TOKEN="sk-livetoken-xxxxx"
export ANTHROPIC_BASE_URL="https://livetoken.top"
export LIVETOKEN_API_KEY="sk-livetoken-xxxxx"
EOF

# 3. Codex 配置
mkdir -p ~/.codex
cat <<'EOF' > ~/.codex/config.toml
model = "gpt-5.5"
model_provider = "cm"
sandbox_mode = "workspace-write"
approval_policy = "on-request"

[model_providers.cm]
name = "OpenAI"
base_url = "https://livetoken.top"
wire_api = "responses"
env_key = "OPENAI_API_KEY"
EOF

# 4. Claude Code 配置
mkdir -p ~/.claude
cat <<'EOF' > ~/.claude/settings.json
{
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "allow": ["Read", "Edit", "Bash", "Glob", "Grep"],
    "deny": ["Bash(rm -rf*)"]
  },
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-livetoken-xxxxx",
    "ANTHROPIC_BASE_URL": "https://livetoken.top",
    "API_TIMEOUT_MS": "3000000"
  }
}
EOF

# 5. opencode 配置
mkdir -p ~/.config/opencode
cat <<'EOF' > ~/.config/opencode/opencode.json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "livetoken/claude-sonnet-4",
  "provider": {
    "livetoken": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Livetoken",
      "options": {
        "baseURL": "https://livetoken.top",
        "apiKey": "{env:LIVETOKEN_API_KEY}"
      },
      "models": {
        "gpt-5.5": { "name": "GPT-5.5" },
        "claude-sonnet-4": { "name": "Claude Sonnet 4" },
        "claude-opus-4": { "name": "Claude Opus 4" },
        "gemini-2.5-pro": { "name": "Gemini 2.5 Pro" },
        "deepseek-r1": { "name": "DeepSeek R1" }
      }
    }
  }
}
EOF

source ~/.zshrc
echo "三引擎配置完成。"
echo "  codex     - GPT-5 系列"
echo "  claude    - Claude 系列"
echo "  opencode  - 多模型聚合"
```

把上面脚本保存为 `setup.sh`,改 4 处 `sk-livetoken-xxxxx` 为你自己的 token,然后:

```bash
chmod +x setup.sh
./setup.sh
```

**5 分钟,3 引擎全部就位**。

---

## FAQ

**Q1:opencode 跟 Cursor / Cline / Continue 谁强?**
**不直接对比**。Cursor 是独立 IDE;Cline / Continue 是 VS Code 扩展;opencode 是 CLI + TUI。**opencode 最大优势是开源 + 多 provider 共存**。

**Q2:opencode 支持 VS Code 扩展吗?**
有官方 VS Code 集成在迭代中(opencode.ai/docs)。**主战场是 TUI / CLI**——Cursor 同类型 IDE 集成不如它们成熟。

**Q3:75+ 模型清单在哪看?**
[opencode.ai/docs/models](https://opencode.ai/docs/models) — 完整列表。基于 AI SDK 的 75+ provider 都能用。

**Q4:opencode 比 Codex / Claude Code 慢吗?**
**不慢**。底层都是 HTTP 调用,opencode 只是多了一层适配。**性能差异 < 5%**。

**Q5:opencode 能跑本地模型吗?**
能。配 Ollama / vLLM endpoint(`http://localhost:11434/v1` 这种)即可——上面预设 3 有完整例子。

**Q6:opencode 有 sandbox 吗?**
有。`permission` 字段控制 AI 能用哪些工具,跟 Claude Code 类似。

**Q7:开源带来什么实际好处?**
**3 件事**:1) 可审计(团队 / 企业必须的);2) 可魔改(加自己需要的 provider 或工具);3) 不会因为厂商策略变化突然失效。

**Q8:走对配置的中国开发者用什么 base URL?**
**根 URL**(不带 /v1)—— 大部分国内聚合服务都按 OpenAI 兼容协议自动路由。具体看你用的服务文档。

---

*实战复盘 · opencode 配置完整教程 · AI 编程工具栈三件套收官*

*关键词:opencode、AI 编程 CLI、开源、多模型聚合、@ai-sdk/openai-compatible、自定义 provider、AI 编程工具栈*

*本文仅供学习参考 · 各服务请按其官方文档使用*
