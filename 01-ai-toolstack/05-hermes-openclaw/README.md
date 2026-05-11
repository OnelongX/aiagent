# Hermes Agent + OpenClaw 配置完整教程 —— 让 AI 走出 IDE,接入你的所有聊天平台

> **TL;DR**:前 4 篇讲的 Codex / Claude Code / opencode —— **AI 在 IDE 里帮你写代码**。这一篇换一个维度:**Hermes Agent**(自我改进 AI agent)+ **OpenClaw**(自托管个人 AI 网关)= **AI 走出 IDE,接入你的微信 / Telegram / Slack / Discord / 飞书 / iMessage 等 20+ 平台**。一个 livetoken token 同时跑 5 个工具的极致工具栈。

承接 AI 编程工具栈系列前 4 篇:Codex / Codex 三端 / Claude 全家桶 / opencode。

那 4 篇全是**写代码场景**——AI 帮你在 IDE 里改代码。

**这一篇换维度**:**AI 跑在你日常用的所有聊天平台 + 自我改进 + 跨会话记忆**。

---

## 一、Hermes Agent vs OpenClaw —— 解决什么问题

| 维度 | Hermes Agent | OpenClaw |
|---|---|---|
| 厂商 | **Nous Research**(开源 AI 实验室)| openclaw.ai 开源社区 |
| 定位 | **自我改进 AI agent** | **自托管 AI 网关 / 个人助手** |
| 核心特点 | 跨会话学习 + 持久化 skills | 把 AI 接入你的所有聊天平台 |
| CLI / TUI | ✓(`hermes` / `hermes --tui`)| ✓(`openclaw onboard`)|
| 跨平台 | 20+(CLI / Telegram / Discord / Slack / WhatsApp / Signal 等)| **22+**(微信 / QQ / 飞书 / Telegram / Slack / iMessage 等)|
| 模型 | Nous Portal / OpenRouter / NIM / OpenAI / 自定义 | OpenRouter / Claude / OpenAI / 任意 OpenAI 兼容 |
| 最大特色 | **built-in learning loop**(从经验积累 skills)| **本地 gateway**(数据不出你机器)|

### 为什么需要这两个工具

前 4 篇的 IDE 工具(Codex / Claude Code / opencode)**只解决"写代码"场景**。

但实际工作中:
- 你在 **微信 / Slack** 上跟同事讨论功能 → 想让 AI 直接参与
- 你在 **iMessage / Telegram** 上想问技术问题
- 你想要 AI **跨会话记得你的偏好 / 项目背景**
- 你想要 AI **在你不在 IDE 时也能帮忙**

**Hermes + OpenClaw = 解这些场景**。

---

## 二、Hermes Agent 安装 + 配置

### 安装

**Linux / macOS / WSL2 / Android (Termux)**:

```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

**Windows (PowerShell, beta)**:

```powershell
irm https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1 | iex
```

**安装脚本自动处理依赖**:uv / Python 3.11 / Node.js / ripgrep / ffmpeg / portable Git Bash(MinGit,Windows)。

### 验证

```bash
hermes --version
```

### 首次启动

**两种模式**:

```bash
# 经典 CLI
hermes

# 现代 TUI(推荐)
hermes --tui
```

TUI 模式 UI 更好看,**推荐**。

### 模型配置

```bash
# 设置默认模型
hermes config set model anthropic/claude-opus-4.6

# 或用 OpenAI
hermes config set model openai/gpt-5.5

# 走第三方 API
hermes config set model openai/gpt-5.5
hermes config set apiBaseUrl https://livetoken.top
hermes config set apiKey sk-livetoken-xxxxx
```

⚠️ **Hermes 要求模型至少 64K 上下文**。

### 配置文件位置(注意:Hermes 用 YAML)

| 用途 | 路径 | 格式 |
|---|---|---|
| **主配置** | `~/.hermes/config.yaml` | **YAML** |
| **API key 等敏感信息** | `~/.hermes/.env` | env file |
| **Skills(学到的能力)** | `~/.hermes/skills/` | 目录 |
| **Memory(跨会话记忆)** | `~/.hermes/memory/` | 目录 |

**配置优先级**:CLI 参数 > config.yaml > .env > 内置默认值

> **API key 放 `.env`,结构化配置放 `config.yaml`**——这是官方推荐做法。

### 完整 config.yaml 示例(走 livetoken)

```yaml
# ~/.hermes/config.yaml
_config_version: 10

