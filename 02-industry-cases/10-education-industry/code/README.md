# education-ai-assistant — 教育行业 AI 助理最小可跑示例

> 5 分钟跑通 · Docker 一键起 · 4 大场景 + 7 条工程纪律

---

## 这是什么

行业落地系列**第 10 篇**的配套代码。7 个 API + 教育行业特化纪律:

- 📝 **客观题判分** —— 规则匹配 · 不走 LLM · 立即省 30-50% 批改时间
- ✍️ **作文批改** —— 4 维度 LLM 初评 + 教师二审 + 敏感话题预扫描
- 📊 **学情分析** —— 班级薄弱 TOP 5 + 教学建议 · 不输出个人成绩
- 📨 **周报草稿** —— LLM 起草 + 5 红线检测 + 教师签字栏
- 💬 **家长答疑** —— 5 类意图分流 · 孩子表现 / 焦虑 / 经济 走特殊路径
- 🎯 **个性化推荐** —— 难度梯度 + 多样性 + **双减时长上限**
- 🔒 **PII 脱敏** —— 教育版(学号/班级/学校/家长 + 标记未成年数据)

📖 完整工程决策见 [上级 README](../README.md)。

---

## 5 分钟跑通

```bash
# 1. 配 endpoint
cp .env.example backend/.env
# 编辑 backend/.env 填 LLM_API_KEY

# 2. 启动
docker compose up -d

# 3. 访问
# http://localhost:8084  前端
# http://localhost:8004/docs  API 文档
```

---

## 7 大 API 速览

### 客观题判分(不走 LLM)

```bash
curl -X POST http://localhost:8004/api/grade/objective \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      {"question_id":"Q1","type":"multiple_choice","student_answer":"B","correct_answer":"B"}
    ]
  }'
```

### 作文批改(LLM 初评 + 必教师二审 + 敏感话题预扫)

```bash
curl -X POST http://localhost:8004/api/grade/essay \
  -d '{"question_id":"E1","prompt":"我最难忘的一件事","student_answer":"..."}'
```

如果作文里出现「想离开这个世界」等关键词 → **AI 不予自动评分** · 返回 `sensitive_flag` · 必须教师亲自阅读。

### 学情分析(班级薄弱 + 不输出个人)

```bash
curl -X POST http://localhost:8004/api/analytics/class \
  -d '{
    "class_id": "C1",
    "results": [
      {"student_id":"S1","knowledge_point":"一元一次方程","correct":false}
    ]
  }'
```

### 周报草稿(5 红线检测)

```bash
curl -X POST http://localhost:8004/api/communication/weekly-report \
  -d '{
    "class_id":"C1",
    "learning_data":{"overall_rate":0.78}
  }'
```

返回的 `issues[]` 列出检测到的禁忌(公开比较/标签化/焦虑诱导/越权评价/经济压力)。

### 家长答疑(意图分流)

```bash
curl -X POST http://localhost:8004/api/communication/parent-qa \
  -d '{"question":"我家孩子这次考几分?"}'
```

- 「孩子表现」类 → 不直答 + 推班主任
- 「教育焦虑」类 → 引导性回复 + 心理援助
- 「经济咨询」类 → 不推任何付费课程

### 个性化推荐(双减对齐)

```bash
curl -X POST http://localhost:8004/api/recommend \
  -d '{
    "student_id":"S001",
    "subject":"数学",
    "weak_points":["一元一次方程"],
    "current_mastery":{"一元一次方程":0.42}
  }'
```

返回 `daily_load_cap_minutes`(小学 60 / 初中 90 / 高中 120)。

### 教育版 PII 脱敏

```bash
curl -X POST http://localhost:8004/api/pii/redact \
  -d '{"text":"三年级二班学生张三, 家长王芳手机 138..."}'
```

返回 `minor_data_detected=true` 时,提示需要家长同意 + 私有部署。

---

## 目录结构

