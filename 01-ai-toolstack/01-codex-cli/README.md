# Codex CLI 配置完整教程 —— 从 0 到 1 用上自定义模型 + 第三方提供商

> **TL;DR**:Codex CLI 是 OpenAI 官方命令行 AI 编程助手。本文从安装开始,把 `~/.codex/config.toml` 每个常用参数拆清楚,**包括如何接入第三方 OpenAI 兼容提供商**(国内稳定 + 价格更低)。文末附完整配置模板 + 常见问题。

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

## 一、Codex CLI 是什么

OpenAI 官方推出的 **命令行 AI 编程助手**。简单说就是把 ChatGPT / Claude Code 那种"在终端里跑 AI 帮你写代码"的体验做成一个 CLI。

支持:

- 多模型(GPT-5 系列 / o 系列 / 自定义提供商)
- 工具使用(读文件 / 写文件 / 执行命令 / 联网搜索)
- 沙箱模式(限制 AI 能做什么)
- 多种推理强度(从 minimal 到 xhigh)
- MCP(Model Context Protocol)集成

跟 Claude Code 是同类产品。

---

## 二、安装

```bash
# Mac (Homebrew)
brew install codex

# Linux / Mac (npm)
npm install -g @openai/codex

# Windows (winget)
winget install OpenAI.Codex

# 或直接从 GitHub Release 下载二进制
# https://github.com/openai/codex/releases
```

安装完确认:

```bash
codex --version
```

---

## 三、配置文件位置

```
~/.codex/config.toml
```

**Mac / Linux**:`/Users/你/.codex/config.toml` 或 `/home/你/.codex/config.toml`

**Windows**:`C:\Users\你\.codex\config.toml`

如果文件不存在,手动创建即可。**Codex 启动时会自动读取**。

---

## 四、完整配置模板

下面这套配置覆盖**绝大部分实用场景**——开箱即用。

```toml
# ============= 模型选择 =============
model = "gpt-5.5"
model_provider = "cm"
review_model = "gpt-5.4"

# ============= 推理强度 =============
model_reasoning_effort = "high"
plan_mode_reasoning_effort = "xhigh"
model_reasoning_summary = "detailed"
model_verbosity = "medium"
model_supports_reasoning_summaries = true

# ============= 行为控制 =============
approval_policy = "on-request"
sandbox_mode = "workspace-write"
allow_login_shell = true
web_search = "live"
service_tier = "fast"
approvals_reviewer = "user"
personality = "none"

# ============= 认证存储 =============
cli_auth_credentials_store = "file"
mcp_oauth_credentials_store = "auto"

# ============= 杂项 =============
chatgpt_base_url = "https://chatgpt.com/backend-api/"
check_for_update_on_startup = true

# ============= 自定义提供商 =============
[model_providers.cm]
name = "OpenAI"
base_url = "https://livetoken.top"
wire_api = "responses"
env_key = "OPENAI_API_KEY"
```

---

## 五、配置参数详解

### 5.1 模型选择

| 参数 | 说明 |
|---|---|
| `model` | 主模型名,如 `gpt-5.5` / `gpt-5` / `o3-mini` |
| `model_provider` | 指向下面 `[model_providers.X]` 配置块的名字。这里是 `cm`,对应自定义提供商 |
| `review_model` | review / 双检场景使用的模型,可以跟主模型不同 |

**坑**:`model` 名字必须是**提供商支持的**。如果第三方只提供 `gpt-5.5` 但你写 `gpt-5.7`,会报 `model not found`。

### 5.2 推理强度(GPT-5 系列特有)

| 参数 | 取值 | 含义 |
|---|---|---|
| `model_reasoning_effort` | `minimal` / `low` / `medium` / `high` / `xhigh` | 主模型思考深度 |
| `plan_mode_reasoning_effort` | 同上 | 进入 plan 模式时的思考深度 |
| `model_reasoning_summary` | `auto` / `concise` / `detailed` | 推理摘要详细度 |
| `model_verbosity` | `low` / `medium` / `high` | 输出 verbose 程度 |
| `model_supports_reasoning_summaries` | `true` / `false` | 模型是否支持推理摘要 |