# ============= 主模型 =============
model:
  default: "openai/gpt-5.5"
  provider: "auto"

# 第三方 endpoint(覆盖默认 api.openai.com)
api_base_url: "https://livetoken.top"

# ============= 辅助模型 =============
auxiliary:
  vision:
    provider: "auto"
    model: ""
  web_extract:
    provider: "auto"
    model: ""
  compression:
    provider: "auto"
    model: ""

# ============= Agent 行为 =============
agent:
  max_turns: 90       # 单轮最大迭代数
  api_max_retries: 3

# ============= 语音(可选)=============
voice:
  tts:
    provider: "edge"  # edge(免费) / elevenlabs / openai / neutts(本地)
  stt:
    provider: "local" # local(faster-whisper) / groq / openai

# ============= Skills 配置 =============
skills:
  config:
    myplugin:
      path: ~/myplugin-data

# ============= MCP servers =============
mcp_servers:
  time:
    command: uvx
    args: ["mcp-server-time"]
  filesystem:
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/Projects"]

# ============= 终端 =============
terminal:
  backend: docker        # docker / daytona / local
  container_cpu: 1
  container_memory: 5120 # MB
  container_disk: 10240  # MB
```

### .env 示例(API key 放这里)

```bash
# ~/.hermes/.env
OPENAI_API_KEY=sk-livetoken-xxxxx
ANTHROPIC_API_KEY=sk-livetoken-xxxxx

# 走第三方 base URL
OPENAI_BASE_URL=https://livetoken.top
ANTHROPIC_BASE_URL=https://livetoken.top
```

### config schema 版本管理

```bash
hermes config migrate
```

新版 Hermes 出来后跑这个命令——**自动加新字段 + 升级 `_config_version`**(当前版本 10)。

### Hermes 的杀招:Self-Improving Loop

Hermes 跟其他 agent 最大区别:**built-in learning loop**。

具体来说:

| 学习机制 | 解释 |
|---|---|
| **Skill creation** | 用过的工具 / 流程 → 自动沉淀为可复用 skill |
| **Skill improvement** | 同一 skill 反复用 → 自动改进版本 |
| **Knowledge persistence** | 重要事实 → 自动记忆,跨会话保留 |
| **User model deepening** | 你的偏好 / 习惯 / 项目背景 → 越用越懂你 |

**这是 Codex / Claude Code / opencode 都没有的能力**——它们每次会话都从零开始(除了 CLAUDE.md 静态记忆)。

**Hermes 是动态学习的**。

### 跨平台接入

让 Hermes 跑在 Telegram / Discord / Slack / 等平台:

```bash
# 接 Telegram bot
hermes platforms add telegram --token xxx

# 接 Discord
hermes platforms add discord --token xxx

# 接 Slack
hermes platforms add slack --token xxx
```

**配完之后,你在 Telegram / Discord / Slack 上发消息 = 跟 Hermes 聊天**——同一个 agent / 同一份 memory / skills 跨平台。

---

## 三、OpenClaw 安装 + 配置

### 安装

```bash
# npm(推荐)
npm install -g openclaw@latest

# 或 pnpm
pnpm add -g openclaw@latest

# 或 curl 一键脚本
curl -fsSL https://openclaw.ai/install-cli.sh | bash
```

⚠️ **要求 Node 24(推荐)或 Node 22 LTS(22.16+)**。

### 引导式安装(推荐)

```bash
openclaw onboard
```

**`onboard` 命令**带你 step by step 配:
1. Gateway(本地网关进程)
2. Workspace(工作目录)
3. Channels(聊天平台)
4. Skills(技能)
5. API providers(模型提供商)

### 非交互式配置

```bash
# 查看配置
openclaw config get

# 设值
openclaw config set provider.openai.apiKey sk-xxxxx
openclaw config set provider.openai.baseURL https://livetoken.top

