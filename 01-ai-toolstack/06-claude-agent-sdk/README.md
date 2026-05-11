# Claude Agent SDK 完整教程 —— 从 0 构建你自己的 AI Agent(Python + TypeScript)

> **TL;DR**:Claude Agent SDK = Anthropic 官方推出的 **AI Agent 编程库**,跟 Claude Code CLI **同引擎**——一个是命令行,一个是给你 import 用的库。**Python / TypeScript 双语支持**,内置 10 种工具 + 6 大核心能力(Hooks / Subagents / MCP / Permissions / Sessions / 自定义 Tool)。本文从 Hello World 到 3 个完整 agent 示例全拆。**关键事实**:支持 `ANTHROPIC_BASE_URL` 走第三方 API,所以国内开发者也能跑。


<div align="center">

<a href="https://github.com/OnelongX/aiagent">
<img src="../../assets/wechat-qrcode.png" width="600" alt="公众号:IamOnelong" />
</a>

📖 **本文同步发布于公众号「实战复盘」** · 微信号:`IamOnelong`
🌐 [完整代码仓库 · github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型:[docs/livetoken.md](../../docs/livetoken.md)

</div>

---

承接 AI 工具栈系列前 5 篇(Codex / Claude / opencode / Hermes / OpenClaw)。

那 5 篇全是"配置工具栈"——**用现成的 AI agent 工具**。

**这一篇换维度**:**用官方 SDK 写自己的 AI agent**。

> ⚠️ 注意:Anthropic 已把 "Claude Code SDK" 改名为 **"Claude Agent SDK"**(2025 年中)。所有官方文档现在都叫 Agent SDK。

---

## 一、Claude Agent SDK 是什么

简单说:**Claude Code 的库版本**。

| 维度 | Claude Code CLI | Claude Agent SDK |
|---|---|---|
| 形态 | 命令行 / TUI / VS Code | **库 / 编程接口** |
| 用法 | 终端交互 | **`import` + 写代码** |
| 引擎 | 同 | 同 |
| 工具 | 10 种内置 | 同 10 种内置 |
| 适合 | 日常开发 / 一次性任务 | **生产环境 / CI/CD / 自定义 agent** |
| 语言 | 不需要写代码 | **Python + TypeScript** |

**SDK 把 CLI 的能力暴露成可编程接口** —— 你可以在自己的应用里调用 Claude 自动读文件 / 改代码 / 跑命令 / 联网搜索。

### Agent SDK 的关键差异化(vs Anthropic Client SDK)

| | **Client SDK** | **Agent SDK** |
|---|---|---|
| 直接 API | ✓ | ✗(走 Claude Code 引擎)|
| 工具循环 | **你自己实现**(while 循环 + tool_use 检查 + tool_result 回传) | **Claude 自动循环**(只管发 prompt 看结果)|
| 内置工具 | 没有 | **10 种**(Read / Write / Edit / Bash / etc.)|
| 适合 | 完全自定义 / 简单调用 | **复杂 agent 任务** |

**对比代码**:

```python
# Client SDK:你自己写循环
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK:Claude 自己跑
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

写 agent 的复杂度差 10 倍。

---

## 二、安装 + 鉴权

### 安装

**TypeScript**:

```bash
npm install @anthropic-ai/claude-agent-sdk

# 可选:加 dev 依赖
npm install -D typescript @types/node tsx
```

**注意**:TS SDK **自带 Claude Code 二进制**(平台原生),不用单独装 Claude Code。

**Python**:

```bash
pip install claude-agent-sdk
```

### 鉴权

**官方 Anthropic API key**:

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**Bedrock / Vertex / Azure(企业)**:

```bash
# AWS Bedrock
export CLAUDE_CODE_USE_BEDROCK=1
# 配 AWS credentials

# Google Vertex AI
export CLAUDE_CODE_USE_VERTEX=1
# 配 Google Cloud credentials

# Azure AI Foundry
export CLAUDE_CODE_USE_FOUNDRY=1
# 配 Azure credentials
```

**国内开发者:走第三方 API(livetoken 等)**:

```bash
export ANTHROPIC_AUTH_TOKEN=sk-livetoken-xxxxx
export ANTHROPIC_BASE_URL=https://livetoken.top
```

> ⚠️ **Anthropic 政策**:Agent SDK 构建的产品 **不能** 给用户提供 claude.ai 登录(必须用 API key 鉴权)。这是 Anthropic 商业条款的硬约束——做产品时注意。

---

## 三、Hello World —— 最简 agent

### Python

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    async for message in query(
        prompt="What files are in this directory?",
        options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### TypeScript

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "What files are in this directory?",
  options: { allowedTools: ["Bash", "Glob"] }
})) {
  if ("result" in message) console.log(message.result);
}
```

**3 步看懂**:

1. `query()` 返回**异步生成器**——一次次 yield message
2. `options.allowed_tools` 限定 Claude 可以用的工具
3. message 有多种类型(System / Tool use / Tool result / Result),按需处理

---

## 四、6 大核心能力

### 能力 1:Built-in Tools(10 种)

| 工具 | 用途 |
|---|---|
| **Read** | 读取文件 |
| **Write** | 创建新文件 |
| **Edit** | 精准修改文件 |
| **Bash** | 跑命令 / 脚本 / git |
| **Monitor** | 监听后台脚本输出 |
| **Glob** | 文件 pattern 匹配(`**/*.ts`)|
| **Grep** | regex 搜文件内容 |
| **WebSearch** | 联网搜索 |
| **WebFetch** | 抓取并解析网页 |
| **AskUserQuestion** | 反问用户(多选) |

**示例**:找所有 TODO 注释:

```python
async for message in query(
    prompt="Find all TODO comments and create a summary",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
):
    if hasattr(message, "result"):
        print(message.result)
```

### 能力 2:Hooks —— 生命周期回调

在 agent 关键节点跑自己的代码(验证 / 日志 / 阻断 / 转换)。

**可用 hooks**:`PreToolUse` / `PostToolUse` / `Stop` / `SessionStart` / `SessionEnd` / `UserPromptSubmit`

**示例**:记录所有文件修改到 audit log:

```python
import asyncio
from datetime import datetime
from claude_agent_sdk import query, ClaudeAgentOptions, HookMatcher


async def log_file_change(input_data, tool_use_id, context):
    file_path = input_data.get("tool_input", {}).get("file_path", "unknown")
    with open("./audit.log", "a") as f:
        f.write(f"{datetime.now()}: modified {file_path}\n")
    return {}


async def main():
    async for message in query(
        prompt="Refactor utils.py to improve readability",
        options=ClaudeAgentOptions(
            permission_mode="acceptEdits",
            hooks={
                "PostToolUse": [
                    HookMatcher(matcher="Edit|Write", hooks=[log_file_change])
                ]
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

**关键**:`PostToolUse` 在每次 Edit / Write 后触发,你可以**审计 / 阻断 / 修改** Claude 行为。

### 能力 3:Subagents —— 派出专项 agent 协作

主 agent 委派任务,subagent 报告回来。

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async for message in query(
    prompt="Use the code-reviewer agent to review this codebase",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep", "Agent"],  # 加 Agent 工具
        agents={
            "code-reviewer": AgentDefinition(
                description="Expert code reviewer for quality and security reviews.",
                prompt="Analyze code quality and suggest improvements.",
                tools=["Read", "Glob", "Grep"],
            )
        },
    ),
):
    print(message)
```

**注意**:用 Subagents 必须 `allowed_tools` 里加 `"Agent"`(因为 subagent 通过 Agent 工具调用)。

Subagent 内消息有 `parent_tool_use_id` 字段,可以追溯哪条消息属于哪个 subagent。

### 能力 4:MCP —— 接外部系统

**M**odel **C**ontext **P**rotocol:数据库 / 浏览器 / API / GitHub / [几百个](https://github.com/modelcontextprotocol/servers)。

**示例**:接 Playwright MCP 让 agent 操作浏览器:

```python
async for message in query(
    prompt="Open example.com and describe what you see",
    options=ClaudeAgentOptions(
        mcp_servers={
            "playwright": {"command": "npx", "args": ["@playwright/mcp@latest"]}
        }
    ),
):
    print(message)
```

### 能力 5:Permissions —— 控制工具权限

```python
# 只读 agent
async for message in query(
    prompt="Review this code for best practices",
    options=ClaudeAgentOptions(
        allowed_tools=["Read", "Glob", "Grep"],  # 只允许这 3 个
    ),
):
    print(message)
```

**permission_mode 取值**:
- `default`:默认(每个工具调用前问)
- `acceptEdits`:自动接受所有 Edit
- `bypassPermissions`:跳过所有许可(危险)
- `plan`:plan 模式(只读 + 输出计划)

### 能力 6:Sessions —— 跨会话上下文

```python
session_id = None

# 第 1 次 query:抓 session ID
async for message in query(
    prompt="Read the authentication module",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob"]),
):
    if isinstance(message, SystemMessage) and message.subtype == "init":
        session_id = message.data["session_id"]

# 第 2 次:resume 上一个 session
async for message in query(
    prompt="Now find all places that call it",  # "it" = auth module(继承上下文)
    options=ClaudeAgentOptions(resume=session_id),
):
    print(message)
```

Sessions 还可以 **fork**(从某个会话分出多个分支并行探索)。

---

## 五、自定义工具(createSdkMcpServer)

除了内置 10 种工具,**你可以加自己的工具**。

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

// 自定义工具:查数据库
const queryDb = tool({
  name: "query_database",
  description: "Run a SQL query against the production database",
  input_schema: z.object({
    sql: z.string().describe("SQL query to run"),
  }),
  handler: async ({ sql }) => {
    const result = await myDb.query(sql);
    return { content: JSON.stringify(result) };
  },
});

// 注册到 SDK
const mcpServer = createSdkMcpServer({
  name: "my-tools",
  tools: [queryDb],
});

// 使用
for await (const message of query({
  prompt: "How many users signed up yesterday?",
  options: {
    mcpServers: { "my-tools": mcpServer },
  }
})) {
  console.log(message);
}
```

**Python 版**用 Pydantic schema:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server
from pydantic import BaseModel


class QueryDbInput(BaseModel):
    sql: str  # SQL query


@tool(
    name="query_database",
    description="Run a SQL query against the production database",
    input_schema=QueryDbInput,
)
async def query_db(args: QueryDbInput):
    result = await my_db.query(args.sql)
    return {"content": str(result)}


mcp_server = create_sdk_mcp_server(name="my-tools", tools=[query_db])
```

**这是 SDK 最强的能力** —— **任何 Python / TypeScript 函数都能变成 Claude 可调用的工具**。

---

## 六、第三方 API 接入(国内开发者关键段)

SDK 底层用 Claude Code 引擎 → **`ANTHROPIC_BASE_URL` 同样生效**。

### 配置走 livetoken

```bash
# 环境变量
export ANTHROPIC_AUTH_TOKEN="sk-livetoken-xxxxx"
export ANTHROPIC_BASE_URL="https://livetoken.top"
```

或在代码里:

```python
# Python
import os
os.environ["ANTHROPIC_AUTH_TOKEN"] = "sk-livetoken-xxxxx"
os.environ["ANTHROPIC_BASE_URL"] = "https://livetoken.top"

from claude_agent_sdk import query
# 之后正常用
```

```typescript
// TypeScript
process.env.ANTHROPIC_AUTH_TOKEN = "sk-livetoken-xxxxx";
process.env.ANTHROPIC_BASE_URL = "https://livetoken.top";

import { query } from "@anthropic-ai/claude-agent-sdk";
// 之后正常用
```

### 走第三方的合规边界

Anthropic 商业条款:

> "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK. Please use the API key authentication methods described in this document instead."

**翻译**:
- ✓ 你做 agent 给客户用,客户用 **API key 鉴权**(包括第三方 API key 如 livetoken)→ **OK**
- ✗ 你做 agent,让客户用 **claude.ai 账号 / 订阅 quota** 登录 → **不允许**

**国内开发者用 livetoken 跑 SDK 是合规的**——只要客户用 API key,不用 Anthropic 账号 quota。

---

## 七、SDK vs CLI vs Managed Agents 对比

| 维度 | Agent SDK | Claude Code CLI | Managed Agents |
|---|---|---|---|
| **形态** | 库 | CLI | 托管 REST API |
| **跑哪** | 你的进程 / 基础设施 | 你的机器 | Anthropic 托管 |
| **接口** | Python / TS | 终端 | REST |
| **Agent 操作** | 你的文件系统 | 你的文件系统 | 托管 sandbox |
| **会话状态** | JSONL 在你磁盘 | 同 | Anthropic 托管 |
| **自定义工具** | in-process Python / TS 函数 | 不支持 | Claude 触发,你执行 |
| **适合** | **本地原型 / 文件系统 agent** | **日常开发** | **生产环境 / 长任务 / 异步会话** |

**常见路径**:本地用 SDK 原型 → 上 Managed Agents 跑生产。

---

## 八、3 个完整 agent 实战示例

### 示例 1:代码 Review agent(只读 + Subagent)

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition


async def main():
    async for message in query(
        prompt="Review the codebase for security and quality issues. Use the security-reviewer subagent.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "Agent"],
            agents={
                "security-reviewer": AgentDefinition(
                    description="Security expert reviewing for vulnerabilities",
                    prompt="Look for SQL injection, XSS, hardcoded secrets, unsafe eval/exec.",
                    tools=["Read", "Glob", "Grep"],
                ),
                "quality-reviewer": AgentDefinition(
                    description="Code quality expert",
                    prompt="Look for code smell, complexity, missing tests.",
                    tools=["Read", "Glob", "Grep"],
                ),
            },
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)


asyncio.run(main())
```

### 示例 2:Email 助手(MCP + 自定义工具)

```typescript
import { query, tool, createSdkMcpServer } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

const sendEmail = tool({
  name: "send_email",
  description: "Send email to a recipient",
  input_schema: z.object({
    to: z.string(),
    subject: z.string(),
    body: z.string(),
  }),
  handler: async ({ to, subject, body }) => {
    // 调你自己的邮件服务
    await myEmailService.send({ to, subject, body });
    return { content: `Email sent to ${to}` };
  },
});

const mcpServer = createSdkMcpServer({
  name: "email-tools",
  tools: [sendEmail],
});

for await (const message of query({
  prompt: "Read my unread Slack messages and email a summary to my manager",
  options: {
    allowedTools: ["WebFetch"],
    mcpServers: {
      "email-tools": mcpServer,
      slack: { command: "npx", args: ["@modelcontextprotocol/server-slack"] },
    },
  }
})) {
  console.log(message);
}
```

### 示例 3:研究 agent(WebSearch + 跨会话记忆)

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def research_agent(topic: str, session_id: str = None):
    options = ClaudeAgentOptions(
        allowed_tools=["WebSearch", "WebFetch", "Write"],
        permission_mode="acceptEdits",
    )
    if session_id:
        options.resume = session_id

    final_session = None
    async for message in query(
        prompt=f"研究 {topic} 的最新进展,把发现写进 research_{topic}.md",
        options=options,
    ):
        if hasattr(message, "data") and "session_id" in message.data:
            final_session = message.data["session_id"]
        if hasattr(message, "result"):
            print(message.result)

    return final_session


# 第一次:开始研究
session = asyncio.run(research_agent("Claude Agent SDK"))

# 第二天:继续(记得之前找过什么)
asyncio.run(research_agent("Claude Agent SDK 实战 case", session_id=session))
```

---

## 九、常见问题

### Q1. Agent SDK 跟 Anthropic Client SDK 怎么选?

- **简单调用 / 完全自定义** → Client SDK
- **Agent 任务(读文件 / 跑命令 / 工具循环)** → Agent SDK

**Agent SDK 帮你省掉写工具循环的复杂度**——这是核心价值。

### Q2. 国内能用 Agent SDK 吗?

能。**3 种方式**:
- 直接 Anthropic API key(需要科学上网 + 美元卡)
- 走第三方 OpenAI 兼容 endpoint(`ANTHROPIC_BASE_URL=https://livetoken.top`)
- Bedrock / Vertex / Foundry(企业)

### Q3. 自定义工具能调用什么?

**任何 Python / TypeScript 函数**——数据库 / 邮件 / 内部 API / 第三方服务。tool handler 是普通 async function。

### Q4. Hooks 能阻止 Claude 行为吗?

能。`PreToolUse` hook 返回 `{"allow": False}` 就阻止该工具调用。

### Q5. Agent SDK 能跟 Claude Code CLI 共用配置吗?

**可以**(部分)。SDK 默认读 `.claude/` 目录(同 CLI):
- `.claude/skills/*/SKILL.md`
- `.claude/commands/*.md`
- `CLAUDE.md` 项目记忆

用 `setting_sources`(Python)或 `settingSources`(TS)控制读哪些。

### Q6. SDK 写的 agent 能商业化吗?

能。但有 2 个边界:
- **不能让客户用 claude.ai 登录**(必须 API key)
- 不能用 "Claude Code" 品牌(可以说 "Claude Agent" 或 "Powered by Claude")

具体看 Anthropic 商业条款。

### Q7. Opus 4.7 报错 thinking.type.enabled 怎么办?

升级 SDK 到 v0.2.111+:

```bash
npm install @anthropic-ai/claude-agent-sdk@latest
# 或
pip install --upgrade claude-agent-sdk
```

### Q8. 老 SDK(Claude Code SDK)的代码要改吗?

要。Anthropic 把 Claude Code SDK 改名 Agent SDK,API 部分有破坏性变化。看 [Migration Guide](https://code.claude.com/docs/en/agent-sdk/migration-guide)。

---

## 十、留言钩子

跟着教程跑一遍,**任何环节卡住、报错、配不通**,都可以在评论区留言:

- 哪一步卡住的
- 完整报错信息
- 你用的是哪个第三方服务

我看到会回复。

也欢迎留言:
- 你想用 SDK 写什么样的 agent
- 想看哪些进阶教程(MCP server 自己写 / Hooks 高级用法 / Subagent 协作模式 / 生产环境部署)
- Agent SDK vs LangChain vs AutoGen 对比

**评论区见**。

---

## 升华

> AI 工具栈 6 篇 = 完整学习路径
>
> **前 5 篇**:配置现成 AI 工具(Codex / Claude / opencode / Hermes / OpenClaw)
>
> **第 6 篇(这一篇)**:**用官方 SDK 写自己的 agent**

从"用工具"到"造工具"——这是国内 AI 开发者的关键跃迁。

| 工具 | 解决问题 |
|---|---|
| Codex / Claude Code / opencode | 帮我写代码 |
| Hermes / OpenClaw | AI 跑在我所有平台 |
| **Claude Agent SDK** | **我自己造 AI 工具,跑在我自己的产品里** |

**3 层能力 + 1 个 livetoken token = 完整 AI 工具栈**。

---

## 附录:从 0 到 production agent 的完整脚本

```bash
#!/bin/bash
# Claude Agent SDK 起步配置

# 1. 安装(选一种)
# Python
pip install claude-agent-sdk

# TypeScript
npm install @anthropic-ai/claude-agent-sdk

# 2. 设置 API key(走第三方)
echo 'export ANTHROPIC_AUTH_TOKEN="sk-livetoken-xxxxx"' >> ~/.zshrc
echo 'export ANTHROPIC_BASE_URL="https://livetoken.top"' >> ~/.zshrc
source ~/.zshrc

# 3. 创建第一个 agent
mkdir my-agent && cd my-agent

# Python 版 hello.py
cat <<'EOF' > hello.py
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="What's in this directory?",
        options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
EOF

# 4. 跑起来
python hello.py
```

3 分钟跑通第一个 agent。

---

## FAQ

**Q1:Agent SDK 跟 LangChain / AutoGen 谁强?**
**Agent SDK 优势**:Anthropic 官方 + Claude Code 同引擎(能力最完整)+ 简洁 API。**LangChain 优势**:多 LLM provider 支持 + 大量集成。**AutoGen 优势**:多 agent 协作模式更细。**用 Claude 优先选 Agent SDK**。

**Q2:Agent SDK 支持流式输出吗?**
支持。`query()` 返回的就是 async generator,每条 message 实时 yield 出来。

**Q3:能在 Lambda / Cloudflare Workers 跑吗?**
**Python SDK** 在 Lambda OK。**TypeScript SDK 用了 Node 原生 binary**,**Cloudflare Workers / 严格的 serverless 跑不通**。

**Q4:Hooks 能不能拦截 user prompt?**
能。`UserPromptSubmit` hook 在用户发 prompt 时触发,可以加 prefix / 改写 / 拒绝。

**Q5:Skills / Slash commands / CLAUDE.md 怎么跟 SDK 一起用?**
默认 SDK 读 `.claude/` 目录跟 CLI 一样。用 `setting_sources` 选项控制读哪些(`user` / `project` / 全部)。

**Q6:SDK 用第三方 API 时延迟更高吗?**
**多一层 hop**(你 → 第三方 → Anthropic),延迟增加 50-200ms。**国内访问国外 Anthropic 反而更慢** —— 第三方 API 反而更快。

**Q7:agent 写完怎么发给别人用?**
3 种方式:**1)CLI 工具**(打包成 npm / pip 包);**2)Web 服务**(包在 FastAPI / Express 里);**3)Discord / Telegram bot**(SDK + bot framework)。

**Q8:Agent SDK 收费吗?**
**SDK 本身免费**(Apache 2.0)。**收费的是模型调用**——按 Anthropic API 价格 / 第三方价格。

---

*实战复盘 · Claude Agent SDK 完整教程 · AI 工具栈 6 篇收官*

*关键词:Claude Agent SDK、Agent SDK、AI Agent、自定义工具、MCP、Hooks、Subagents、Claude Code、Anthropic、AI 编程*

*本文仅供学习参考 · 各服务请按其官方文档使用*
