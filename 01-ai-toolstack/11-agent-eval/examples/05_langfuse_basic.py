"""Langfuse · 装饰器一行 trace + Prompt 管理

依赖:pip install langfuse openai

前置:
1. docker run -p 3000:3000 langfuse/langfuse:latest
2. 在 UI 创建 project · 拿 secret_key + public_key
"""
import os
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from openai import OpenAI


langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
)

client = OpenAI()


# === 用法 1:装饰器一行 trace ===
@observe()
def chat_agent(user_input: str) -> str:
    # 装饰器自动捕获:函数名 / 输入 / 输出 / 异常 / 耗时
    resp = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": user_input}],
    )
    return resp.choices[0].message.content


# === 用法 2:嵌套 trace · 看每个子步骤 ===
@observe()
def kb_pipeline(query: str) -> str:
    docs = retrieve(query)
    answer = generate(query, docs)
    return answer


@observe()
def retrieve(query: str) -> list[str]:
    # 假装是向量检索
    return [f"doc related to {query}"]


@observe()
def generate(query: str, docs: list[str]) -> str:
    resp = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": f"基于 {docs} 回答 {query}"}],
    )
    return resp.choices[0].message.content


# === 用法 3:Prompt 管理 ===
def use_managed_prompt(user_q: str) -> str:
    # 从 Langfuse UI 拉取 prompt(版本由 UI 控)
    prompt = langfuse.get_prompt("customer_service_v3")
    compiled = prompt.compile(
        question=user_q,
        company="实战复盘",
    )

    resp = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": compiled}],
    )
    return resp.choices[0].message.content


# === 用法 4:打分(人工 / LLM Judge / 业务事件)===
@observe()
def chat_with_scoring(user_input: str) -> str:
    answer = chat_agent(user_input)

    # 跟当前 trace 打分(后续可以看趋势)
    langfuse_context.score_current_trace(
        name="answer_length",
        value=len(answer),
        comment="字符数",
    )
    return answer


if __name__ == "__main__":
    # 跑几条 · 浏览器 http://localhost:3000 看 traces
    result1 = chat_agent("你好")
    result2 = kb_pipeline("Subagent 是什么")
    result3 = chat_with_scoring("Claude 跟 OpenAI 哪个好")

    # 显式 flush(保证 trace 写入)
    langfuse.flush()
    print("\n打开 http://localhost:3000 看 traces")