**实用建议**:
- 日常写代码:`high` 够用
- 复杂调试 / 重构:`xhigh`(慢但准)
- 简单问答:`low` 省钱

### 5.3 行为控制

| 参数 | 取值 | 含义 |
|---|---|---|
| `approval_policy` | `never` / `on-request` / `always` | AI 执行命令前是否要确认 |
| `sandbox_mode` | `read-only` / `workspace-read` / `workspace-write` | AI 能不能写文件 |
| `allow_login_shell` | `true` / `false` | 是否允许 AI 启动 login shell(读 .bashrc 等)|
| `web_search` | `live` / `disabled` | 是否允许联网搜索 |
| `service_tier` | `fast` / `standard` / `priority` | 请求优先级(影响延迟和价格) |
| `personality` | `none` / `friendly` / `professional` | AI 人设风格 |

**安全建议**:
- 不熟的项目用 `read-only` + `on-request`
- 自己的项目用 `workspace-write` + `on-request`
- **永远别配 `approval_policy = "never"`**——AI 会无询问执行任何命令

### 5.4 认证存储

| 参数 | 取值 | 含义 |
|---|---|---|
| `cli_auth_credentials_store` | `file` / `keychain` | API key 存哪 |
| `mcp_oauth_credentials_store` | `auto` / `file` / `keychain` | MCP OAuth token 存哪 |

**Mac 推荐 keychain · Linux/Windows 推荐 file**。

---

## 六、自定义提供商配置详解

这是最关键的一段——**让你可以用任何 OpenAI 兼容的第三方服务**。

```toml
[model_providers.cm]
name = "OpenAI"
base_url = "https://livetoken.top"
wire_api = "responses"
env_key = "OPENAI_API_KEY"
```

| 参数 | 说明 |
|---|---|
| 块名 `[model_providers.cm]` | `cm` 是这个提供商的别名,在 `model_provider = "cm"` 引用 |
| `name` | 显示名(影响日志,实际用的是块名)|
| `base_url` | 第三方 OpenAI 兼容端点(注意要带 `/v1`)|
| `wire_api` | `responses`(GPT-5 系列 / o 系列推理协议)/ `chat`(老 ChatCompletions)|
| `env_key` | 从哪个环境变量读 API key |

### 为什么用第三方提供商

国内开发者常见痛点:

- 官方 OpenAI 国内访问不稳定
- 大陆 IP / 大陆卡注册 / 充值繁琐
- 想同时用 GPT 和 Claude / Gemini,要分别申请账号
- 不想绑定个人 OpenAI 账号去跑生产环境

**第三方 OpenAI 兼容服务**就是解这些问题的。一行 `base_url` 切过去,Codex / Continue / Cursor / Cline 各种工具都能直接用。

### 实战:我目前用的是 livetoken.top

**不是广告**,是说一下我配置时的实际选择,以及为什么。

我跑过几家(OpenRouter / DeepBricks / livetoken / AnyRouter),最后留下来用 **livetoken.top** 是因为 4 个具体原因:

**1. 模型覆盖广**

我同时要用:
- **GPT-5 / GPT-5.5**(Codex 主力)
- **Claude Sonnet / Claude Code**(写复杂业务)
- **DeepSeek R1**(便宜跑大量任务)
- **Gemini 2.5 Pro**(长上下文)
- **o1 / o3 系列**(深度推理)

livetoken.top 一个 base_url **同时支持上面所有模型**。我以前在 OpenRouter 和 DeepBricks 之间切换,**两个 token 两个余额管两套**——挺烦的。

**2. 支持 GPT-5 的 `responses` 协议**

很多老服务只支持 `wire_api = "chat"`(ChatCompletions)。但 GPT-5 / o 系列的**推理摘要 + 工具结构**只在 `responses` 协议里完整传出来。

如果你的 base_url 不支持 responses,那么:
- 看不到 reasoning summary
- 工具调用结果可能被截断
- 复杂任务效果掉一截

