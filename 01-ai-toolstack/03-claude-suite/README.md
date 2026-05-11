# Claude 桌面 app + VS Code 扩展 完整配置教程 —— 一个 API key 跑遍 Claude 全家桶

> **TL;DR**:Claude 不只是 claude.ai 网页版。Anthropic 推了 **2 个产品 / 3 个端**:**Claude Desktop App**(聊天 + MCP 工具调用)+ **Claude Code**(CLI + VS Code 扩展,AI 编程)。本文从安装到第三方接入全拆。**关键杀招**:一个 token 同时跑 Codex 和 Claude Code,**国内 AI 编程工作流双引擎**。


<div align="center">

<a href="https://github.com/OnelongX/aiagent">
<img src="../../assets/wechat-qrcode.png" width="320" alt="公众号:IamOnelong" />
</a>

📖 **本文同步发布于公众号「实战复盘」** · 微信号:`IamOnelong`
🌐 [完整代码仓库 · github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型:[docs/livetoken.md](../../docs/livetoken.md)

</div>

---

承接系列 1《Codex CLI 配置完整教程》+ 系列 2《Codex 三端通用配置》。

Codex 那两篇讲了 OpenAI 这边的配置。**这一篇讲 Anthropic 这边**——Claude Desktop + Claude Code。

---

## 一、Claude 全家桶 —— 1 个统一应用 + CLI + 扩展

很多教程说"Claude Desktop 是一个产品 / Claude Code 是另一个产品"——**这个说法已经过期**。

**事实(2026 最新)**:**Claude Desktop 现在是 3 标签页统一应用**:

| 标签页 | 用途 | 引擎 |
|---|---|---|
| **Chat** | 聊天 + MCP 工具调用 + 文件分析 | 账号 / API |
| **Cowork** | Dispatch + 长任务 + 多 agent 协作 | Claude Sonnet / Opus |
| **Code** | AI 编程(等同 Claude Code) | **跟 CLI 同引擎** |

加上独立的 CLI 和 VS Code 扩展,**完整版图是**:

| 形态 | 是什么 |
|---|---|
| **Claude Desktop App · Chat 标签** | 聊天 / MCP / 文件分析 |
| **Claude Desktop App · Cowork 标签** | Dispatch 长任务(Pro / Max 才能用) |
| **Claude Desktop App · Code 标签** | **= Claude Code Desktop GUI** |
| **Claude Code CLI** | 终端命令行 |
| **Claude Code VS Code 扩展** | IDE 内嵌 |

**关键认知(很多文章漏讲)**:

> **Claude Desktop 的 Code 标签 + Claude Code CLI + VS Code 扩展 — 3 个端共享同一份配置**
>
> 共享的文件:`~/.claude/settings.json` + `~/.claude.json` + `CLAUDE.md`

**这意味着**:你在 CLI 里配的 `ANTHROPIC_BASE_URL`,**Desktop 的 Code 标签里也生效**。

引用官方文档:

> "Desktop and CLI read the same configuration files, so your setup carries over."

---

## 二、Claude Desktop 配置

### 安装

**官网下载**:[claude.ai/download](https://claude.ai/download)

支持:
- macOS(Intel + Apple Silicon 通用)
- Windows(x64 + ARM64)
- ⚠️ **Linux 暂不提供 Desktop**(用 CLI 即可)

### 3 个标签页配置思路

| 标签页 | 配置入口 |
|---|---|
| **Chat** | `claude_desktop_config.json`(MCP servers)+ 设置面板登录 |
| **Cowork** | 跟 Chat 共用 + Pro/Max 订阅检查 |
| **Code** | **跟 CLI 共享 `~/.claude/settings.json` + `~/.claude.json`** |

### Chat 标签:MCP 配置(让聊天升级为工具型 AI)

Chat 标签默认用账号登录,**核心配置点是 MCP servers**。

#### 配置文件位置

| 平台 | 路径 |
|---|---|
| Mac | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**注意**:这份文件是给 **Chat 标签的 MCP servers** 用的——**Code 标签不读这份文件**(Code 标签的 MCP 配在 `~/.claude.json` 或项目的 `.mcp.json`)。

### Code 标签:跟 CLI 完全共享 settings.json

**这是很多文章漏讲的关键点**:

> Claude Desktop 的 **Code 标签** 跟 Claude Code CLI **共享 `~/.claude/settings.json`**
>
> 你在 settings.json 的 `env` 块里配的 `ANTHROPIC_BASE_URL` / `ANTHROPIC_AUTH_TOKEN` —— **Code 标签也读到,也生效**。

也就是说,**第三方 API 接入对 Code 标签同样有效**。后面第三章会讲完整的 settings.json 配置——**那一份 settings 同时管 CLI / VS Code 扩展 / Desktop Code 标签 3 个端**。

---

### 🔥 官方方案:Developer Mode 把整个 Desktop 切到第三方

更猛的方案 —— **Anthropic 在最新版 Desktop 加了官方 GUI 第三方接入**。

**这个面板把 Cowork + Code + Projects + Artifacts 整个应用切到第三方 API**(Chat 标签除外)。

#### Step 1:启用 Developer Mode

| 平台 | 步骤 |
|---|---|
| **macOS** | 菜单栏 → **Help** → **Troubleshooting** → **Enable Developer Mode** |
| **Windows** | 左上角应用菜单(☰)→ **Help** → **Troubleshooting** → **Enable Developer Mode** |

启用后,**菜单栏会出现 Developer 菜单**。

#### Step 2:打开第三方推理面板

```
Developer → Configure third-party inference
```

#### Step 3:配置面板(7 个 sidebar 区)

按顺序配:

| 区 | 内容 |
|---|---|
| **Connection** | Gateway 类型选 **Gateway (Anthropic-compatible)** + Gateway base URL + Gateway API key |
| **Identity & Models** | 模型映射 / identity 配置 |
| **Sandbox & workspace** | 工作区 / 沙箱设置 |
| **Connectors & extensions** | MCP / 扩展 |
| ... | 其他高级配置 |

**Connection 区 3 个核心字段**:

| 字段 | 说明 |
|---|---|
| **Gateway type** | 选 **Gateway (Anthropic-compatible)** |
| **Gateway base URL** | 必须 `https://` 开头(HTTP 不接受) |
| **Gateway API key** | 第三方 token |

例子(配 livetoken):

```
Gateway type:     Gateway (Anthropic-compatible)
Gateway base URL: https://livetoken.top
Gateway API key:  sk-livetoken-xxxxx
```

#### Step 4:Apply locally

点 **Apply locally** → **Claude Desktop 重启进入 3P 模式**(third-party mode)。

#### 网关要求(给 livetoken 等聚合服务的开发者参考)

Gateway 必须满足:
- 暴露 `/v1/messages` endpoint
- 转发 `anthropic-beta` header
- 转发 `anthropic-version` header
- 兼容 Anthropic Messages API(**不是 OpenAI Chat Completions**)

⚠️ **只支持 OpenAI 协议(/v1/chat/completions)的服务在这里跑不通**——必须 Anthropic Messages 协议。

livetoken 这边**两个协议都支持**,所以直接配。

#### 进入 3P 模式后:哪些功能可用 / 不可用

| 功能 | 3P 模式下 |
|---|---|
| **Chat 标签**(原生聊天) | ❌ 不再支持 |
| **Cowork**(Dispatch / 长任务) | ✓ 支持 |
| **Code**(AI 编程) | ✓ 支持 |
| **Projects**(项目分享) | ✓ 支持 |
| **Artifacts**(代码 / 文档生成) | ✓ 支持 |
| **MCP servers** | ✓ 支持 |

也就是 —— **进入 3P 模式 = 用第三方 API 跑除 Chat 之外的所有 Desktop 功能**。

如果你**重点用 Cowork / Code / Projects**(开发者大概率是),3P 模式就是为你设计的。

⚠️ **重度用 Chat 标签的用户**:别开 3P 模式,Chat 标签会失效。

#### 配置存哪

3P 配置 **加密存在本地机器**——**不发回 Anthropic**。

企业 / 团队部署时可通过 MDM 推送,首次启动自动加载。

---

### 完整 JSON 配置参考(企业 MDM / 高级用户)

GUI 面板填的所有字段,**底层都对应 JSON keys**——以下是完整 spec(来自 Anthropic 官方 MDM 配置文档):

#### 配置文件 / 注册表位置

| 平台 | 部署方式 | 路径 |
|---|---|---|
| **macOS** | `.mobileconfig` 通过 MDM(Jamf / Kandji / Mosyle / Intune)| Domain: `com.anthropic.claudefordesktop` |
| **Windows** | `.reg` 通过组策略 / Intune | Registry: `HKCU\SOFTWARE\Policies\Claude` |
| **macOS plugin 目录** | 本地插件 | `/Library/Application Support/Claude/org-plugins/` |
| **Windows plugin 目录** | 本地插件 | `C:\ProgramData\Claude\org-plugins\` |

也就是说 **实际 JSON 配置不是直接保存为文件,而是**:
- macOS:写进系统 plist preferences(`com.anthropic.claudefordesktop` domain)
- Windows:写进注册表

**单机 Developer Mode** 配置:GUI 面板填完后**加密存本地**(看不到原始 JSON 文件)。

**企业 MDM 部署**:JSON keys 直接打包成 `.mobileconfig`(Mac)或 `.reg`(Windows)推送下发。

#### 核心字段(Connection 区)

| Key | 类型 | 说明 | 必填 |
|---|---|---|---|
| `inferenceProvider` | string | `gateway` / `bedrock` / `vertex` / `foundry` | ✓ |
| `inferenceGatewayBaseUrl` | string | Gateway endpoint URL(必须 `https://`)| Gateway 模式必填 |
| `inferenceGatewayApiKey` | string | Gateway API token | Gateway 模式必填 |
| `inferenceGatewayAuthScheme` | string | `auto` / `x-api-key` / `bearer` | 否(默认 auto)|
| `inferenceGatewayHeaders` | JSON array | 自定义 HTTP headers | 否 |
| `inferenceModels` | JSON array | 模型 ID 列表 | Vertex / Bedrock / Foundry 必填 |

#### Vertex AI 字段(走 Google Cloud)

| Key | 说明 |
|---|---|
| `inferenceVertexProjectId` | GCP 项目 ID |
| `inferenceVertexRegion` | GCP 区域 |
| `inferenceVertexCredentialsFile` | service-account JSON 绝对路径 |
| `inferenceVertexBaseUrl` | 自定义 endpoint(PSC 支持) |
| `inferenceVertexOAuthClientId` / `inferenceVertexOAuthClientSecret` | OAuth 交互登录 |
| `inferenceVertexOAuthScopes` | 权限 scopes |

#### Bedrock 字段(走 AWS)

| Key | 说明 |
|---|---|
| `inferenceBedrockRegion` | AWS region |
| `inferenceBedrockBearerToken` | AWS token |
| `inferenceBedrockBaseUrl` | 自定义 endpoint(VPC / gateway) |
| `inferenceBedrockProfile` | AWS named profile |
| `inferenceBedrockAwsDir` | AWS credentials 目录 |

#### Azure Foundry 字段

| Key | 说明 |
|---|---|
| `inferenceFoundryResource` | 资源名 |
| `inferenceFoundryApiKey` | API key |

#### 部署 / 更新控制

| Key | 类型 | 说明 |
|---|---|---|
| `deploymentOrganizationUuid` | string | 组织唯一标识 |
| `autoUpdaterEnforcementHours` | integer | 强制更新截止时间(小时)|
| `disableAutoUpdates` | boolean | 禁用自动更新 |

#### MCP 与扩展

| Key | 类型 | 说明 |
|---|---|---|
| `isClaudeCodeForDesktopEnabled` | boolean | 是否启用 Code 标签 |
| `isLocalDevMcpEnabled` | boolean | 允许自定义 MCP servers |
| `isDesktopExtensionEnabled` | boolean | 允许本地扩展 |
| `isDesktopExtensionSignatureRequired` | boolean | 强制扩展签名 |
| `managedMcpServers` | JSON array | 远程 MCP 配置 |
| `disabledBuiltinTools` | JSON array | 禁用的内置工具 |

#### 工作区 + 使用配额

| Key | 类型 | 说明 |
|---|---|---|
| `allowedWorkspaceFolders` | JSON array | 允许的工作目录 |
| `coworkEgressAllowedHosts` | JSON array | Cowork 可访问的主机 |
| `inferenceMaxTokensPerWindow` | integer | Token 用量上限 |
| `inferenceTokenWindowHours` | integer | Token 窗口时长(小时)|

#### 遥测控制

| Key | 类型 | 说明 |
|---|---|---|
| `disableEssentialTelemetry` | boolean | 禁用崩溃报告 |
| `disableNonessentialTelemetry` | boolean | 禁用使用分析 |
| `otlpEndpoint` | string | OpenTelemetry collector URL |

---

### 实战 JSON 配置(走 livetoken)

**最简版** —— 用 livetoken 作为 Anthropic-compatible gateway:

```json
{
  "inferenceProvider": "gateway",
  "inferenceGatewayBaseUrl": "https://livetoken.top",
  "inferenceGatewayApiKey": "sk-livetoken-xxxxx",
  "inferenceGatewayAuthScheme": "auto",
  "isClaudeCodeForDesktopEnabled": true,
  "isLocalDevMcpEnabled": true
}
```

**完整版** —— 加上模型限定 + MCP + 工作区控制:

```json
{
  "inferenceProvider": "gateway",
  "inferenceGatewayBaseUrl": "https://livetoken.top",
  "inferenceGatewayApiKey": "sk-livetoken-xxxxx",
  "inferenceGatewayAuthScheme": "auto",
  "inferenceModels": [
    "claude-sonnet-4",
    "claude-opus-4",
    "claude-haiku-4"
  ],
  "isClaudeCodeForDesktopEnabled": true,
  "isLocalDevMcpEnabled": true,
  "isDesktopExtensionEnabled": true,
  "managedMcpServers": [
    {
      "name": "filesystem",
      "url": "https://your-mcp-server.example.com/filesystem"
    }
  ],
  "allowedWorkspaceFolders": [
    "/Users/your-name/Projects",
    "/Users/your-name/Documents"
  ],
  "inferenceMaxTokensPerWindow": 10000000,
  "inferenceTokenWindowHours": 24
}
```

### 部署流程(企业 / 团队)

1. **本机配通**:Developer Mode → Configure third-party inference → 填好字段 → **Export** 按钮下载 `.mobileconfig`(Mac)或 `.reg`(Windows)
2. **MDM 推送**:把导出文件推到团队成员机器
3. **首次启动**:自动加载,**用户不用手动配**
4. **配置变更**:再 Export 一次新文件,MDM 覆盖

**单机用户**直接走 GUI 面板就够,**不需要碰 JSON**。

JSON 这一段主要是给:
- 团队 / 企业管理员
- 想完整理解配置结构的高级用户
- 第三方聚合服务(参考接入规范)

---

---

### Cowork 标签

Cowork 是 Pro / Max 计划的 Dispatch 长任务功能。

- **默认 1P 模式**:走 Anthropic 账号订阅 quota
- **3P 模式下**:跟着切到第三方 gateway

**结论**:Cowork 也是支持第三方 API 的,只要走 Developer Mode 切换。

### MCP 配置(Claude Desktop 的真正强项)

**MCP** = Model Context Protocol。Anthropic 开源的协议,让 AI 可以调用各种工具(读文件 / 操作浏览器 / 查数据库 / GitHub 等)。

`claude_desktop_config.json` 示例:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/your-name/Documents",
        "/Users/your-name/Projects"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxxxx"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@executeautomation/playwright-mcp-server"]
    }
  }
}
```

改完保存,**重启 Claude Desktop** —— 启动后就能在对话框里直接让 AI 操作文件 / GitHub / 浏览器。

### MCP 必装清单(我自己跑下来最有用的 4 个)

| MCP server | 用途 | 安装 |
|---|---|---|
| **Filesystem** | 让 Claude 读写本地文件 | `npx @modelcontextprotocol/server-filesystem` |
| **GitHub** | 让 Claude 操作 GitHub repo / PR / issue | `npx @modelcontextprotocol/server-github` |
| **Playwright** | 让 Claude 操作浏览器 | `npx @executeautomation/playwright-mcp-server` |
| **SQLite** | 让 Claude 查询本地数据库 | `npx @modelcontextprotocol/server-sqlite` |

**装上这 4 个,Claude Desktop 才发挥真正威力**——不只是聊天,是工具型 AI。

---

## 三、Claude Code 配置(CLI + VS Code 扩展)

### Claude Code 是什么

Anthropic 官方推的 **AI 编程工具**。功能上跟 Codex 对标:
- 终端里跑(CLI)
- VS Code 扩展(IDE 内嵌)
- 支持工具调用 / 沙箱 / 自动化任务

### 安装

```bash
# CLI(全平台通用)
npm install -g @anthropic-ai/claude-code

