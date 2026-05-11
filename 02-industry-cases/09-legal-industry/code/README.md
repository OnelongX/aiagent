# legal-ai-assistant — 法律行业 AI 助理最小可跑示例

> 5 分钟跑通 · Docker 一键起 · 5 大场景 + 6 条工程纪律

---

## 这是什么

行业落地系列**第 9 篇**的配套代码。6 个 API + 法律行业特化的工程纪律:

- 📋 **合同审查** —— 风险评级 + PII 脱敏 + 软化建议性语言
- ⚖️ **类案检索** —— 真实判例库 + 审级权威加权 + 跨地区警告
- 📝 **文书起草** —— 6 种模板 + 律师签字栏 + 法条验真
- 💬 **法律咨询** —— 5 类意图分流 + 应急拦截 + 强制免责
- 📰 **法规追踪** —— 多源订阅 + 业务匹配 + LLM 影响分析
- 🔒 **PII 脱敏** —— 身份证/手机/邮箱/银行卡/地址/姓名

📖 完整工程决策见 [上级 README](../README.md)。

---

## 5 分钟跑通

```bash
# 1. 配 endpoint
cp .env.example backend/.env
# 编辑 backend/.env 填 LLM_API_KEY(推荐 livetoken)

# 2. 启动
docker compose up -d

# 3. 访问
# http://localhost:8083  前端
# http://localhost:8003/docs  API 文档
```

---

## 6 大场景速览

### 1. 合同审查

```bash
curl -X POST http://localhost:8003/api/contract/review \
  -H "Content-Type: application/json" \
  -d '{
    "contract_text": "甲方应当...",
    "contract_type": "SaaS",
    "jurisdiction": "中国大陆",
    "party_role": "乙方"
  }'
```

返回 `overall_level + risks[] + summary`。每个 risk 标 `ai_drafted=true`,提醒律师审核。

### 2. 类案检索

```bash
curl -X POST http://localhost:8003/api/cases/search \
  -H "Content-Type: application/json" \
  -d '{
    "case_facts": "(脱敏)A 向 B 借款...",
    "claim_type": "民间借贷",
    "top_k": 10
  }'
```

返回 `cases[]`(含案号 / 审级 / 相似度 / 跨地区警告)。

### 3. 文书起草

```bash
curl -X POST http://localhost:8003/api/drafting/generate \
  -H "Content-Type: application/json" \
  -d '{
    "document_type": "民事起诉状",
    "case_info": {"原告": "[作者填入]", "案由": "民间借贷"}
  }'
```

返回的文书**自动加律师签字栏 + 末尾 AI 协助声明**。

### 4. 法律咨询(边界最严)

```bash
curl -X POST http://localhost:8003/api/qa \
  -H "Content-Type: application/json" \
  -d '{"question": "民法典关于借贷的条款是什么?"}'
```

意图分类:
- **普法** → 正常回答 + 强制免责声明
- **个案咨询** → 改写为科普 + 强烈推荐律师
- **刑事相关** → 拒绝分析 + 推刑事辩护律师
- **应急情况** → **立即拦截 · 推 110 / 12348**

### 5. 法规追踪

```bash
curl -X POST http://localhost:8003/api/regulation/track \
  -H "Content-Type: application/json" \
  -d '{
    "days": 7,
    "business_keywords": ["数据出境", "跨境支付"]
  }'
```

LLM 给出**初步影响分析**,必须律师审批后才能发客户。

### 6. PII 脱敏(独立工具)

```bash
curl -X POST http://localhost:8003/api/pii/redact \
  -H "Content-Type: application/json" \
  -d '{
    "text": "原告张三身份证 110101199001011234"
  }'
```

返回脱敏后文本 + 实体清单。**身份证 / 手机 / 邮箱 / 银行卡 / 地址 / 中文姓名 全识别**。

---

## 目录结构

```
code/
├── docker-compose.yml          # 一键启动
├── .env.example                # 配置模板
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run.py
│   └── app/
│       ├── main.py
│       ├── config.py           # pydantic-settings
│       ├── api/
│       │   ├── contract.py     # 合同审查
│       │   ├── cases.py        # 类案检索
│       │   ├── drafting.py     # 文书起草
│       │   ├── qa.py           # 法律咨询
│       │   ├── regulation.py   # 法规追踪
│       │   └── pii.py          # PII 脱敏
│       ├── services/
│       │   ├── llm.py          # OpenAI 协议封装
│       │   ├── legal_db.py     # ⭐ 法条 / 判例数据库(含 mock)
│       │   ├── pii_redact.py   # ⭐ 6 类 PII 正则脱敏
│       │   └── lawyer_block.py # ⭐ 签字栏 + 免责 + 应急 + 软化
│       └── models/schemas.py   # ⭐ 字段契约
└── frontend/
    ├── nginx.conf
    ├── index.html              # 6 tab 单页
    ├── style.css
    └── js/app.js               # 纯 JS · 无框架
```

