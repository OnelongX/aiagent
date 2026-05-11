# thesis-assistant — 学生论文助手最小可跑示例

> 5 分钟跑通 · Docker 一键起 · OpenAI 协议兼容 · 学术诚信工程化

---

## 这是什么

行业落地系列**第 8 篇**的配套代码。8 个能力 API + 轻量前端,**学术诚信红线写在代码里**:

- 💬 **大纲** 多版本生成
- ✍️ **章节起草** 留 `[作者填入]` 占位
- 💎 **润色** diff 输出
- 📖 **文献** 真实学术 API + DOI 校验
- 📚 **格式化** BibTeX / GB7714 / APA / IEEE / MLA / Chicago
- 🔍 **相似度** 本地 embedding(不是查重)
- 🎤 **答辩** 3 persona Q&A 模拟

后端 **FastAPI**,前端 **纯静态 HTML+JS**(无框架),向量 **sentence-transformers BGE-M3**,模型走 **OpenAI 协议兼容 endpoint**。

📖 完整架构和工程决策见 [上级 README](../README.md)。

---

## 5 分钟跑通

### 方案 A:Docker(推荐)

```bash
# 1. 配 endpoint
cp .env.example backend/.env
# 编辑 backend/.env 填 LLM_API_KEY

# 2. 启动
docker compose up -d

# 3. 访问 http://localhost:8081
```