# 或用 Homebrew (Mac)
brew install claude-code
```

确认:

```bash
claude --version
```

### VS Code 扩展安装

VS Code Marketplace 搜 **Claude Code** → 安装。

**注意**:VS Code 扩展**内部调用 CLI**——所以 CLI 必须先装好,扩展才能跑。

### 配置文件位置

| 用途 | 路径 |
|---|---|
| 全局设置 | `~/.claude/settings.json` |
| 项目记忆 | `<project>/.claude/CLAUDE.md` |
| 全局记忆 | `~/.claude/CLAUDE.md` |

`settings.json` 示例(走第三方 API):

```json
{
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "allow": ["Read", "Edit", "Bash"],
    "deny": []
  },
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-xxxxx",
    "ANTHROPIC_BASE_URL": "https://livetoken.top",
    "API_TIMEOUT_MS": "3000000"
  }
}
```

**3 个关键字段**:

| 字段 | 说明 |
|---|---|
| `ANTHROPIC_AUTH_TOKEN` | 你的 API key(走第三方时填第三方的 token)|
| `ANTHROPIC_BASE_URL` | 第三方 endpoint **根 URL,不带 /v1**——Claude Code 自动拼 `/v1/messages` |
| `API_TIMEOUT_MS` | 超时时间(可选,长任务推荐 3000000 即 50 分钟)|

**注意是 `ANTHROPIC_AUTH_TOKEN` 不是 `ANTHROPIC_API_KEY`** —— 这是写在 settings.json 的 `env` 块里时的标准字段名。如果用 shell 环境变量,两个名字都能识别。

### CLAUDE.md(项目记忆,Claude Code 独有)

放在项目根目录的 `.claude/CLAUDE.md` 文件,**Claude Code 启动时自动读取**——可以写项目背景 / 代码风格 / 常用命令 / 测试要求。

```markdown
# 项目背景
这是一个 Next.js + TypeScript 的 SaaS 应用,使用 Tailwind + shadcn/ui。