# 删值
openclaw config unset provider.foo
```

### 配置文件位置

```
~/.openclaw/openclaw.json
```

### openclaw.json 完整结构

OpenClaw 用 **JSON5**(支持注释 + 尾逗号)。完整 schema 包括 9 个顶级字段:

| 字段 | 用途 |
|---|---|
| `gateway` | 本地 Gateway 端口 / 鉴权 / 限流 |
| `agents` | 多 agent 定义 + defaults(workspace / 模型 / skills) |
| `models` | 模型 catalog(mode + providers 列表) |
| `providers` | API providers(OpenAI / Anthropic / Ollama / 自定义) |
| `channels` | 22+ 聊天渠道配置(微信 / Telegram / Slack 等) |
| `skills` | Skills 启用 + 自定义设置 |
| `plugins` | 插件配置(allowlist / load paths) |
| `crons` | 定时任务(scheduled tasks) |
| `subagents` | Subagent 协作配置 |

### 完整 openclaw.json 示例(走 livetoken)

```json5
{
  // ============= Gateway =============
  "gateway": {
    "port": 7878,
    "host": "127.0.0.1",
    "auth": {
      "rateLimit": {
        "attempts": 5,
        "window": 60000,    // 60 秒
        "lockout": 300000   // 5 分钟
      }
    }
  },

  // ============= 工作区 =============
  "workspace": "/Users/your-name/Documents/openclaw",

  // ============= API Providers =============
  "providers": {
    "livetoken": {
      "type": "openai-compatible",
      "baseURL": "https://livetoken.top",
      "apiKey": "sk-livetoken-xxxxx",
    },
    "ollama": {
      "type": "openai-compatible",
      "baseURL": "http://localhost:11434/v1",
      "apiKey": "ollama",
    }
  },

  // ============= 模型 catalog =============
  "models": {
    "mode": "merge",
    "providers": {
      "livetoken": {
        "models": [
          { "id": "gpt-5.5", "name": "GPT-5.5", "reasoning": true,
            "contextWindow": 200000, "maxTokens": 8192 },
          { "id": "claude-sonnet-4", "name": "Claude Sonnet 4", "reasoning": true,
            "contextWindow": 200000, "maxTokens": 8192 },
          { "id": "deepseek-r1", "name": "DeepSeek R1", "reasoning": true,
            "contextWindow": 128000, "maxTokens": 8192 }
        ]
      }
    }
  },

  // ============= Agents =============
  "agents": {
    "defaults": {
      "workspace": "~/openclaw-workspace",
      "primaryModel": "livetoken/claude-sonnet-4",
      "fallbacks": ["livetoken/gpt-5.5"],
      "modelsAllowlist": ["livetoken/*"],
      "skillsEnabled": ["filesystem", "web", "memory"],
      "sandbox": "workspace-write"
    },
    "items": [
      {
        "id": "main",
        "workspace": "~/Projects",
        "skills": ["*"],
        "groupChat": { "mention": "@openclaw" }
      }
    ]
  },

  // ============= 聊天渠道 =============
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "your-telegram-bot-token",
      "dmPolicy": "allowlist",       // pairing / allowlist / open / disabled
      "allowFrom": ["@your-username"],
      "groupPolicy": "allowlist",
      "groups": [
        { "id": "@your-group", "requireMention": true }
      ]
    },
    "wechat": {
      "enabled": true,
      "dmPolicy": "pairing"
    },
    "slack": {
      "enabled": false
    },
    "discord": {
      "enabled": false
    }
  },

  // ============= Skills =============
  "skills": {
    "filesystem": {
      "enabled": true,
      "settings": {
        "allowedPaths": ["~/Projects", "~/Documents"]
      }
    },
    "web": { "enabled": true },
    "memory": { "enabled": true }
  },

  // ============= Plugins =============
  "plugins": {
    "enabled": true,
    "allow": ["openclaw-*"],
    "deny": [],
    "loadPaths": ["~/.openclaw/plugins"],
    "entries": []
  },

  // ============= 定时任务 =============
  "crons": [
    {
      "schedule": "0 9 * * 1-5",     // 工作日早 9 点
      "agent": "main",
      "task": "总结昨天的 GitHub PR",
      "model": "livetoken/claude-sonnet-4"
    }
  ],

  // ============= Subagents =============
  "subagents": {
    "research": {
      "model": "livetoken/gpt-5",
      "skills": ["web", "memory"]
    }
  }
}
```

### 关键字段说明

#### `channels.X.dmPolicy` 取值

| 取值 | 含义 |
|---|---|
| `pairing` | 第一次对话需要配对(隐私模式) |
| `allowlist` | 只允许 `allowFrom` 列表里的用户 |
| `open` | 任何人都能 DM(慎用) |
| `disabled` | 禁用 DM(只走群聊) |

#### `channels.X.groupPolicy` 取值

| 取值 | 含义 |
|---|---|
| `open` | 任何群都能用 |
| `allowlist` | 只允许 `groups` 列表里的群 |
| `disabled` | 禁用群聊 |

#### `agents.defaults.sandbox` 取值

| 取值 | 含义 |
|---|---|
| `read-only` | 只读 |
| `workspace-read` | 工作区只读 |
| `workspace-write` | 工作区可读可写(推荐) |
| `unrestricted` | 无限制(危险) |

### 22+ 渠道接入

OpenClaw 官方支持的聊天平台:

| 平台 | 说明 |
|---|---|
| **WhatsApp** | 个人 / 商业 |
| **Telegram** | Bot 模式 |
| **Slack** | App / Bot |
| **Discord** | Bot |
| **微信(WeChat)** | 个人号 / 公众号 |
| **QQ** | Bot |
| **飞书(Feishu)** | App / Bot |
| **iMessage** | macOS Bridge |
| **Google Chat** | Webhook |
| **Microsoft Teams** | App |
| **Signal** | Bridge |
| **Matrix** | Native |
| **LINE** | Messaging API |
| **Mattermost** | Bot |
| 还有 **Nextcloud Talk / Tlon / Twitch / Zalo / IRC / WebChat / Synology / Nostr** 等 |

每个 channel 配置参考各自的 `~/.openclaw/openclaw.json` 子段。

### 启动 Gateway

```bash
openclaw start
```

Gateway 跑在 `127.0.0.1:7878`(默认),所有 channel 通过这个本地服务转发。

**重要**:**数据不出你的机器**——这是 OpenClaw 跟云端 AI 助手的根本区别。

---

## 四、第三方 API 接入 —— 两个工具都用 livetoken

### Hermes 走 livetoken

```bash
hermes config set model openai/gpt-5.5
hermes config set apiBaseUrl https://livetoken.top
hermes config set apiKey sk-livetoken-xxxxx
```

或写进 `~/.hermes/config.json`:

```json
{
  "model": "openai/gpt-5.5",
  "apiBaseUrl": "https://livetoken.top",
  "apiKey": "sk-livetoken-xxxxx"
}
```

**Hermes 也支持 Anthropic 协议** —— 可以直接走 Claude:

```bash
hermes config set model anthropic/claude-sonnet-4
hermes config set apiBaseUrl https://livetoken.top
```

### OpenClaw 走 livetoken

`~/.openclaw/openclaw.json`:

```json
{
  "providers": {
    "livetoken": {
      "type": "openai-compatible",
      "baseURL": "https://livetoken.top",
      "apiKey": "sk-livetoken-xxxxx",
      "models": ["gpt-5.5", "claude-sonnet-4", "deepseek-r1"]
    }
  },
  "defaultModel": "livetoken/claude-sonnet-4"
}
```

或用命令:

```bash
openclaw config set providers.livetoken.type openai-compatible
openclaw config set providers.livetoken.baseURL https://livetoken.top
openclaw config set providers.livetoken.apiKey sk-livetoken-xxxxx
```

### 一个 token 跑两个工具

```bash
# 共享同一个 livetoken token
export LIVETOKEN_API_KEY="sk-livetoken-xxxxx"

