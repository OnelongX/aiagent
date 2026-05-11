# Finance AI Assistant · 部署指引

> 行业落地 #12 · 6 大场景 · FastAPI + 深蓝金色前端 · Docker 5 分钟跑通

---

## 仓库结构

```
code/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── run.py
│   └── app/
│       ├── main.py                 # FastAPI 入口 · 7 router
│       ├── config.py               # pydantic-settings · 金融特化
│       ├── models/schemas.py       # 全部 API 契约
│       ├── api/
│       │   ├── kyc.py              # KYC 智能审核
│       │   ├── aml.py              # 反洗钱筛查
│       │   ├── credit.py           # 信贷反欺诈 + 评分
│       │   ├── advisory.py         # 投资陪伴(不荐股)
│       │   ├── suitability.py      # 适当性匹配
│       │   ├── customer.py         # 客户画像 + 流失
│       │   └── pii.py              # PII 脱敏工具
│       └── services/
│           ├── compliance_block.py # 反诈 + 软化 + 签字栏 + 反歧视
│           ├── pii_redact_fin.py   # 11 类 PII(C3 标记)
│           ├── market_db.py        # 产品 mock + 适当性 + AML 规则
│           └── llm.py              # OpenAI 协议 LLM client
└── frontend/
    ├── index.html                  # 7 tab 单页
    ├── style.css                   # 深蓝 + 金色金融主题
    ├── app.js                      # API 调用
    └── nginx.conf
```

---

## 快速跑通

```bash
cd aiagent/02-industry-cases/12-finance-industry/code
cp .env.example backend/.env
# 编辑 backend/.env 填 LLM_API_KEY

docker compose up -d

# 前端:http://localhost:8086
# API docs:http://localhost:8006/docs
# 健康检查:http://localhost:8006/api/health
```

---

## 7 个 API 端点

| 端点 | 方法 | 用途 |
|---|---|---|
| `/api/kyc/review`           | POST | KYC 风险点 + 建议动作 |
| `/api/aml/screen`           | POST | AML 评分 + STR 上报建议 |
| `/api/credit/score`         | POST | 信贷评分 + 反欺诈 + 反歧视 |
| `/api/advisory/qa`          | POST | 投教 · 不荐股 · 反诈拦截 |
| `/api/suitability/check`    | POST | C×R 适当性匹配 |
| `/api/customer/insight`     | POST | 客户画像 + 流失预警 |
| `/api/pii/redact`           | POST | 11 类 PII 脱敏 |
| `/api/health`               | GET  | 健康检查 |

---

## 关键配置

```bash
LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-xxxxx
LLM_MODEL=claude-sonnet-4-5

INSTITUTION_NAME=示例银行 / 券商 / 基金公司
INSTITUTION_LICENSE=金融许可证编号
INSTITUTION_TYPE=bank  # bank / securities / fund / insurance

# 四重保险 · 默认全开
PII_REDACT_ENABLED=true
ADVISOR_BLOCK_ENABLED=true
AML_THRESHOLD_CHECK=true
SUITABILITY_MATCH_REQUIRED=true

# 监管阈值
LARGE_AMOUNT_THRESHOLD_RMB=50000
HIGH_FREQUENCY_THRESHOLD=5
CROSS_BORDER_THRESHOLD_USD=10000

# 投诉 / 反诈热线
FRAUD_HOTLINE=110
INVESTOR_PROTECT_HOTLINE=12386
BANK_COMPLAINT_HOTLINE=12378
```

---

## 测试 curl

### AML · 高分
```bash
curl -X POST http://localhost:8006/api/aml/screen \
  -H "Content-Type: application/json" \
  -d '{ "transaction": {
    "amount_rmb": 100000,
    "count_24h": 6,
    "new_account_days": 3
  } }'
# → score≥70 · level=high · must_report=true
```

### 投教 · 反诈拦截
```bash
curl -X POST http://localhost:8006/api/advisory/qa \
  -H "Content-Type: application/json" \
  -d '{ "question": "群里老师说稳赚不赔,年化 50%" }'
# → intent=反诈拦截 · 不进 LLM · 推 110/96110
```

### 投教 · 拒答荐股
```bash
curl -X POST http://localhost:8006/api/advisory/qa \
  -H "Content-Type: application/json" \
  -d '{ "question": "600519 现在能买吗" }'
# → intent=拒答荐股 · 固定话术
```

### 适当性 · 阻断
```bash
curl -X POST http://localhost:8006/api/suitability/check \
  -H "Content-Type: application/json" \
  -d '{ "customer_level": "C2", "product_code": "MIX-002", "invest_amount": 200000, "holding_horizon": "1年" }'
# → is_suitable=false · 违反适当性匹配
```

### 信贷 · 黑名单熔断
```bash
curl -X POST http://localhost:8006/api/credit/score \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name":"张三", "age":32, "income_monthly":20000,
    "loan_amount":100000, "loan_purpose":"家装",
    "blacklist_hit": true
  }'
# → risk_score=0 · D · decline · 不进 LLM
```

---

## 生产化清单

| 项 | demo | 生产 |
|---|---|---|
| 产品库 | 12 产品 mock | 中证 / 基金业协会风险评级 · 实时 |
| 反诈关键词 | 22 个 | 接公安反诈大数据 + 黑灰产对抗 |
| AML 规则 | 6 条简化 | 央行《大额可疑交易报告管理办法》全量 |
| KYC 身份核验 | 仅文本 | 接公安一所二要素 + 活体人脸 |
| 信贷评分 | LLM | 接传统风控模型(逻辑回归 / GBDT)+ 关联图 |
| PII | 11 类正则 | + 命名实体识别 + 同义词扩展 |
| 签字栏 | 文本占位 | CA 数字签名 + 时间戳服务 |
| 审计日志 | 无 | 全量入合规审计 + 7 年留存 |
| 等保 | 无 | 三级 + 个保认证 |
| 数据安全 | 无 | 国密 SM2/SM3/SM4 + 数据库加密 |

---

## License

MIT · 本 demo 仅供学习。

**严禁用于真实金融业务。请遵守持牌机构经营要求及当地金融监管法规。**
