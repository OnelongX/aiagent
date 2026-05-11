"""Phoenix · 自动 trace + 本地 UI

依赖:pip install arize-phoenix openinference-instrumentation-openai
预期:浏览器开 http://localhost:6006 看 trace
"""
import phoenix as px
from openinference.instrumentation.openai import OpenAIInstrumentor
from openai import OpenAI


# 1. 启动本地 UI(Postgres + Web)
print("启动 Phoenix UI · 浏览器打开 http://localhost:6006")
session = px.launch_app()

# 2. 装 instrumentor · 一行覆盖所有 OpenAI 调用
OpenAIInstrumentor().instrument()

# 3. 正常调 LLM · 自动 trace
client = OpenAI()

for q in [
    "什么是 Subagent",
    "Claude SDK 跟 OpenAI SDK 区别",
    "RAG 怎么做评测",
]:
    resp = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": q}],
    )
    print(f"Q: {q}")
    print(f"A: {resp.choices[0].message.content[:80]}...\n")

print("\n打开浏览器 → http://localhost:6006 看 3 条 trace")
input("回车退出 · UI 进程将关闭...")
