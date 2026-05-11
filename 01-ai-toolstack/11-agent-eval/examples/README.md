# Agent Eval Examples

跟随 [AI 工具栈 #11](../README.md) 的可跑代码。

## 文件清单

| 文件 | 干什么 | 依赖 |
|---|---|---|
| `01_ragas_basic.py`     | RAGAS 4 指标 Hello World | `ragas datasets` |
| `02_ragas_ci.py`        | RAGAS + 阈值 + drift 检测 + CI 阻断 | `ragas datasets` |
| `03_phoenix_basic.py`   | Phoenix 自动 trace + 本地 UI | `arize-phoenix openinference-instrumentation-openai` |
| `04_phoenix_eval.py`    | Phoenix LLM-as-Judge 评测合规 | 同上 + `pandas` |
| `05_langfuse_basic.py`  | Langfuse 装饰器 trace + Prompt 管理 | `langfuse openai` · 需要 docker run langfuse |
| `06_openai_tracing.py`  | OpenAI Agents SDK 零配置 trace | `openai-agents` |
| `07_full_pipeline.py`   | **端到端 Eval 管线** · CI 集成范例 | `ragas datasets` |
| `08_drift_monitor.py`   | 生产环境 drift 监控 + Slack 告警 | `langfuse` |
| `golden_set.json`       | 黄金例子样本(5 条参考) | – |

## 快速开始

```bash
# 1. RAGAS Hello World
pip install ragas datasets
python 01_ragas_basic.py

# 2. Phoenix 本地 UI
pip install arize-phoenix openinference-instrumentation-openai
python 03_phoenix_basic.py
# 浏览器开 http://localhost:6006

# 3. Langfuse self-host(可选)
docker run -p 3000:3000 langfuse/langfuse:latest
# UI 创建 project · 拿 keys
export LANGFUSE_SECRET_KEY=sk-...
export LANGFUSE_PUBLIC_KEY=pk-...
python 05_langfuse_basic.py

# 4. 完整管线
python 07_full_pipeline.py
# exit 0 = 通过 · exit 1 = 阻断
```

## CI 集成参考

```yaml
# .github/workflows/eval.yml
name: Eval
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install ragas datasets openai
      - run: python examples/07_full_pipeline.py
        env:
          OPENAI_API_KEY:  ${{ secrets.OPENAI_API_KEY }}
          OPENAI_BASE_URL: https://livetoken.top/v1
```

任一 PR 改了 prompt / 模型 / 工具 → 自动跑 → 跌 5% 立刻红灯。