# 代码风格
- 组件用 PascalCase
- 工具函数用 camelCase
- 不要写 default export

# 常用命令
- 启动开发: pnpm dev
- 跑测试: pnpm test
- 构建: pnpm build

# 测试要求
所有新组件必须有对应的 .test.tsx 文件。
```

**这个文件 = AI 的"项目入门手册"**。配好之后,Claude Code 不会再问"项目是什么 stack"。

### CLI vs VS Code 扩展 共享认证

跟 Codex 类似——**Claude Code CLI 登录后,VS Code 扩展自动读取认证**,不用再登一次。

---

## 四、第三方 API 接入(对 Code 标签 / CLI / VS Code 扩展都有效)

**关键**:第三方 API 接入对 3 个端都有效——**因为它们共享 `~/.claude/settings.json`**:

- ✓ Claude Desktop **Code 标签**
- ✓ Claude Code **CLI**
- ✓ Claude Code **VS Code 扩展**

**配一次 settings.json,3 个端同时切到第三方**。

**不影响**:
- ✗ Claude Desktop **Chat 标签**(走 Anthropic 账号)
- ✗ Claude Desktop **Cowork 标签**(走 Anthropic 账号)

### 为什么要走第三方

跟 Codex 一样的痛点:

- Anthropic 国内访问不稳定
- API key 充值要美元卡
- 想同时用 GPT 和 Claude 要分别申请账号
- 想跑生产环境不绑个人账号

**解决方案**:第三方 Anthropic 兼容服务。

### 2 种配置方式 · 选一个就行

**方式 A:写进 `~/.claude/settings.json`**(推荐)

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "sk-xxxxx",
    "ANTHROPIC_BASE_URL": "https://livetoken.top",
    "API_TIMEOUT_MS": "3000000"
  }
}
```

