# 企业级知识库 + 问答系统 —— 3 周落地的完整工程方案

> 实战复盘 · AI 工具栈 · 行业落地篇
>
> 跟个人 RAG 不是一个东西。80% 的工作量在 LLM 之外。

---


<div align="center">

<a href="https://github.com/OnelongX/aiagent">
<img src="../../assets/wechat-qrcode.png" width="600" alt="公众号:IamOnelong" />
</a>

📖 **本文同步发布于公众号「实战复盘」** · 微信号:`IamOnelong`
🌐 [完整代码仓库 · github.com/OnelongX/aiagent](https://github.com/OnelongX/aiagent)
💡 endpoint 选型:[docs/livetoken.md](../../docs/livetoken.md)

</div>

---

## I. 企业级 ≠ ChatGPT 喂文档

试过的都知道:把公司文档丢进 ChatGPT,前 2 天惊艳,第 3 天发现:

- 答不出昨天刚更新的内容(没增量同步)
- HR 同事问到了财务的薪资数据(没权限隔离)
- 答案没出处,法务团队不敢用(没引用溯源)
- "你这数据从哪来的" 答不上(没审计日志)
- 一周后回答变差,没人知道为什么(没评测)

**这就是个人 RAG 跟企业级 RAG 的本质差距。**

| 维度 | 个人 RAG | 企业级 |
|---|---|---|
| 数据 | 一次性上传 | 多源 + 增量同步 |
| 权限 | 全员可见 | ACL 隔离 + 继承 |
| 引用 | 可选 | **强制**,每句必引 |
| 审计 | 无 | 谁问了什么 / 看了什么 |
| 评测 | 凭感觉 | RAGAS 自动跑 |

**5 个维度缺一不可,这才叫企业级。**

---

## II. 整体架构(三层)

```
┌─────────────────────────────────────────────┐
│ 数据层  Connectors(Confluence/Notion/SP/PDF/  │
│         Slack/Jira/Git/Email)+ 增量同步       │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ 索引层  Chunking → Embedding → Vector DB     │
│         + BM25 倒排 + ACL 元数据              │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ 查询层  Claude Agent SDK orchestrator        │
│         Hybrid Retrieval → Rerank → Cite     │
│         → Audit Log                          │
└─────────────────────────────────────────────┘
```

---

## III. 技术选型(2026 推荐栈)

**不造轮子,全用现成的**:

| 模块 | 推荐 | 替代 | 为什么 |
|---|---|---|---|
| Connectors | **Airbyte** | Fivetran / 自写 | 200+ 数据源现成 |
| Parser | **Unstructured.io** | PyMuPDF | 表格/图片/版面识别强 |
| Chunking | **Late Chunking**(BGE-M3) | RecursiveSplitter | 跨段语义保留 |
| Embedding | **BGE-M3** | OpenAI text-embedding-3-large | 中英多语 + 长文 + 开源 |
| Vector DB | **Qdrant** | Milvus / Weaviate | payload filter 快 / ACL 友好 |
| 倒排 | **OpenSearch** | Elasticsearch | BM25 + 中文分词 |
| Reranker | **Cohere rerank-3.5** | BGE-reranker-v2-m3 | 召回 100 → 精排 10 |
| 评测 | **RAGAS** | DeepEval | 4 个核心指标自动算 |
| Orchestrator | **Claude Agent SDK** | LangChain | 上一篇讲过 |
| LLM | **Claude Sonnet 4.5** | GPT-4.1 | 长上下文 + 引用准 |

**3 个非主流选择**(企业级关键):

1. **Late Chunking** —— 先 embed 全文再切块,保留跨段落语义
2. **Hybrid Retrieval** —— BM25 + Dense 双路融合,纯向量会漏关键词匹配
3. **Reranker 必须有** —— top-100 → top-10 精排,Answer Relevancy +15-20 个点

---

## IV. 增量同步是企业级灵魂

```python
class Connector:
    def list_docs(since: datetime) -> list[DocMeta]: ...
    def fetch(doc_id) -> RawDoc: ...
    def acl(doc_id) -> list[str]: ...   # 权限随文档一起入库

for source in [confluence, notion, sharepoint, slack, jira]:
    for doc in source.list_docs(since=last_sync[source]):
        raw = source.fetch(doc.id)
        chunks = late_chunk(parse(raw))
        for chunk in chunks:
            chunk.payload = {
                "doc_id": doc.id,
                "source": source.name,
                "url": doc.url,
                "updated_at": doc.updated_at,
                "acl": source.acl(doc.id),    # ← 权限随文档
                "title": doc.title,
            }
            qdrant.upsert(chunk)
            opensearch.index(chunk)
```

**关键纪律**:删除文档要传播。Confluence 上删了一个 page,Qdrant 里对应的 chunk 也得删,否则用户问出来的答案引用 404。

---

## V. 7 个核心工具

```python
from claude_agent_sdk import tool

# 1. 混合检索(权限过滤在向量层做)
@tool("hybrid_search", "BM25 + Dense 双路融合",
      {"query": str, "user_id": str, "top_k": int})
async def hybrid_search(args):
    user_acl = acl_service.groups_of(args["user_id"])
    dense_hits = qdrant.search(
        embed(args["query"]),
        filter={"acl": {"$any": user_acl}},
        limit=100)
    sparse_hits = opensearch.search(
        args["query"], filter={"acl": user_acl}, size=100)
    merged = reciprocal_rank_fusion(dense_hits, sparse_hits)
    return {"content": [{"type": "text",
            "text": json.dumps(merged[:args["top_k"]])}]}

# 2. Rerank 精排
@tool("rerank", "Cohere rerank 精排",
      {"query": str, "candidates": list, "top_n": int})
async def rerank(args):
    resp = cohere.rerank(model="rerank-3.5",
                        query=args["query"],
                        documents=[c["text"] for c in args["candidates"]],
                        top_n=args["top_n"])
    return {"content": [{"type": "text",
            "text": json.dumps([args["candidates"][r.index] 
                                for r in resp.results])}]}

# 3. 带引用生成
@tool("generate_with_citation", "强制引用回答",
      {"query": str, "passages": list})
async def generate_with_citation(args):
    prompt = f"""仅根据以下 passages 回答。每句末尾必须标引用 [src_N]。
若 passages 不足以回答,直接说"我不知道"。

passages:
{format_passages(args['passages'])}

问题:{args['query']}"""
    answer = call_claude(prompt)
    return {"content": [{"type": "text", "text": answer}]}

# 4. 引用验证
@tool("verify_citations", "验证引用是否真实",
      {"answer": str, "passages": list})
async def verify_citations(args):
    cites = extract_citations(args["answer"])
    bad = [c for c in cites if c not in {p["id"] for p in args["passages"]}]
    return {"content": [{"type": "text",
            "text": json.dumps({"valid": not bad, "fake": bad})}]}

# 5. 查询改写
@tool("rewrite_query", "提问 → 多检索查询",
      {"raw_query": str})
async def rewrite_query(args):
    queries = call_claude_for_rewrite(args["raw_query"], n=3)
    return {"content": [{"type": "text", "text": json.dumps(queries)}]}

# 6. ACL 二次校验
@tool("check_acl", "二次校验用户权限",
      {"user_id": str, "doc_ids": list})
async def check_acl(args):
    allowed = acl_service.filter(args["user_id"], args["doc_ids"])
    return {"content": [{"type": "text",
            "text": json.dumps({"allowed": allowed,
                                "denied": list(set(args["doc_ids"]) - set(allowed))})}]}

# 7. 审计日志
@tool("audit_log", "落审计日志",
      {"user_id": str, "query": str, "passages": list, "answer": str})
async def audit_log(args):
    audit_db.insert({**args, "ts": now()})
    return {"content": [{"type": "text", "text": "logged"}]}
```

---

## VI. 4 个 Subagent

```python
agents = {
    "query-planner": AgentDefinition(
        prompt="rewrite_query 拆 3 个检索查询,准备 hybrid_search。",
        tools=["rewrite_query"]),

    "retriever": AgentDefinition(
        prompt="对每个改写查询 hybrid_search → 合并 → rerank 到 top-10。",
        tools=["hybrid_search", "rerank"]),

    "answerer": AgentDefinition(
        prompt="generate_with_citation → verify_citations。"
               "引用造假删除重生成。passages 不足直说不知道。",
        tools=["generate_with_citation", "verify_citations"]),

    "auditor": AgentDefinition(
        prompt="check_acl 二次校验 → audit_log 落库。",
        tools=["check_acl", "audit_log"]),
}
```

---

## VII. 权限模型 —— 企业级最重要的一段

**三道闸门,缺一不可**:

```
闸门 1:索引时(数据入库)
  chunk.payload.acl = [group_ids]   # 跟随源系统

闸门 2:检索时(向量召回)
  qdrant.search(filter={"acl": {"$any": user.groups}})

闸门 3:答完二次校验
  check_acl(user_id, cited_doc_ids)
  → 任一拒绝 → 整答案打回 / 重生成
```

**ACL 继承规则**(从源系统拉,别自己重新设计):

- Confluence:Space → Page(继承 + override)
- SharePoint:Site / Library / Item 三级
- Notion:Workspace / Page / Block

**最易踩的坑**:用户从 finance 组转到 sales 组后,缓存的 embedding 还能搜到 finance 数据。**ACL 必须实时,不能缓存**。

**永远不要在 Prompt 里限制权限**:
- 错:"你是 HR,只回答 HR 问题" → 会被 prompt injection 突破
- 对:权限在向量层 filter,LLM 根本接触不到不该看的 chunk

---

## VIII. 3 个 Hooks(工程红线)

```python
hooks = {
  # 引用造假 → 阻断输出
  "PostToolUse:verify_citations":
      lambda i: deny(i) if not parsed(i)["valid"] else allow(),
  
  # ACL 二次校验不过 → 整答案打回
  "PostToolUse:check_acl":
      lambda i: regenerate(i) if parsed(i)["denied"] else allow(),
  
  # 检索为 0 → 强制说"找不到",不让 Agent 编
  "PostToolUse:rerank":
      lambda i: force_idk(i) if len(parsed(i)) == 0 else allow(),
}
```

---

## IX. RAGAS 评测体系

**没有评测就没有企业级**。RAGAS 自动跑这 4 个指标:

| 指标 | 测什么 | 合格线 |
|---|---|---|
| **Faithfulness** | 答案是否忠于检索内容 | > 0.85 |
| **Answer Relevancy** | 答案是否切题 | > 0.80 |
| **Context Precision** | 召回内容相关性 | > 0.75 |
| **Context Recall** | 该召回的有没有召回 | > 0.80 |

**做法**:

1. 让员工提 100 个真实问题 + 标准答案 → 黄金集
2. 每次 prompt / chunk / embedding 改动 → 跑黄金集
3. 任一指标跌 5% → block 上线

---

## X. 3 周快速落地

| 周 | 目标 | 交付 |
|---|---|---|
| **W1** | 单源 MVP | Confluence + Qdrant + Claude · 内网 demo |
| **W2** | 多源 + 权限 | Notion/SP/Slack + ACL + 引用 + 审计 |
| **W3** | 评测 + 上线 | RAGAS 黄金集 + 反馈按钮 + 灰度 10% 员工 |

**别在 W1 就上 Reranker / Late Chunking**。MVP 先验证产品价值,再优化质量。

---

## XI. 三个工程坑

### 坑 1:不要切 1000 tokens 固定大小

按文档结构切(标题/段落/list),不够大再合并。**Late Chunking** 是 2025 的新解:先 embed 全文再切块,跨段语义保留。

### 坑 2:别跳过 Reranker

向量检索 top-10 看着对,实际排序很乱。Cohere rerank-3.5 加一层,**Answer Relevancy +15-20 个点**。每次 query 多花 $0.001,极度划算。

### 坑 3:权限不要在 Prompt 里限制

权限必须在数据层 filter,不能交给 LLM 自觉。Prompt injection 一句话就能突破。

---

## XII. 升华

| 维度 | 个人 RAG | 企业级 |
|---|---|---|
| 周期 | 一周 demo | **3 周 MVP / 3 个月调优** |
| 核心难点 | LLM 选型 | **数据 + 权限 + 检索** |
| 失败原因 | 模型不行 | **Chunking + ACL + Rerank** |
| 必备工具 | LangChain | Qdrant + Cohere + RAGAS + Claude SDK |

**关键认知**:企业级知识库 80% 的工作量在 LLM 之外。LLM 只是最后一公里。

把 **检索质量 + 权限隔离 + 引用溯源 + 评测体系** 做对,再讨论用 Claude 还是 GPT。

反过来,模型再强,前面没做对,生产环境一定崩。

---

实战复盘 · AI 工具栈 · 行业落地篇
关键词:企业知识库 / RAG / Qdrant / Cohere / Claude Agent SDK / RAGAS / 权限隔离 / 引用溯源
本文仅供学习参考。
