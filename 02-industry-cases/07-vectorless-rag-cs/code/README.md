# ai-customer-service — Vectorless RAG 智能客服

> 基于 PageIndex 的 PDF 智能客服系统
> 不切块、不向量、按文档结构 + LLM 推理检索

---

## 这是什么

行业落地系列**第 7 篇**的配套代码。一个面向**结构化长文档(产品规格书 / 法律文书 / 技术手册)**的智能客服系统。

📖 完整工程决策与方案对比见 [上级 README](../README.md)。

### 核心技术差异

| 维度 | 传统向量 RAG(#6) | Vectorless RAG(本篇) |
|---|---|---|
| 文档切块 | 固定 size + overlap | **按文档自然结构(章节 / 小节)** |
| 检索 | embedding + cosine | **LLM 推理选最相关章节** |
| 依赖 | 向量库(Chroma / Qdrant) | **不要向量库** |
| 长文档适配 | 切块易失语义 | **保留章节完整性** |
| 适合 | 通用 / 短文档 | **结构化长文档 / 中文场景** |

---

## 5 分钟跑通

### 方案 A:Docker(推荐)

Dockerfile 已自带 PageIndex 拉取,**真的一键起**:

```bash
# 1. 配 .env
cp .env.example .env
# 编辑 .env 填入你的 CHATGPT_API_KEY
# 推荐 livetoken,详见 docs/livetoken.md

# 2. 启动
docker compose up -d

# 3. 访问
# http://localhost:8000
```

### 方案 B:本地开发(快速迭代)

```bash
# 1. 自动 setup(克隆 PageIndex + 装依赖)
chmod +x setup.sh
./setup.sh

# 2. 编辑 .env 填 API key

# 3. 启动
python run.py
# 或 uvicorn app.main:app --reload --port 8000
```

---

## 第一次使用流程

1. 访问 http://localhost:8000(默认有个简单的登录页,演示用)
2. 进「知识库」页面 → 上传 PDF
3. 后端会异步索引(看进度条):
   - PyMuPDF 抽取文本(扫描件走 RapidOCR)
   - PageIndex 按目录结构切章节
   - LLM 生成每章 description + keywords
   - 写入 `app/indexes/<filename>_structure.json`
4. 索引完成后回「聊天」页问问题
5. 系统:**LLM 看完文档章节树 → 决定看哪几章 → 读章节原文 → 生成答案**

---

## 适合什么场景

✅ **强相关**:
- 产品规格书客服(本案例的来源:光伏 / 储能 / 逆变器)
- 法律文书查询(合同 / 法规 / 判例)
- 技术手册问答(API 文档 / 安装手册 / 维修指南)
- 学术论文检索
- 中文长文档(embedding 不灵敏的场景)

❌ **不太合适**:
- 短文档 / 大量碎片(QA pair / FAQ)→ 用向量 RAG 更快
- 实时性强 / 检索量大(每次都让 LLM 推理一遍贵)
- 文档结构差(没标题层级)

---

## 目录结构

```
code/
├── README.md                # 你正在看的
├── Dockerfile               # 自带 PageIndex 拉取
├── docker-compose.yml
├── requirements.txt
├── run.py                   # 本地启动入口
├── setup.sh                 # 一键 setup 脚本
├── .env.example             # endpoint 配置模板
├── .gitignore
├── app/
│   ├── main.py              # FastAPI 入口 + WebSocket 任务推送
│   ├── indexer.py           # PageIndex 包装(切章节 + 元数据生成)
│   ├── retriever.py         # ⭐ 核心:树状检索 + LLM 推理
│   ├── spec_parser.py       # 规格参数结构化提取
│   ├── database.py          # SQLite(documents / events / library)
│   ├── task_queue.py        # 自写异步任务队列
│   ├── settings.json        # AI 配置(model / temperature / RAG 开关)
│   └── static/
│       ├── index.html       # 主界面
│       ├── login.html       # 登录页(纯演示)
│       ├── 404.html
│       ├── style.css
│       ├── manifest.json
│       ├── favicon.svg
│       └── js/
│           ├── app.js       # 主应用逻辑
│           ├── chat.js      # 聊天交互
│           ├── kb.js        # 知识库管理
│           ├── settings.js  # 设置页
│           ├── analytics.js # 数据统计
│           └── utils.js
├── knowledge/               # 用户上传的 PDF(.gitkeep 占位)
├── indexes/                 # PageIndex 生成的结构 JSON
├── data/                    # SQLite 文件
└── tests/
    └── test_api.py
```

---

## API 参考

### 上传 PDF

```bash
curl -F "file=@your_doc.pdf" \
     -F "library_id=default" \
     http://localhost:8000/api/upload
```

返回 `{"task_id": "..."}`,后端异步处理。

### 查询任务进度

```bash
curl http://localhost:8000/api/tasks/<task_id>
```

返回 `{"status": "running", "progress": 50, "message": "..."}`。

### 提问(同步)

```bash
curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "CHSM78N 的最大功率是多少?", "library_id": "default"}'
```

### 列出已索引文档

```bash
curl http://localhost:8000/api/documents
```

---

## PageIndex 工作机制(简化版)

```
PDF 上传
   ↓
1. PyMuPDF 抽文本(扫描件 fallback RapidOCR)
   ↓
2. PageIndex 按目录切章节
   structure.json:
   [
     {
       "title": "1. Overview",
       "page_range": [1, 3],
       "description": "Product overview...",
       "keywords": ["solar", "module"],
       "children": [...]
     },
     ...
   ]
   ↓
3. 入库:doc_registry + structure.json 保存
   ↓
查询时:
   LLM 看完所有 structure(树状)
   → 决定查看哪些章节
   → 读取具体页面文本
   → 生成答案
```

**关键:LLM 是检索器,不只是生成器**。这是 Vectorless 范式的核心。

---

## 配置说明

### `.env`

```bash
CHATGPT_API_KEY=sk-xxxxx     # PageIndex 标准变量名
OPENAI_API_BASE=https://livetoken.top    # 不带 /v1
```

PageIndex 默认走 OpenAI 官方,本项目通过 `OPENAI_API_BASE` 切到任意 OpenAI 协议兼容 endpoint。

### `app/settings.json`

```json
{
  "ai": {
    "model": "gpt-4o-mini",       // 索引用便宜模型
    "temperature": 0.7,
    "max_tokens": 2048,
    "rag_enabled": true,
    "logging_enabled": false
  }
}
```

可以通过设置页 UI 改,改完立刻生效(写文件)。

---

## 常见问题

### Q1. 第一次启动很慢

PageIndex 解析一个 100 页 PDF 约 30-90 秒(取决于 LLM 速度)。`task_queue` 异步处理,前端有进度条。

### Q2. 扫描件 OCR 不准

RapidOCR 是兜底,精度有限。**生产环境建议**:

- 用 PaddleOCR / Tesseract 替换
- 或者用 Gemini 多模态直接解析 PDF 图像

### Q3. 怎么换不同 LLM 跑测试?

改 `app/settings.json` 的 `model` 字段。`indexer` 和 `retriever` 都读这个配置。

### Q4. 怎么删除已索引文档?

```bash
# 1. 删 PDF 文件
rm knowledge/<filename>.pdf
# 2. 删 structure
rm indexes/<filename>_structure.json
# 3. 删 registry(通过 API 或直接 SQLite)
curl -X DELETE http://localhost:8000/api/documents/<filename>
```

### Q5. 跟 02-industry-cases/06 那个 Chroma 版本怎么选?

| 场景 | 用哪个 |
|---|---|
| 短文档 / FAQ / 通用 | #6 Chroma 向量 RAG |
| 长结构化文档 | **#7 PageIndex Vectorless** |
| 中文场景 + embedding 差 | **#7 PageIndex** |
| 高并发 / 实时 | #6 Chroma |
| 文档数 1000+ | #6 Chroma(预算上限) |
| 文档数 < 100 / 高精度 | **#7 PageIndex** |

---

## 致谢

- **[PageIndex](https://github.com/VectifyAI/PageIndex)** by Vectify AI(MIT License)—— Vectorless Reasoning-based RAG 核心库
- **FastAPI** —— 后端框架
- **RapidOCR** —— OCR 引擎

---

## License

本项目代码 MIT — 详见 [../../../LICENSE](../../../LICENSE)。

PageIndex 部分遵循其原 MIT 许可。