**方式 B:写进 shell 环境变量**

```bash
# 临时
export ANTHROPIC_AUTH_TOKEN="sk-xxxxx"
export ANTHROPIC_BASE_URL="https://livetoken.top"

# 永久写入 ~/.zshrc 或 ~/.bashrc
echo 'export ANTHROPIC_AUTH_TOKEN="sk-xxxxx"' >> ~/.zshrc
echo 'export ANTHROPIC_BASE_URL="https://livetoken.top"' >> ~/.zshrc
source ~/.zshrc
```

**两种都能用 · 我推荐方式 A**——所有 Claude Code 配置集中在 `~/.claude/settings.json` 一份文件里,容易维护。

### 3 个常见坑

**坑 1:base_url 不要带 /v1**

```bash
# ✓ 对
ANTHROPIC_BASE_URL="https://livetoken.top"

# ✗ 错
ANTHROPIC_BASE_URL="https://livetoken.top/v1"
```

Claude Code **自动拼 `/v1/messages`** —— 你写 `/v1` 反而会变成 `/v1/v1/messages`。

**坑 2:末尾别加斜杠**

```bash
# ✓ 对
ANTHROPIC_BASE_URL="https://livetoken.top"

# ⚠ 部分代理服务挑剔斜杠
ANTHROPIC_BASE_URL="https://livetoken.top/"
```