# Hermes
hermes config set apiKey "$LIVETOKEN_API_KEY"

# OpenClaw
openclaw config set providers.livetoken.apiKey "$LIVETOKEN_API_KEY"
```

---

## 五、5 工具栈完整方案 —— 极致工具栈

加上前 4 篇的工具,**一个 livetoken token 跑 5 个 AI 工具**:

| 工具 | 场景 | env / 配置 |
|---|---|---|
| **Codex** | IDE 里写代码(GPT)| `OPENAI_API_KEY` + 配置 toml |
| **Claude Code** | IDE 里写代码(Claude)| `ANTHROPIC_AUTH_TOKEN` + settings.json |
| **opencode** | 多模型对比 / 本地混合 | `LIVETOKEN_API_KEY` + opencode.json |
| **Hermes Agent** | 自我改进 AI agent + 跨平台 | `~/.hermes/config.json` |
| **OpenClaw** | 自托管个人 AI + 22+ 聊天平台 | `~/.openclaw/openclaw.json` |

### 完整环境变量(写进 ~/.zshrc)

```bash
export OPENAI_API_KEY="sk-livetoken-xxxxx"
export ANTHROPIC_AUTH_TOKEN="sk-livetoken-xxxxx"
export ANTHROPIC_BASE_URL="https://livetoken.top"
export LIVETOKEN_API_KEY="sk-livetoken-xxxxx"
```

**4 个 env vars + 5 套 CLI = 完整覆盖**:
- IDE 内 AI 编程(Codex / Claude Code / opencode)
- IDE 外 AI agent(Hermes 自我改进)
- 聊天平台 AI 助手(OpenClaw 22+ 渠道)

**一个 livetoken token 跑全部**。

---

## 六、3 套使用场景

### 场景 1:技术开发主力

```
IDE 里 → Codex / Claude Code / opencode
聊天平台 → 不接,专注 IDE
```

### 场景 2:技术 + 协作(团队场景)

```
IDE 里 → Claude Code(主力)
Slack / 飞书 → OpenClaw(让 AI 参与团队讨论)
Telegram → Hermes(个人 AI agent)
```

### 场景 3:全栈个人 AI(极致)

```
IDE → Codex(快速)+ Claude Code(重构)+ opencode(多模型对比)
跨平台 → Hermes(自我改进)
聊天平台 → OpenClaw(微信 / Telegram / Slack 全接)
```

**场景 3 = 5 工具全装 + 一个 livetoken token**。

---

## 七、常见问题

### Q1. Hermes 64K 上下文要求,哪些模型够?

GPT-4 Turbo+ / GPT-5 系列 / Claude 3+ / Gemini 1.5+ / DeepSeek R1 等,**livetoken 上的主流模型都够**。

### Q2. OpenClaw Gateway 默认端口被占用怎么办

```bash
openclaw config set gateway.port 8080
openclaw restart
```

### Q3. Hermes 学到的 skills 在哪看

```
~/.hermes/skills/
```

每个 skill 一个文件,可以手动编辑 / 删除。

### Q4. OpenClaw 的微信 channel 真能用?

依赖第三方 bridge(因为微信官方不开放 bot API),**需要单独配 wechat-bridge**。OpenClaw docs 有具体步骤。

### Q5. 这两个工具会不会太重 / 太复杂

**不一定**。**单纯当 CLI agent 用就够**——不一定接 22+ 渠道。最简使用:
- Hermes:`hermes --tui` 当 Claude Code 替代
- OpenClaw:`openclaw onboard` 配最简版,只用本地 CLI

### Q6. Self-improving 真的有用吗

3-5 次会话之后开始有感觉。**Hermes 会记住**:
- 你常用的项目结构
- 你偏好的代码风格
- 你常用的命令 / 工具
- 你之前问过的问题 + 答案

第 10 次会话起 = **AI 像跟你工作很久的同事一样懂你**。

### Q7. 5 工具栈会不会太多?用不过来?

**不会**。各自场景不一样,**不冲突**。我自己的实际使用频率:
- Codex / Claude Code:**每天**(IDE 主力)
- opencode:**每周几次**(多模型对比 / 复杂任务)
- Hermes:**每周几次**(长期记忆任务)
- OpenClaw:**手机端 / 通勤路上**(把 AI 带在身边)

---

## 八、留言钩子

跟着教程跑一遍配置过程,**任何环节卡住、报错、配不通**,都可以在评论区留言:

- 哪一步卡住的
- 完整报错信息
- 你用的是哪个第三方服务

我看到会回复。

也欢迎留言:
- Hermes / OpenClaw 哪个更让你心动
- 你最想接入哪个聊天平台
- 想看哪些进阶教程(Hermes skills 自定义 / OpenClaw 多 agent / 微信 bridge 部署)

**评论区见**。

---

## 升华

> **AI 工具栈 5 件套**:
>
> Codex + Claude Code + opencode + **Hermes** + **OpenClaw**
>
> = IDE 写代码 + IDE 外 agent + 22+ 聊天平台
>
> **一个 livetoken token · 跑全部**

5 工具 + 1 token = 你的 AI 工作流应该是这样:

| 时间 | 工具 |
|---|---|
| 在 IDE 写代码 | Codex / Claude Code(看任务复杂度) |
| 跑 plan 模式 | Claude Code(Subagent) |
| 多模型对比 | opencode |
| 长期任务 / 跨会话记忆 | **Hermes** |
| 通勤 / 手机端 / 跨平台 | **OpenClaw** |

**5 个工具一起用 ≠ 复杂 = 各司其职**。

---

## 附录:5 工具栈一键配置脚本(终极版)

```bash
#!/bin/bash
# AI 工具栈 5 件套一键配置

