# ai-workbench — 全栈 AI 工作台最小可跑示例

> 5 分钟跑通 · Docker 一键部署 · OpenAI 协议兼容

---

## 这是什么

行业落地系列第 6 篇的**配套代码**。一个最小可跑、**行业无关**的全栈 AI 工作台:

- 💬 **聊天**:流式 SSE + RAG 上下文 + 引用展示
- 📚 **知识库**:文档 ingest + UUID 主键 + Chroma 向量检索
- ⚙️ **设置**:配置展示 + 请求日志(字段契约示范)

后端 **FastAPI**,前端 **Vue 3 + Pinia**,向量库 **Chroma**,模型走 **OpenAI 协议兼容 endpoint**。

📖 完整架构和工程决策见 [上级 README](../README.md)。

---

## 5 分钟跑通

### 步骤 1:配置 endpoint

```bash
cp .env.example backend/.env
```

编辑 `backend/.env`:

```bash
# 推荐用 livetoken — 一个 base_url 跑 GPT-5/Claude/Gemini/DeepSeek
LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-xxxxx
LLM_MODEL=gpt-5
```

**没 token?**

- 去 [livetoken.top](https://livetoken.top) 注册 + 充 ¥10 试用
- 控制台 → 令牌管理 → 创建 token
- 详细介绍:[../../../docs/livetoken.md](../../../docs/livetoken.md)

**或者用其他 endpoint**:
- OpenAI 官方:`LLM_API_BASE=https://api.openai.com/v1`
- OpenRouter:`LLM_API_BASE=https://openrouter.ai/api/v1`
- 私有 LiteLLM Gateway:你自己的地址

### 步骤 2:Docker 启动

```bash
docker compose up -d
```

**首次启动 1-2 分钟**(下载 BGE-M3 embedding 模型)。后续秒启。

查看日志:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### 步骤 3:访问

| 服务 | URL |
|---|---|
| 前端 | http://localhost:8080 |
| 后端 API 文档(Swagger) | http://localhost:8001/docs |
| 健康检查 | http://localhost:8001/api/health |

### 步骤 4:试用

1. 打开前端 http://localhost:8080
2. 进入「💬 聊天」直接对话(无知识库时,纯 LLM 回答)
3. 进入「📚 知识库」,粘一段文本 → 添加到知识库
4. 回到「💬 聊天」问相关问题,会看到带引用的回答
5. 进入「⚙️ 设置」看实时请求日志

---

## 不用 Docker 也可以跑

### 本地后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 配置 .env
cp ../.env.example .env

# 启动
uvicorn app.main:app --reload --port 8001
```

### 本地前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173(vite dev server)
```

vite 已配置 `/api` 代理到 `http://localhost:8001`,前后端联调直接跑。

---

## 目录结构

```
code/
├── docker-compose.yml          # 一键启动配置
├── .env.example                # endpoint + 模型配置模板
├── README.md                   # 你正在看的
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt        # FastAPI + Chroma + OpenAI SDK
│   └── app/
│       ├── main.py             # FastAPI 入口 + 健康检查
│       ├── config.py           # pydantic-settings(读 .env)
│       ├── api/
│       │   ├── chat.py         # /api/chat/stream
│       │   ├── knowledge.py    # /api/knowledge/ingest|search|list
│       │   └── settings.py     # /api/settings/config|logs
│       ├── services/
│       │   ├── chat.py         # ⭐ 编排核心:RAG + 历史 + LLM 流式
│       │   └── rag.py          # ⭐ Chroma + UUID 主键 + sentence-transformers
│       └── models/
│           └── schemas.py      # ⭐ 字段契约(timestamp/doc_id 等)
└── frontend/
    ├── Dockerfile              # multi-stage build
    ├── nginx.conf              # SSE 长连接 + API 代理
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.js
        ├── router.js
        ├── App.vue             # 3 标签 sidebar 布局
        ├── api/index.js
        └── views/
            ├── ChatView.vue    # ⭐ 流式 SSE 消费 + 引用渲染
            ├── KnowledgeView.vue
            └── SettingsView.vue
```

---

## API 参考

### 流式聊天

```bash
curl -N -X POST http://localhost:8001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "你好", "history": []}'
```

返回 SSE 流:

```
data: {"type": "references", "data": [...]}
data: {"type": "delta", "data": "你"}
data: {"type": "delta", "data": "好"}
...
data: [DONE]
```

### Ingest 文档

```bash
curl -X POST http://localhost:8001/api/knowledge/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试文档",
    "content": "这是一段测试内容...",
    "category": "default"
  }'
```

返回 `{"doc_id": "...", "status": "ingested"}`。

**首次 ingest 不传 `doc_id`**,系统生成 UUID。
**rebuild / 改分类传入原 `doc_id`**,避免文档身份漂移。

### 检索测试

```bash
curl "http://localhost:8001/api/knowledge/search?q=测试&top_k=3"
```

---

## 配置切换示例

### 切换模型(同一 endpoint)

修改 `backend/.env`:

```bash
LLM_MODEL=claude-sonnet-4-5     # 改成 Claude
# LLM_MODEL=gemini-2.5-pro      # 或 Gemini
# LLM_MODEL=deepseek-r1         # 或 DeepSeek
```

重启 backend:

```bash
docker compose restart backend
```

### 切换 endpoint

```bash
# 走官方
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=sk-真实-openai-key

# 走 livetoken
LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-livetoken-token
```

**代码完全不用改** —— OpenAI 协议兼容的好处。

### 热改 system prompt

不重启:

```bash
docker exec workbench-backend sh -c \
  'echo "你是一名 [行业] 专家..." > /app/data/system_prompt.txt'
```

下一条消息生效。

---

## 数据持久化

Docker 部署后,以下目录会被挂载到主机:

| 容器路径 | 主机路径 | 内容 |
|---|---|---|
| `/app/data/chroma_db` | `./data/chroma_db` | 向量库 |
| `/app/data/uploads` | `./data/uploads` | 原始文件(预留) |
| `/app/data/db_data` | `./data/db_data` | SQLite(对话历史 + doc_registry) |
| `/root/.cache/huggingface` | `hf_cache` volume | embedding 模型(几 GB) |

**重启容器数据不丢**。彻底重置:

```bash
docker compose down -v   # ⚠️ 删 volume
rm -rf ./data
```

---

## 工程纪律(本仓库代码体现的)

| 纪律 | 在哪里 | 体现 |
|---|---|---|
| 数据主键稳定 | `services/rag.py` | UUID + registry,不绑路径 |
| 前后端契约统一 | `models/schemas.py` + 各 View | `timestamp` 字段两边一致 |
| 系统 prompt 工程化 | `services/chat.py` | 文件优先 / 代码兜底 / 可热改 |
| 模型层抽象 | `config.py` + `chat.py` | OpenAI 协议兼容,1 行切换 |
| RAG + 历史融合 | `services/chat.py::stream_reply` | 始终跑,不靠 LLM 判断 |
| 启动期分离 | `main.py::lifespan` | embedding 后台异步加载 |
| 健康检查 | `main.py::health` | SQLite + Chroma 双检 |

---

## 接下来怎么扩展

### 加新页面

参考 `frontend/src/views/ChatView.vue`,3 步:

1. 写一个新 `.vue`(如 `RewriteView.vue`)
2. `router.js` 加路由
3. `App.vue` 的 sidebar 加 nav-item

**所有页面共享 `/api/chat/stream`**,只是前端拼不同的 system prompt。

### 加多模型路由

参考 [docs/livetoken.md](../../../docs/livetoken.md) 里的 LiteLLM 代码片段,在 `services/chat.py` 加 `smart_call(task_type, prompt)`,按任务路由到不同模型。

### 加领域知识库

直接通过「知识库」页面上传。生产环境建议加上:

- 按目录批量 ingest(脚本)
- 按文档类型不同切块策略(Markdown / PDF / 代码)
- 加 Reranker(Cohere rerank-3.5)提升召回质量

---

## 常见问题

### Q1. 前端访问报 502 / API 不通

后端没启动好。等 30 秒,或:

```bash
docker compose logs backend | tail -50
```

查看错误。常见:`.env` 没配 / API key 错。

### Q2. 流式输出卡住

`nginx.conf` 里 `proxy_buffering off` 没生效,或:

- `proxy_read_timeout` 不够(默认 600s)
- 你的 endpoint 不支持长 SSE(换 livetoken / 官方)

### Q3. embedding 模型下载慢

首次下载 BGE-M3 几个 GB。可以:

- 改用更小的模型:`.env` 里 `EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5`
- 用国内镜像:在 backend 里加 `HF_ENDPOINT=https://hf-mirror.com`

### Q4. 怎么换前端框架?

后端 API 是 REST + SSE,前端可以换成 React / Svelte / Next.js,只要按 `/api/*` 文档调用即可。

---

## License

MIT — 跟主仓库一致。详见 [../../../LICENSE](../../../LICENSE)。