我测下来 livetoken 这边 responses 协议支持得最完整——配上 `wire_api = "responses"` 直接跑。

**3. 接入简单到只改 1 个字**

```toml
# 官方 OpenAI:
base_url = "https://api.openai.com/v1"

# 切到 livetoken:
base_url = "https://livetoken.top"
```

**就这么一行**。env_key 还是 `OPENAI_API_KEY`。Codex / Cursor / Continue / Cline 全部不用改第二个字。

**4. 国内访问没掉过链**

我跑了几个月,**没遇到过 502 / timeout 系列问题**。连续推理任务、长 SSE 流、并发请求都稳。这一点对生产环境很关键。

---

> **说白了**:**模型够全 + 协议跟得上 + 接入懒得动手 + 跑得稳**,4 个条件都满足就够我用了。
> 
> 你也可以试 OpenRouter / DeepBricks 等,**接入方式完全一样,改 `base_url` 即可**。

国内常见 OpenAI 兼容聚合服务:**livetoken.top / OpenRouter / DeepBricks / AnyRouter** 等。

### `wire_api` 怎么选

| 用什么模型 | wire_api |
|---|---|
| GPT-5 / GPT-5.5 / o1 / o3 系列 | `responses` |
| GPT-4 / GPT-4o / GPT-3.5 等老模型 | `chat` |
| 部分聚合服务自己的接口 | 看文档 |

**默认 GPT-5 系列必须 `responses`**——用 `chat` 会丢推理摘要 / 工具调用结构。

---

## 七、设置 API Key

API key 不写在 `config.toml` 里(避免被误传到 Git),而是存环境变量。

### Linux / Mac

```bash
# 临时(当前 session)
export OPENAI_API_KEY="sk-xxxxx"

# 永久 — 写入 ~/.bashrc 或 ~/.zshrc
echo 'export OPENAI_API_KEY="sk-xxxxx"' >> ~/.zshrc
source ~/.zshrc
```

### Windows PowerShell

```powershell
# 临时
$env:OPENAI_API_KEY = "sk-xxxxx"

# 永久(用户级)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-xxxxx", "User")
# 重启终端生效
```

确认:

```bash
echo $OPENAI_API_KEY
# Windows: echo $env:OPENAI_API_KEY
```

---

## 八、启动 + 测试

```bash
cd 你的项目目录
codex
```

进入交互界面后试一下:

```
> 帮我看看 src/main.py 现在写了什么
> 给这个项目写一个 README
> 帮我重构 utils/helpers.py,提取重复逻辑
```

观察:
- 推理摘要是否出现(`model_reasoning_summary` 设了 `detailed` 应该有)
- 修改文件前是否问你(`approval_policy = "on-request"`)
- 写文件能不能成功(`sandbox_mode = "workspace-write"`)

---

## 九、常见问题

### Q1. 报 401 / 403

API key 没配 / 写错了 / key 余额不足。

```bash
echo $OPENAI_API_KEY
```

确认能输出 key 且不为空。再去提供商后台看余额。

### Q2. 报 `model not found`

第三方提供商不支持你写的模型名。**去提供商后台看支持模型列表**,改 `model = "..."` 即可。

### Q3. 请求 timeout / 连接失败

`base_url` 写错了——常见错误:

- 写成 `https://livetoken.top`(漏 `/v1`)
- 写成 `https://livetoken.top/`(末尾多斜杠,部分服务挑剔)
- 写成 `livetoken.top/v1`(漏 `https://`)

### Q4. 沙箱写入失败 `permission denied`

`sandbox_mode` 设成了 `read-only` 但你想让 AI 写文件 → 改成 `workspace-write`。

或者写的路径在 workspace 之外 → AI 默认只能写当前目录及子目录。

### Q5. 推理摘要不显示

GPT-5 / o 系列才有。确保:

- `wire_api = "responses"`
- `model_supports_reasoning_summaries = true`
- 用的是 GPT-5+ / o-series 模型,不是 GPT-4

### Q6. 提示 `update available`