如果配完报 404,先试一下去掉末尾斜杠。

**坑 3:`ANTHROPIC_AUTH_TOKEN` vs `ANTHROPIC_API_KEY`**

- shell 环境变量:**两个都能识别**
- `~/.claude/settings.json` 的 `env` 块:**用 `ANTHROPIC_AUTH_TOKEN`**(标准字段)

### 实战:我自己用的是 livetoken.top

> **不是广告**,是说一下我配置时的实际选择。

我配 Codex 的时候选了 livetoken.top(参考前两篇)。配 Claude Code 时**继续用同一个 token**——4 个具体原因:

**1. 同一个聚合服务支持双协议**

livetoken 同时提供:
- OpenAI 兼容协议 → Codex 用 `base_url = "https://livetoken.top"`
- Anthropic 兼容协议 → Claude Code 用 `ANTHROPIC_BASE_URL="https://livetoken.top"`

**两个协议同一个根 URL · 两套用法**——不用维护 OpenAI / Anthropic 两套账号。

**2. Claude Code 全模型支持**

我用 Claude Code 跑过:
- `claude-sonnet-4`
- `claude-opus-4`
- `claude-haiku-4`
- `claude-sonnet-4.5`(发布即支持)

livetoken 这边**新模型出来很快就接入**——Anthropic 发布当天 / 第二天就能调到。

