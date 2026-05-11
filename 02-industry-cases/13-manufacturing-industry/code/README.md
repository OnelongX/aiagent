# Manufacturing AI Assistant · 部署指引

> 行业落地 #13 · 6 大场景 · FastAPI + 工业橙前端 · Docker 5 分钟跑通

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
│       ├── main.py                # FastAPI 入口 · 7 router
│       ├── config.py              # pydantic-settings · 工厂特化
│       ├── models/schemas.py      # 全部 API 契约
│       ├── api/
│       │   ├── mes_qa.py          # MES 自然语言问答
│       │   ├── process.py         # 工艺参数推荐
│       │   ├── qc.py              # 质检视觉
│       │   ├── pdm.py             # 预测性维护
│       │   ├── scheduling.py      # 排程辅助
│       │   ├── sop_ecn.py         # SOP / ECN 知识
│       │   └── pii.py             # PII / 商业秘密脱敏
│       └── services/
│           ├── process_guard.py    # 签字栏 + 物理边界 + 安全熔断 + 软化
│           ├── pii_redact_mfg.py   # 8 类 PII(SN/Lot/客户料号)
│           ├── mes_mock.py         # MES + SOP + 设备健康度 mock
│           └── llm.py              # OpenAI 协议 LLM client
└── frontend/
    ├── index.html                 # 7 tab 单页
    ├── style.css                  # 工业橙 / 钢铁主题
    ├── app.js                     # API 调用
    └── nginx.conf
```

---

## 快速跑通

```bash
cd aiagent/02-industry-cases/13-manufacturing-industry/code
cp .env.example backend/.env
# 编辑 backend/.env 填 LLM_API_KEY

docker compose up -d

# 前端:http://localhost:8087
# API docs:http://localhost:8007/docs
# 健康检查:http://localhost:8007/api/health
```

---

## 7 个 API 端点

| 端点 | 方法 | 用途 |
|---|---|---|
| `/api/mes/qa`              | POST | 自然语言查 MES 数据 |
| `/api/process/recommend`   | POST | 工艺参数推荐 + 边界检查 |
| `/api/qc/inspect`          | POST | 质检初判(必须 QC 终判)|
| `/api/pdm/check`           | POST | 设备健康度 + 维护建议 |
| `/api/scheduling/plan`     | POST | 订单排程(贪心 demo)|
| `/api/sop/qa`              | POST | SOP / ECN 知识问答 |
| `/api/pii/redact`          | POST | 8 类 PII / 商业秘密脱敏 |
| `/api/health`              | GET  | 健康检查 |

---

## 关键配置

```bash
LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-xxxxx
LLM_MODEL=claude-sonnet-4-5

FACTORY_NAME=示例工厂
WORKSHOP=示例车间
LINE_CODE=L01
PROCESS_ENGINEER=示例工艺工程师

# 五重保险 · 默认全开
PII_REDACT_ENABLED=true
PROCESS_BOUNDARY_ENFORCED=true
QC_DOUBLE_CHECK_REQUIRED=true
MES_READONLY_MODE=true
RECIPE_SECRET_MASK=true

USER_WORKSHOP=*   # * 或 WS-A / WS-B / WS-C / WS-D

SAFETY_HOTLINE=119
ESHS_HOTLINE=厂内 EHS 分机 8888
```

---

## 测试 curl

### MES 问答(良率)
```bash
curl -X POST http://localhost:8007/api/mes/qa \
  -H "Content-Type: application/json" \
  -d '{ "question": "L-A1 昨天良率多少", "workshop_scope": "*" }'
```

### 工艺参数(越界拦截)
```bash
curl -X POST http://localhost:8007/api/process/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "line_code": "L-A2",
    "process_step": "sinter",
    "target_yield": 0.985,
    "current_params": {"sinter_temp_c": 700, "sinter_time_min": 60},
    "issue_desc": "良率从 0.97 跌到 0.93"
  }'
# 如 LLM 推荐 900°C → boundary_violations 命中(上限 850°C)
```

### PdM(安全熔断)
```bash
curl -X POST http://localhost:8007/api/pdm/check \
  -H "Content-Type: application/json" \
  -d '{ "line_code": "L-A1", "extra_observations": "氢气泄漏报警,急停按下" }'
# → 不进 LLM · 直接 EHS 响应
```

### SOP / ECN(版本号引用)
```bash
curl -X POST http://localhost:8007/api/sop/qa \
  -H "Content-Type: application/json" \
  -d '{ "question": "ECN-2026-038 影响哪些 WIP?", "line_code": "L-A1" }'
# → cite_docs 含 doc_id + version + effective_date
# → answer 自动附 impact 列表
```

### 排程(贪心)
```bash
curl -X POST http://localhost:8007/api/scheduling/plan \
  -H "Content-Type: application/json" \
  -d '{
    "orders": [
      {"order_id":"SO-001","product":"PN-A","qty":3000,"due_date":"2026-05-20","priority":"urgent"}
    ],
    "available_lines": ["L-A1", "L-A2"],
    "horizon_days": 14
  }'
```

### PII / 商业秘密
```bash
curl -X POST http://localhost:8007/api/pii/redact \
  -H "Content-Type: application/json" \
  -d '{ "text": "客户料号 PN-A0815, Lot-001, SN-A0815-998877" }'
# → trade_secret_detected=true · 3 个 SECRET_KEYS
```

---

## 生产化清单

| 项 | demo | 生产 |
|---|---|---|
| MES 接入 | 内置 mock | SAP MES / 西门子 Opcenter / 鼎捷 / 用友 / 自研 |
| 时序数据 | 静态 mock | InfluxDB / TimescaleDB / Pi |
| 设备数据 | 静态 mock | OPC-UA / Modbus / EtherNet/IP |
| 视觉模型 | 仅 LLM 文本 | 接 YOLOv8 / Mask R-CNN / 工业相机 |
| LLM | 公有云 | **私有部署 vLLM + Qwen/DeepSeek**(工艺机密必须内网)|
| 排程 | 贪心 demo | OR-Tools / Gurobi / SAP APO |
| 工艺边界 | 12 工序 | 工艺手册全量录入 + 工艺工程师签字 |
| 审计日志 | 无 | 全量入 ELK · 留存 ≥3 年(IATF 16949) |
| 等保 | 无 | 工业控制系统三级 |

---

## License

MIT · 本 demo 仅供学习。

**严禁用于真实生产线下发指令。请遵守 ISO 9001 / IATF 16949 / 安全生产法及工厂内部 SOP。**
