# Medical AI Assistant · 部署指引

> 行业落地 #11 · 6 大场景 · FastAPI + 蓝白前端 · Docker 5 分钟跑通

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
│       ├── main.py             # FastAPI 入口 · 7 router
│       ├── config.py           # pydantic-settings · 医疗特化
│       ├── models/schemas.py   # 全部 API 契约
│       ├── api/
│       │   ├── imaging.py      # 影像辅助
│       │   ├── triage.py       # 智能分诊
│       │   ├── medication.py   # 用药审查
│       │   ├── discharge.py    # 出院小结
│       │   ├── cdss.py         # 临床决策支持
│       │   ├── education.py    # 患者科普
│       │   └── pii.py          # PII 脱敏工具
│       └── services/
│           ├── doctor_block.py    # 急救熔断 + 签字栏 + 软化
│           ├── pii_redact_med.py  # 10 类 PII(加 4 类医疗 ID)
│           ├── drug_db.py         # 药品 mock · 15 药 6 相互作用
│           └── llm.py             # OpenAI 协议 LLM client
└── frontend/
    ├── index.html              # 7 tab 单页
    ├── style.css               # 蓝白医疗主题
    ├── app.js                  # API 调用
    └── nginx.conf
```

---

## 快速跑通

```bash
# 1. 进入目录
cd aiagent/02-industry-cases/11-medical-industry/code

# 2. 配 LLM key
cp .env.example backend/.env
# 编辑 backend/.env 填 LLM_API_KEY

# 3. 启动
docker compose up -d

# 4. 访问
# 前端:http://localhost:8085
# API docs:http://localhost:8005/docs
# 健康检查:http://localhost:8005/api/health
```

---

## 7 个 API 端点

| 端点 | 方法 | 用途 |
|---|---|---|
| `/api/imaging/review`   | POST | 影像建议复核 · 不出诊断 |
| `/api/triage/`          | POST | ESI 5 级分诊 · 急救熔断 |
| `/api/medication/check` | POST | 用药相互作用 + 特殊人群 |
| `/api/discharge/summary`| POST | 出院小结 AI 起草 + 签字栏 |
| `/api/cdss/`            | POST | 临床决策提示 |
| `/api/education/qa`     | POST | 患者科普 + 首诊转线下 |
| `/api/pii/redact`       | POST | 10 类 PII 脱敏 |
| `/api/health`           | GET  | 健康检查 |

---

## 关键配置

`.env` 全部开关:

```bash
LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-xxxxx
LLM_MODEL=claude-sonnet-4-5

HOSPITAL_NAME=示例医院
DEPARTMENT=示例科室
DOCTOR_NAME=示例医师
DOCTOR_LICENSE=1100000000000000

# 三重保险 · 默认全开
PII_REDACT_ENABLED=true
EMERGENCY_INTERCEPT_ENABLED=true
DOCTOR_REVIEW_REQUIRED=true
DRUG_DB_VERIFY_ENABLED=true

EMERGENCY_PHONE=120
POISON_HOTLINE=010-83132345
MENTAL_HOTLINE=400-161-9995
```

---

## 测试 curl

### 影像辅助
```bash
curl -X POST http://localhost:8005/api/imaging/review \
  -H "Content-Type: application/json" \
  -d '{
    "modality": "CT",
    "body_part": "胸部",
    "clinical_history": "患者 65 岁,长期吸烟史",
    "findings_text": "右肺上叶可见 8mm 结节"
  }'
```

### 分诊(急救)
```bash
curl -X POST http://localhost:8005/api/triage/ \
  -H "Content-Type: application/json" \
  -d '{
    "age": 55, "sex": "male",
    "chief_complaint": "胸痛大汗 1 小时"
  }'
# → esi_level=1 · 红色 · 推 120
```

### 用药审查(冲突)
```bash
curl -X POST http://localhost:8005/api/medication/check \
  -H "Content-Type: application/json" \
  -d '{
    "drugs": ["华法林", "阿司匹林", "奥美拉唑"],
    "patient_age": 68
  }'
# → high 出血叠加 + moderate 氯吡格雷-PPI(若有)
```

### 商品名拦截
```bash
curl -X POST http://localhost:8005/api/medication/check \
  -H "Content-Type: application/json" \
  -d '{ "drugs": ["立普妥"] }'
# → type=commercial_name · 建议改用阿托伐他汀
```

### 患者科普(心理危机)
```bash
curl -X POST http://localhost:8005/api/education/qa \
  -H "Content-Type: application/json" \
  -d '{ "question": "我已经不想活了" }'
# → intent=心理危机 · 不进 LLM · 直接推热线
```

---

## 生产化清单

| 项 | demo | 生产 |
|---|---|---|
| 药品数据库 | 15 药 mock | 国家药监数据库 / 国家基药目录 / Drugs.com |
| 影像 AI 模型 | 仅 LLM 文本 | 接 DICOM PACS + 专用模型(联影 / 数坤 / 推想) |
| 急救熔断词 | 38 个 | 接卫健委急救分级标准 |
| ESI 评级 | LLM | 接专业分诊算法(ESI v4 表) |
| PII | 10 类正则 | + 命名实体识别 + 同义词扩展 |
| 签字栏 | 文本占位 | 接 CA 数字签名 + 时间戳 |
| 审计日志 | 无 | 全量入 ELK + 操作可追溯 |
| 等保 | 无 | 三级 + HIPAA(出海) + GDPR |

---

## License

MIT · 本 demo 仅供学习。

**严禁用于真实临床诊疗。请遵守《医师法》《处方管理办法》《互联网诊疗管理办法》及当地卫健委细则。**