**3. CLAUDE.md / Subagent / Plan 模式 全部正常**

Claude Code 比 Codex 有几个特色功能:
- **CLAUDE.md 项目记忆**(刚才讲过)
- **Subagent**(分裂出多个专项 agent 协作)
- **Plan 模式**(计划任务 + 自动执行)

第三方代理服务**经常会丢这些功能的语义**——但 livetoken 这边**全部正常**。

**4. 同一个 token 跑两套助手**

最实用的一点:

```bash
# 一个 token 同时配 Codex + Claude Code
export OPENAI_API_KEY="sk-livetoken-xxxxx"      # Codex 用
export ANTHROPIC_AUTH_TOKEN="sk-livetoken-xxxxx" # Claude Code 用(同一个 token!)
export ANTHROPIC_BASE_URL="https://livetoken.top"
```

**Codex 跑 GPT-5 + Claude Code 跑 Claude Sonnet,两套助手共享同一个余额**。

---

## 五、一个 token 跑 Codex + Claude Code 的双端方案

> 这是国内 AI 编程工作流的**双引擎方案**。

### 为什么要双引擎

不同任务有不同的最佳模型:

| 任务 | 我倾向用 |
|---|---|
| 重构 / 大型代码改写 | **Claude Sonnet 4** |
| 完整的 plan 模式自动化 | **Claude + Subagent** |
| 单点修改 / 快速 review | **GPT-5.5** |
| 长上下文理解 | **Claude(200K)** |
| 推理任务 | **GPT-5 / o1** |