**没 token?** 推荐用 [livetoken](https://livetoken.top)(详见 [docs/livetoken.md](../../../docs/livetoken.md))。

### 方案 B:本地开发

```bash
# 1. 自动 setup
chmod +x setup.sh && ./setup.sh

# 2. 配 .env
# (setup.sh 已自动 cp .env.example → backend/.env)
# 编辑 backend/.env 填 LLM_API_KEY

# 3. 启动 backend
cd backend && python run.py
# → http://localhost:8002/docs(API 文档)

# 4. 启动 frontend(用任意静态服务)
cd ../frontend && python -m http.server 8081
# → http://localhost:8081
```

注意:本地开发模式下,`frontend/js/app.js` 调用 `/api/*`,需要前端反代到后端 8002。最简单的方式是用 Docker Compose。

---

## 第一次使用流程

1. 访问 http://localhost:8081
2. 进「📋 大纲」填论文题目、学科、关键论点 → 生成 3 套大纲对比
3. 挑一套大纲 → 进「✍️ 起草」按章节起草框架
4. **重点看占位符** `[作者填入: ...]` —— 那些必须你自己补
5. 写完后进「💎 润色」改语言(diff 输出 · 可审阅)
6. 进「📖 文献」检索 —— **DOI 验证后才能用**
7. 进「🎤 答辩」让 AI 当 3 类委员模拟提问

---

## 适合什么场景

✅ **强相关**:
- 本科 / 硕士 / 博士论文写作辅助
- 高校教师论文修订
- 研究生导师组工具

❌ **不太合适**:
- 用 AI 代写整篇论文(本工具的诚信红线会拦截)
- 真实查重(请用知网 / Turnitin / iThenticate)
- 学术不端用途

---

## 目录结构

```
code/
├── docker-compose.yml          # 一键启动
├── .env.example                # endpoint + 模型配置模板
├── setup.sh                    # 一键 setup
├── README.md                   # 你正在看的
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run.py
│   └── app/
│       ├── main.py             # FastAPI 入口
│       ├── config.py           # pydantic-settings
│       ├── api/
│       │   ├── outline.py      # POST /api/outline
│       │   ├── section.py      # POST /api/section
│       │   ├── polish.py       # POST /api/polish
│       │   ├── cite.py         # /api/cite/search + /api/cite/format
│       │   ├── dedupe.py       # POST /api/dedupe
│       │   └── defense.py      # POST /api/defense
│       ├── services/
│       │   ├── llm.py          # OpenAI 协议客户端封装
│       │   ├── academic_api.py # ⭐ arXiv + Crossref + OpenAlex
│       │   ├── citation.py     # 6 种格式化
│       │   └── similarity.py   # 本地 embedding 相似度
│       └── models/
│           └── schemas.py      # ⭐ 字段契约(Pydantic)
└── frontend/
    ├── nginx.conf              # SSE + API 代理
    ├── index.html              # 6 tab 单页
    ├── style.css
    └── js/
        └── app.js              # 纯 JS · 无框架
```

---

## API 参考

### 大纲生成

```bash
curl -X POST http://localhost:8002/api/outline \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "钙钛矿太阳能电池稳定性研究",
    "discipline": "材料科学",
    "paper_type": "实验型",
    "target_words": 8000,
    "key_points": ["ABX3 结构", "湿热稳定性"],
    "n_versions": 3
  }'
```

### 文献检索 + DOI 校验

```bash
curl -X POST http://localhost:8002/api/cite/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "perovskite stability",
    "year_from": 2020,
    "limit": 5
  }'
```

返回的每篇 paper 都带 `doi_verified` 字段。**未校验的不能进正文**。

### 格式化引用(DOI 必须先校验)

```bash
curl -X POST http://localhost:8002/api/cite/format \
  -H "Content-Type: application/json" \
  -d '{
    "paper": { "title": "...", "doi": "10.1126/science.abc123", "doi_verified": true, ... },
    "style": "gb7714"
  }'
```

支持:`bibtex` / `gb7714` / `apa` / `ieee` / `mla` / `chicago`

### 完整 API 文档

启动后访问 http://localhost:8002/docs(Swagger UI)。

---

## 工程纪律(代码里的体现)

| 纪律 | 代码位置 | 实现 |
|---|---|---|
| **学术 API 真实接入** | `services/academic_api.py` | arXiv + Crossref + OpenAlex 三源融合 |
| **DOI 必须校验** | `api/cite.py::format` | 格式化前调 Crossref verify · 失败拒绝 |
| **章节起草加 AI 标签** | `api/section.py` system prompt | 草稿头部强制 `[本节由 AI 协助起草...]` |
| **降重禁词列表** | `api/dedupe.py::FORBIDDEN_WORDS` | "伪装原创" / "避免查重" → 替换 |
| **答辩 3 persona** | `api/defense.py::PERSONAS` | critic / friendly / outsider 独立 prompt |
| **前后端字段契约** | `models/schemas.py` | Pydantic 类型,前端跟着用 |

---

## 配置说明

### `backend/.env`

```bash
# LLM endpoint(推荐 livetoken)
LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-xxxxx
LLM_MODEL=claude-sonnet-4-5

# 学术 API · 公开 · 无需 key
# Semantic Scholar 可选 key
SEMANTIC_SCHOLAR_API_KEY=

# Embedding(本地下载)
EMBEDDING_MODEL=BAAI/bge-m3
```

### 切换模型

改 `.env` 的 `LLM_MODEL` —— 大纲用 Sonnet,润色用 Haiku 省钱,答辩用 Opus 深思考都行。

---

## 接下来怎么扩展

### 1. 加 Word/LaTeX 导出 + AI 协助报告

新建 `app/api/export.py` + `services/export.py`:

- python-docx 生成 .docx
- 或 jinja2 渲染 .tex
- **关键**:文档末尾自动 append AI 协助章节清单(对齐 Nature/Science 政策)

### 2. 加术语表 + 全文一致性检查

新建 `services/terminology.py`:

- 用户上传 / 自动提取专业术语
- 全文扫描,提示不一致用法

### 3. 加 Semantic Scholar(语义检索)

`services/academic_api.py` 加 `semantic_scholar_search`,接 Semantic Scholar Graph API。

### 4. 接 Zotero / Mendeley

让用户的文献库一键导入,而不只是搜索。

### 5. 加流式输出

`api/section.py` 和 `polish.py` 改成 SSE 流式,前端边写边显示。

---

## 常见问题

### Q1. 大纲生成很慢

LLM 调用 + JSON 解析需要 10-30 秒。可以改 `n_versions=1` 加快。

### Q2. 文献检索为空

- 检查关键词(用英文学术词,不要中文俗语)
- 检查年份过滤是否太严
- 看后端日志:有可能是 arXiv / Crossref 限速

### Q3. DOI 校验为什么有的 false?

Crossref 返回 404 就是 false。可能原因:

- DOI 拼写错(LLM 编的会校验失败)
- DOI 还未发布(很新的 preprint)
- 这正是这个机制存在的意义 —— **过滤掉假引用**

### Q4. 相似度检测准吗?

本地 embedding 是**提示**,不是定罪。真实查重必须用知网 / Turnitin / iThenticate。

### Q5. 答辩 Q&A 太友好

提高 `temperature` 到 0.9+,或修改 `api/defense.py` 的 `PERSONAS["critic"]` prompt,加更强烈的对抗性指令。

---

## 学术诚信声明

**本工具是学术辅助 · 不是代笔工具。**

- 引用必须真实可验证(DOI 校验)
- 章节起草留占位让作者补
- 降重提示禁止包装抄袭
- 论文最终内容、观点、责任归作者本人
- 请遵守所在学术机构的诚信规范

---

## License

MIT — 跟主仓库一致。详见 [../../../LICENSE](../../../LICENSE)。
