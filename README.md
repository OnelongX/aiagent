<div align="center">

<img src="assets/header.png" alt="AI Agent 实战手册" width="100%" />

# AI Agent 实战手册

**14 篇 Claude Agent SDK 实战教程**
**从工具栈配置 · 到行业落地 · 到跨行业平移**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Articles](https://img.shields.io/badge/Articles-18-blue.svg)](#内容索引)
[![Industries](https://img.shields.io/badge/Industries-15+-4ade80.svg)](#)
[![Public Account](https://img.shields.io/badge/公众号-实战复盘-orange.svg)](#关注公众号实战复盘)

<!-- LAST-UPDATED -->最近更新:2026-05-11<!-- /LAST-UPDATED -->

</div>

---

## 这是什么

本仓库是公众号「**实战复盘**」14 篇 Agent 实战教程的完整开源资料。

写过 14 篇 Agent 实战之后,验证了一个核心结论:

> **Claude Agent SDK 的工程模式是行业无关的。**
> 真正的门槛不在技术,在认知。
> 唯一稀缺的是把行业 20 年的 Excel,拆成 20 个工具 + 4 个 Subagent + 5 个 Hooks。

7 个完全不同的领域(绿电 / 合同 / 知识库 / 客服 / 电商 / 二手 3C / 自媒体)—— 同一套骨架都撑得住。

---

## 内容索引

### 第一阶段:AI 工具栈(6 篇)

从用 AI 编程工具,到用官方 SDK 造自己的 AI Agent。

| # | 篇目 | 核心 |
|---|---|---|
| 1 | [Codex CLI 配置完整教程](01-ai-toolstack/01-codex-cli/) | config.toml 全参数解析 + 3 套预设 |
| 2 | [Codex 三端通用配置](01-ai-toolstack/02-codex-multi-platform/) | CLI / Desktop / VS Code 共享配置 |
| 3 | [Claude 全家桶配置](01-ai-toolstack/03-claude-suite/) | Claude Chat / Cowork / Code 三端 |
| 4 | [opencode 配置教程](01-ai-toolstack/04-opencode/) | 75+ 模型聚合编程助手 |
| 5 | [Hermes + OpenClaw 配置](01-ai-toolstack/05-hermes-openclaw/) | 个人 AI 网关 + 工具编排 |
| 6 | [Claude Agent SDK 完整教程](01-ai-toolstack/06-claude-agent-sdk/) | Python + TS 双语 · 6 大核心能力 |

### 第二阶段:行业落地(8 篇)

5 个 Agent SDK 工具调度案例 + 3 个全栈产品级实战(均含完整可跑代码)。

| # | 篇目 | 关键创新 |
|---|---|---|
| 1 | [家庭绿电方案助手](02-industry-cases/01-home-solar-advisor/) | 6 工具 + 4 Subagent · 单模型工具调度 |
| 2 | [合同审查助手](02-industry-cases/02-contract-review/) | Claude+Gemini+GPT 多模型协作 · 漏判 <2% |
| 3 | [企业知识库 Q&A](02-industry-cases/03-enterprise-kb-qa/) | Qdrant + Cohere Rerank + RAGAS · 3 周落地 |
| 4 | [企业客服系统](02-industry-cases/04-customer-service/) | 12 工具 + 5 Hooks · 边界守护 |
| 5 | [绿电电商客服系统](02-industry-cases/05-solar-ecommerce/) | 接 OMS · 下单闭环 · Claude+GPT-5 双引擎 |
| **6** | [**全栈 AI 工作台**](02-industry-cases/06-fullstack-workbench/) ⭐ | Vue + FastAPI + Chroma + Docker · **完整可跑代码** |
| **7** | [**Vectorless RAG 客服**](02-industry-cases/07-vectorless-rag-cs/) ⭐ | PageIndex 中文实战 · **完整可跑代码** |
| **8** | [**学生论文助手**](02-industry-cases/08-thesis-assistant/) ⭐ | 8 能力 + 学术诚信红线 + DOI 校验 · **完整可跑代码** |

### 第三阶段:跨行业平移(2 篇)

验证工程模式与行业无关。

| # | 篇目 | 行业 |
|---|---|---|
| 1 | [二手手机推荐 + 售卖 Agent](03-cross-industry/01-used-phone-agent/) | 二手 3C · 2B/2C · 微信生态 |
| 2 | [自媒体写作 + 脚本 Agent](03-cross-industry/02-content-creator-agent/) | 内容创作 · 风格 embedding |

### 第四阶段:阶段性综述

| 篇目 | 主轴 |
|---|---|
| [AI Agent 全行业落地综述](04-survey/) | 15+ 行业全景图 + 任务×模型矩阵 + 5 大工程定律 |

---

## 关于公众号「实战复盘」

> 每周更新 AI Agent 行业落地实战
> 14 篇沉淀 1 套工程框架 · 跨行业平移已验证 2 个方向
> 留言区告诉我:你在哪个行业 / 想看哪个场景的下一篇

**留言区欢迎**:
- 你在哪个行业 · 卡在哪一步
- 想看哪个场景的深度落地
- 你正在做的 Agent 卡在哪一个 Hook

---

## 技术栈

- **Orchestrator**: [Claude Agent SDK](https://docs.anthropic.com/) (Python + TypeScript)
- **Multi-provider**: [LiteLLM](https://github.com/BerriAI/litellm)
- **Vector DB**: [Qdrant](https://qdrant.tech/)
- **Embedding**: BGE-M3
- **Rerank**: Cohere rerank-3.5
- **Eval**: [RAGAS](https://github.com/explodinggradients/ragas)
- **Models**: Claude Sonnet 4.5 / GPT-5 / Gemini 2.5 Pro / DeepSeek R1
- **Visual**: Python PIL(配图生成代码全部开源)

---

## 快速开始

```bash
# 1. 装环境
pip install claude-agent-sdk litellm

# 2. 配置 endpoint(参考 docs/endpoints.md)
export ANTHROPIC_AUTH_TOKEN="sk-xxxxx"
export ANTHROPIC_BASE_URL="https://livetoken.top"
export OPENAI_API_KEY="sk-xxxxx"
export OPENAI_BASE_URL="https://livetoken.top"

# 3. 跑第一个 Agent
python -c "
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions
async def main():
    async for m in query(prompt='What files are here?',
                          options=ClaudeAgentOptions(allowed_tools=['Bash'])):
        if hasattr(m, 'result'): print(m.result)
asyncio.run(main())
"
```

国内开发者推荐使用 **[livetoken](https://livetoken.top)** 作为统一 endpoint —— 一个 base_url 同时跑 **280+ 模型**(GPT-5 / Claude / Gemini / DeepSeek / Midjourney 等),OpenAI 协议 100% 兼容,**官方价 2.21~3.42 折**。

- 📋 endpoint 选型综述:[docs/endpoints.md](docs/endpoints.md)
- 📘 **livetoken 深度介绍**(配置示例 / 价格 / 踩坑指南):[docs/livetoken.md](docs/livetoken.md)

---

## 5 个行业无关的工程定律

13 篇沉淀的规律,**任何行业都成立**:

1. **工具优先 · LLM 不计算** —— 任何数字/价格/状态全走工具
2. **权限在数据层 · 不在 Prompt** —— 向量库 filter,不靠 prompt 自觉
3. **Subagent 分工** —— triager 用 Haiku,推理用 Sonnet · 成本压 1/5
4. **Hooks 守红线** —— 价格/承诺/状态机不让 LLM 自由发挥
5. **评测驱动** —— RAGAS / CSAT / DSAT 任一指标跌 5% 阻断上线

---

## 仓库结构

```
aiagent/
├── README.md                       # 你正在看的
├── assets/
│   ├── banner.png                  # GitHub social preview (1280×640)
│   ├── header.png                  # 顶部 header (1200×300)
│   └── gen_banner.py               # banner 生成代码
├── docs/
│   └── endpoints.md                # endpoint 选型 + 配置示例
├── sync_to_github.py               # 本地同步脚本(WeChat → GitHub)
├── .github/workflows/              # CI:自动更新索引 + link check
├── 01-ai-toolstack/                # AI 工具栈 6 篇
├── 02-industry-cases/              # 行业落地 5 篇
├── 03-cross-industry/              # 跨行业平移 2 篇
└── 04-survey/                      # 阶段性综述
```

每篇含:`README.md`(完整文章)+ `gen.py`(PIL 配图代码)+ `images/`(5 张配图)

---

## 后续路线

跨行业平移已验证 2 个方向(3C 电商 + 内容创作)。下一步:

- [ ] 法律行业(合同 / 案例 / 文书)
- [ ] 医疗行业(影像 / 分诊 / 用药)
- [ ] 金融行业(KYC / 风控 / 投顾)
- [ ] 教育行业(学情 / 批改 / 家校)
- [ ] 制造行业(MES / 工艺 / 质检)

模式相同,数据 + 工具不同。

---

## License

[MIT](LICENSE)

本仓库内容仅供学习参考。涉及的所有外部服务请按其官方文档使用,遵守相关服务条款。