**单一模型不可能在所有任务都最优**。双引擎 = 任意切换。

### 双引擎完整配置

**步骤 1:Codex 配置**(参考系列 1)

`~/.codex/config.toml`:

```toml
model = "gpt-5.5"
model_provider = "cm"
sandbox_mode = "workspace-write"
approval_policy = "on-request"

[model_providers.cm]
name = "OpenAI"
base_url = "https://livetoken.top"
wire_api = "responses"
env_key = "OPENAI_API_KEY"
```

环境变量:`export OPENAI_API_KEY="sk-livetoken-xxxxx"`

**步骤 2:Claude Code 配置**

`~/.claude/settings.json`:

```json
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
```

**步骤 3:验证**

```bash
codex   # 测试 Codex,跑 GPT-5.5
claude  # 测试 Claude Code,跑 Claude Sonnet
```

**两个 CLI 都能起来 = 双引擎配通了**。

**一个 livetoken token 同时填进去**——Codex 那边走 OpenAI 协议,Claude Code 这边走 Anthropic 协议,**livetoken 后端自动路由**。

---

## 六、MCP 必装清单(Claude Desktop 主战场)

回到 Claude Desktop。装好之后**必装 MCP servers** 让它从聊天升级到工具:

### 必装 4 件套

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/你/Documents",
        "/Users/你/Projects"
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_xxx"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["@executeautomation/playwright-mcp-server"]
    },
    "sqlite": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-sqlite",
        "--db-path",
        "/path/to/your.db"
      ]
    }
  }
}
```

### 进阶推荐

| MCP server | 用途 |
|---|---|
| **Slack** | 让 Claude 发 Slack 消息 / 读频道 |
| **Linear** | Issue / PR / Sprint 管理 |
| **Brave Search** | 让 Claude 联网搜索(免费) |
| **Memory** | 让 Claude 跨对话记住事情 |

---

## 七、3 套预设(复制即用)

### 预设 1:开发主力

`~/.claude/settings.json`:

```json
{
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "allow": ["Read", "Edit", "Bash", "Glob", "Grep"],
    "deny": ["Bash(rm -rf*)"]
  }
}
```

环境变量:`ANTHROPIC_BASE_URL=https://livetoken.top`

### 预设 2:Plan + Subagent

```json
{
  "model": "claude-opus-4",
  "permissions": {
    "allow": ["*"],
    "deny": ["Bash(rm -rf*)", "Bash(curl*)"]
  }
}
```

适合复杂任务 + Plan 模式 + Subagent 协作。

### 预设 3:团队部署(只读 + 严格审批)

```json
{
  "model": "claude-sonnet-4-20250514",
  "permissions": {
    "allow": ["Read", "Glob", "Grep"],
    "deny": ["Edit", "Write", "Bash"]
  }
}
```

适合代码 review / 团队场景 / 不熟项目。

---

## 八、常见问题

### Q1. Claude Desktop 启动后 MCP 不显示

`claude_desktop_config.json` 写错了 / 或者路径不对。

**调试方法**:
1. 打开 Claude Desktop → Settings → Developer → Open MCP Logs
2. 看启动日志,定位哪个 MCP server 没启动

### Q2. Claude Code 报 401

`ANTHROPIC_API_KEY` 没配 / 或者 `ANTHROPIC_BASE_URL` 写错了。