```bash
brew upgrade codex
# 或
npm update -g @openai/codex
```

或在 config 里关:`check_for_update_on_startup = false`。

---

## 十、进阶:多提供商切换

可以在 config 里同时配置多个提供商,**通过命令行参数切换**:

```toml
[model_providers.openai]
name = "OpenAI Official"
base_url = "https://api.openai.com/v1"
wire_api = "responses"
env_key = "OPENAI_API_KEY"

[model_providers.cm]
name = "Livetoken Relay"
base_url = "https://livetoken.top"
wire_api = "responses"
env_key = "LIVETOKEN_API_KEY"

[model_providers.openrouter]
name = "OpenRouter"
base_url = "https://openrouter.ai/api/v1"
wire_api = "chat"
env_key = "OPENROUTER_API_KEY"
```

启动时切换:

```bash
codex --model-provider cm
codex --model-provider openrouter
```

---

## 十一、推荐的 3 套配置预设

### 预设 1:开发主力(GPT-5.5 + 高思考)

```toml
model = "gpt-5.5"
model_provider = "cm"
model_reasoning_effort = "high"
sandbox_mode = "workspace-write"
approval_policy = "on-request"
service_tier = "fast"
```

### 预设 2:复杂重构(xhigh + 多模型)

```toml
model = "gpt-5.5"
review_model = "gpt-5.4"
model_reasoning_effort = "xhigh"
plan_mode_reasoning_effort = "xhigh"
model_verbosity = "high"
sandbox_mode = "workspace-write"
approval_policy = "on-request"
```

### 预设 3:省钱模式(low + 只读)

```toml
model = "gpt-5"
model_reasoning_effort = "low"
sandbox_mode = "read-only"
approval_policy = "always"
service_tier = "standard"
```

---

## 十二、一句话总结

> Codex CLI 配置 = **3 件事**:
>
> 1. **`config.toml` 写明模型 / 提供商 / 行为**
> 2. **环境变量存 API key**
> 3. **`base_url` 指向支持 GPT-5 `responses` 协议的 OpenAI 兼容服务**

我自己配的是 livetoken.top,模型够全 + 跑得稳 + 接入懒得动手。**5 分钟搞定**。

---

## 附录:常用第三方 OpenAI 兼容服务对照

| 服务 | 模型覆盖 | responses 协议 | 国内访问 |
|---|---|---|---|
| **livetoken.top** | GPT-5 全系 + Claude + Gemini + DeepSeek + o 系列 | ✓ 完整 | 直连 |
| **OpenRouter** | 多家(国际化为主) | 部分 | 需中转 |
| **DeepBricks** | OpenAI 系为主 | ✓ | 直连 |
| **AnyRouter** | OpenAI 兼容 | 部分 | 直连 |

各服务接入方式一致——**改 `base_url` 和 `env_key` 即可,代码一行不动**。

我个人配 Codex 用的是 **livetoken.top**——上文第 6 章讲了选它的 4 个具体原因(模型全 + 支持 responses + 接入简单 + 跑得稳)。

如果你也是国内开发,跑 Codex / Cursor / Cline / Continue 这类需要 OpenAI 兼容端点的工具,**直接套上面的配置文件,改一下 `base_url` 和 API key 就能跑**。

---

## 遇到问题留言交流

跟着教程跑一遍配置过程,**任何环节卡住、报错、配不通**,都可以在评论区留言:

- 哪一步卡住的
- 完整报错信息
- 你用的是哪个第三方服务

我看到会回复。

也欢迎留言:
- 你目前用的是什么 base_url
- 配 Codex 之外还想配 Cursor / Cline / Continue 吗
- 想看哪些实战教程(比如 MCP 接入 / 多 agent 协作 / 沙箱安全)

**评论区见**。

---

*实战复盘 · Codex CLI 配置教程*

*关键词:Codex、Codex CLI、AI 编程助手、config.toml、OpenAI 兼容、第三方提供商、GPT-5、wire_api*

*本文仅供学习参考 · 各服务请按其官方文档使用*