---

## 6 大工程纪律 → 代码落地

| 纪律 | 代码位置 | 实现 |
|---|---|---|
| **法条必须真实可查** | `services/legal_db.py::verify_article` | mock 数据库 · 生产接北大法宝 |
| **律师签字栏(强制)** | `services/lawyer_block.py::sign_block` | 文书顶部自动注入 |
| **免责声明(强制)** | `services/lawyer_block.py::qa_disclaimer` | 末尾自动追加 |
| **应急情况拦截** | `services/lawyer_block.py::is_emergency` | 关键词 · 不进 LLM |
| **PII 双重脱敏** | `services/pii_redact.py` | 6 类正则 + GDPR/PIPL |
| **建议性语言软化** | `services/lawyer_block.py::soften_advice` | 12 个禁词 → 科普性表达 |

---

## 关键配置

### `.env`

```bash
# LLM endpoint(推荐 livetoken)
LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-xxxxx
LLM_MODEL=claude-sonnet-4-5

# 律所信息(用于签字栏)
LAW_FIRM_NAME=示例律师事务所
LAW_FIRM_LICENSE=

# 法律数据库(生产环境填写)
PKULAW_API_KEY=
WESTLAW_API_KEY=

# PII 脱敏开关(默认开)
PII_REDACT_ENABLED=true
```

### 切换模型

改 `.env` 的 `LLM_MODEL`:
- `claude-sonnet-4-5` —— 法律推理(推荐)
- `claude-opus-4-5` —— 复杂法律意见书
- `gpt-5` —— 结构化条款提取(快)
- `gemini-2.5-pro` —— 扫描件 PDF 多模态

---

## 接生产数据库

本 demo 用 mock 数据。生产环境需要替换 `services/legal_db.py`:

```python
# 北大法宝(付费 · 推荐律所)
async def verify_article(statute, article_number):
    headers = {"Authorization": f"Bearer {settings.pkulaw_api_key}"}
    async with httpx.AsyncClient() as c:
        r = await c.get("https://api.pkulaw.com/...", params={...}, headers=headers)
        if r.status_code == 200:
            return LegalArticle(..., verified=True)
    return None

# 国家法律法规数据库(免费 · 限速)
async def search_articles(keywords, jurisdiction):
    async with httpx.AsyncClient() as c:
        r = await c.get("https://flk.npc.gov.cn/api/...", params={...})
        ...
```

---

## 律所部署模板

**关键纪律**:律所内部用必须**私有部署**(《数据安全法》司法数据合规)。

```bash
# 1. 私有服务器(不上公有云)
# 2. 改 docker-compose.yml 的 endpoint 为 OpenAI 官方 · 或 livetoken 私有部署版
# 3. 加 SSO 接入律所域账号
# 4. 接律所案件管理系统(同步客户档案)
# 5. 接律师电子签系统(法大大 / e签宝)
```

---

## 自测脚本

```bash
# PII 脱敏自测
python backend/app/services/pii_redact.py

# 健康检查
curl http://localhost:8003/api/health
# → {
#     "status": "ok",
#     "components": {
#       "llm_client": "ok",
#       "pii_redact": "enabled",
#       "legal_db": "ok (mock)"
#     }
#   }
```

---

## 常见问题

### Q1. 法律数据库要付费吗?

- **国家法律法规数据库**:免费(限速 · 公开 API)
- **裁判文书网**:免费(限速 · 需爬取)
- **北大法宝 / 威科先行**:付费(律所推荐)
- **本 demo**:用 mock 演示,生产环境必接真实数据库

### Q2. PII 识别准吗?

正则版本召回 85-95%(身份证 / 手机 / 邮箱基本不漏)。**生产环境建议加 NER 模型**(spaCy / HanLP / paddleNLP)提升中文姓名识别。

### Q3. 律师签字栏怎么对接电子签?

签字栏占位 + 律师扫码 → 法大大 / e签宝签字 → 文档归档。本仓库只做生成,具体签字流程需对接客户的电子签服务。

### Q4. 应急拦截会误伤吗?

关键词列表 `EMERGENCY_KEYWORDS` 偏严格(宁可误伤)。生产环境可以加 LLM 二次判断。

### Q5. 怎么换不同律所?

改 `.env` 里 `LAW_FIRM_NAME` 和 `LAW_FIRM_LICENSE`,签字栏自动适配。一个 codebase 多律所部署很简单。

---

## License

MIT — 跟主仓库一致。详见 [../../../LICENSE](../../../LICENSE)。

**本工具是律师辅助 · 不是律师替代。AI 输出 · 律师签字 · 律师担责。**