```bash
echo $ANTHROPIC_API_KEY
echo $ANTHROPIC_BASE_URL
```

确认能输出且不为空。

### Q3. ANTHROPIC_BASE_URL 末尾要不要带 /v1

**不需要**。Anthropic 官方协议路径是 `/v1/messages`,但只配 base_url 到根路径(`https://livetoken.top`),Claude Code 会自动拼 `/v1/messages`。

跟 OpenAI 那边配 `https://xxx.com/v1` 不一样——这是协议设计差异。

### Q4. CLAUDE.md 和 settings.json 哪个优先

`settings.json` 管行为(模型 / 权限 / 环境变量)。
`CLAUDE.md` 管内容(项目背景 / 代码规范 / 常用命令)。

**两个文件不冲突**,Claude Code 会同时读。

### Q5. Claude Code VS Code 扩展不工作

99% 是因为 CLI 没装好。VS Code 扩展只是 GUI 包装。

```bash
which claude   # 应该能输出路径
claude --version   # 应该能输出版本号
```

### Q6. Subagent 调用第三方 API 会失败吗

不会。**Subagent 还是走 ANTHROPIC_BASE_URL**——只要主 agent 跑通,Subagent 也跑通。

### Q7. 一个 livetoken token 配 Codex + Claude Code,余额怎么算

**余额合并算**——两套 CLI 的请求都走同一个 token 计费。**不是 ×2**。

---

## 九、留言钩子

跟着教程跑一遍配置过程,**任何环节卡住、报错、配不通**,都可以在评论区留言:

- 哪一步卡住的
- 完整报错信息
- 你用的是哪个第三方服务

我看到会回复。

也欢迎留言:
- 你目前 Codex 和 Claude Code 哪个用得多
- 想看哪些实战教程(MCP 进阶 / Subagent 协作 / Plan 模式深拆)
- 团队内部部署 Claude / Codex 有什么坑

**评论区见**。

---

## 升华

> Codex + Claude Code = 国内 AI 编程的双引擎
>
> 一个 livetoken token 两套用 ·
> 不维护两个账号 · 不切换两个余额 ·
> **AI 编程工作流的最优解**

3 套配置都搞定后,你的开发流可以这样切:

- **写新模块** → VS Code 里用 Claude Code(Sonnet 重构能力强)
- **跑 plan 模式自动化** → Claude Code CLI(Subagent + Plan)
- **快速 review / 单点修改** → Codex 里用 GPT-5.5
- **慢慢聊架构问题** → Claude Desktop(配 MCP 看代码 + GitHub)

**4 个工作流场景 × 同一个 token**。

---

## 附录:Codex + Claude 双引擎一键配置脚本

```bash
#!/bin/bash
# Codex + Claude Code 双引擎一键配置

# 1. 安装两个 CLI
npm install -g @openai/codex
npm install -g @anthropic-ai/claude-code

# 2. 设置 Codex 用的 OpenAI key
echo 'export OPENAI_API_KEY="sk-livetoken-xxxxx"' >> ~/.zshrc

# 3. 创建 Codex 配置
mkdir -p ~/.codex
cat <<EOF > ~/.codex/config.toml
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

# 4. 创建 Claude Code 配置(env 块直接放第三方接入)
mkdir -p ~/.claude
cat <<EOF > ~/.claude/settings.json
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

# 5. 重启 shell
source ~/.zshrc

echo "双引擎配置完成。运行 codex 或 claude 启动。"
```

把上面脚本保存为 `setup.sh`,改一下两处 `sk-livetoken-xxxxx` 为你自己的 token,然后:

```bash
chmod +x setup.sh
./setup.sh
```

**3 分钟,Codex + Claude Code 双引擎全部就位**。

---

*实战复盘 · Claude 全家桶配置教程 · Codex + Claude 双引擎方案*

*关键词:Claude、Claude Desktop、Claude Code、claude_desktop_config.json、CLAUDE.md、ANTHROPIC_BASE_URL、MCP、双引擎 AI 编程*

*本文仅供学习参考 · 各服务请按其官方文档使用*