# 1. 安装 5 个工具
npm install -g @openai/codex
npm install -g @anthropic-ai/claude-code
brew install anomalyco/tap/opencode
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
npm install -g openclaw@latest

# 2. 设置环境变量
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
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-livetoken-xxxxx",
    "ANTHROPIC_BASE_URL": "https://livetoken.top"
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
        "claude-sonnet-4": { "name": "Claude Sonnet 4" }
      }
    }
  }
}
EOF

# 6. Hermes 配置
hermes config set model anthropic/claude-sonnet-4
hermes config set apiBaseUrl https://livetoken.top
hermes config set apiKey sk-livetoken-xxxxx

# 7. OpenClaw 配置(运行 onboard 引导)
echo "运行 'openclaw onboard' 完成 OpenClaw 配置"

source ~/.zshrc
echo "5 工具栈配置完成。"
echo "  codex     - GPT-5"
echo "  claude    - Claude"
echo "  opencode  - 多模型聚合"
echo "  hermes    - 自我改进 AI agent"
echo "  openclaw  - 跨 22+ 聊天平台"
```

---

## FAQ

**Q1:Hermes 跟 Claude Code 谁更强?**
**功能对标但定位不同**。Hermes 强在**自我改进 + 跨会话记忆 + 跨平台**。Claude Code 强在**IDE 集成 + Subagent + Plan 模式**。**两个都装,各司其职**。

**Q2:OpenClaw 自托管会不会很费机器?**
不会。Gateway 进程占内存 < 100MB,大部分时间空闲。**主要消耗在 AI 调用本身**(走第三方 API 不耗本地)。

**Q3:Hermes 学到的 skills 能跨机器同步吗?**
能。`~/.hermes/` 目录可以用 dotfiles / git 同步。或者用 Hermes 的 cloud sync(Pro 计划)。

**Q4:OpenClaw 的 22+ 渠道我都要装吗?**
不需要。**按需启用**。我个人只接 Telegram + 微信 + Slack 3 个就够。

**Q5:这 5 个工具一起用会不会冲突?**
**不会**。各自配置文件路径独立(~/.codex / ~/.claude / ~/.config/opencode / ~/.hermes / ~/.openclaw),env vars 不冲突。

**Q6:有没有更轻量的方案?**
有。**新手建议**:Codex(IDE 主力)+ Hermes(自我改进 agent)。两个工具就能覆盖 80% 场景。**5 工具栈适合重度用户**。

**Q7:Hermes / OpenClaw 适合企业部署吗?**
适合。**Hermes**:每个开发者本地一份,skills 跟 dotfiles 一起同步。**OpenClaw**:本地 gateway + 接团队 Slack / 飞书 → 整个团队共用。

**Q8:走对配置的国内开发者用什么 base URL?**
**根 URL**(不带 /v1)—— `https://livetoken.top`。具体看你用的服务文档。

---

*实战复盘 · Hermes Agent + OpenClaw 配置教程 · AI 工具栈 5 件套*

*关键词:Hermes Agent、OpenClaw、AI agent、自我改进 AI、自托管网关、聊天平台 AI、Nous Research、AI 工具栈*

*本文仅供学习参考 · 各服务请按其官方文档使用*
