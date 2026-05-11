"""OpenAI Agents SDK · 零配置 tracing

依赖:pip install openai-agents
预期:跑完去 https://platform.openai.com/traces 看
"""
import os
from agents import Agent, Runner, function_tool


# 涉密场景必关 · 默认上传 OpenAI 平台
# os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"


@function_tool
def get_weather(city: str) -> str:
    """查询城市天气"""
    return f"{city}: 23°C 晴"


@function_tool
def get_traffic(city: str) -> str:
    """查询交通拥堵情况"""
    return f"{city}: 早高峰拥堵"


agent = Agent(
    name="出行助手",
    instructions="帮用户规划出行 · 必要时查天气和交通",
    tools=[get_weather, get_traffic],
    model="gpt-5",
)


# 跑几个不同复杂度的请求 · 看 trace
queries = [
    "上海今天天气怎么样",
    "我要去北京 · 现在出门方便吗",
    "杭州下午 3 点适合出门吗",
]

for q in queries:
    result = Runner.run_sync(agent, q)
    print(f"Q: {q}")
    print(f"A: {result.final_output}\n")

print("打开 https://platform.openai.com/traces 看 3 条 trace · 含工具调用细节")