```
code/
├── docker-compose.yml
├── .env.example
├── README.md
└── backend/
    ├── Dockerfile · requirements.txt · run.py
    └── app/
        ├── main.py · config.py
        ├── api/  (5 个 router · 7 个 endpoint)
        │   ├── grade.py        POST /api/grade/objective + /essay
        │   ├── analytics.py    POST /api/analytics/class
        │   ├── communication.py POST /api/communication/weekly-report + /parent-qa
        │   ├── recommend.py    POST /api/recommend
        │   └── pii.py          POST /api/pii/redact
        ├── services/
        │   ├── llm.py
        │   ├── pii_redact_edu.py  ⭐ 教育版 PII(更严)
        │   └── teacher_block.py   ⭐ 签字栏 / 红线 / 焦虑 / 软化 / 双减
        └── models/schemas.py     ⭐ 字段契约
└── frontend/
    ├── nginx.conf
    ├── index.html              (7 tab 单页)
    ├── style.css
    └── js/app.js
```

---

## 7 条教育纪律 → 代码体现

| 纪律 | 代码 | 验证 |
|---|---|---|
| 未成年 PII 脱敏 | `pii_redact_edu.py` | 学号/班级/学校/家长 全识别 + minor flag |
| 标签温和 | `teacher_block.py::soften_labels` | 8 个负面词替换 |
| 不公开个人评价 | `analytics.py::class_analytics` | 只输出班级 · 不出个人 |
| 主观题教师二审 | `grade.py::grade_essay` | `requires_teacher_review=True` |
| 焦虑监控 | `teacher_block.py::is_anxiety_signal` | 12 关键词 + 引导回复 |
| 敏感话题人审 | `teacher_block.py::detect_sensitive_topic` | 5 类话题 · 不进 LLM 评分 |
| 不推付费 | `teacher_block.py::has_commercial_content` | 8 关键词拦截 |

---

## 配置

```bash
# backend/.env

LLM_API_BASE=https://livetoken.top
LLM_API_KEY=sk-xxxxx
LLM_MODEL=claude-sonnet-4-5

SCHOOL_NAME=示例学校
TEACHER_NAME=示例教师

# 学段(影响推荐时长上限)
GRADE_STAGE=junior_high       # primary / junior_high / senior_high

# 教育合规(默认全开)
PII_REDACT_ENABLED=true
PARENT_CONSENT_REQUIRED=true
DOUBLE_REDUCTION_MODE=true
```

---

## 自测

```bash
# PII 脱敏自测
python backend/app/services/pii_redact_edu.py

# 健康检查(看合规开关状态)
curl http://localhost:8004/api/health
# 期望 components 含:
# pii_redact: enabled
# double_reduction: enabled
```

---

## 常见问题

### Q1. 客观题怎么实现自动判分?

`grade_objective` 用规则匹配(`_normalize` 处理大小写/标点/全半角)。**不走 LLM**,毫秒级响应。

### Q2. 作文批改的"敏感话题"具体检测什么?

`detect_sensitive_topic` 检测 5 类:
- self_harm(自伤倾向)
- family_loss(亲人去世)
- abuse(身体/性侵害)
- depression(抑郁信号)
- family_change(父母离异)

**触发任一关键词 → 不进 LLM 评分 · 标记 sensitive_flag · 教师必须人审**。

### Q3. 双减时长上限怎么生效?

`recommend` 根据 `.env` 的 `GRADE_STAGE` 自动返回:
- 小学:60 分钟
- 初中:90 分钟
- 高中:120 分钟

前端可以基于这个值显示「今日推荐学习时长不超过 X 分钟」。

### Q4. 怎么对接学校 LMS?

替换 mock 数据源:
- `recommend.py::MOCK_EXERCISES` → 接学校题库
- `analytics.py::class_analytics` → 接 LMS 作业系统

---

## License

MIT — 跟主仓库一致。

**本工具是教师辅助 · 不替代教师专业判断。请遵守未成年人保护法 / 教育数据规范 / 双减政策。**
