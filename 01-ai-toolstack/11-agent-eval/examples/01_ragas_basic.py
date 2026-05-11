"""RAGAS · 4 个核心指标 Hello World

依赖:pip install ragas datasets

预期输出:每个指标 0-1 之间的分数
"""
from ragas import evaluate
from ragas.metrics import (
    faithfulness, answer_relevancy,
    context_precision, context_recall,
)
from datasets import Dataset


# 4 条评测样本 · 真实场景会从 golden_set.json 加载
data = {
    "question": [
        "AI 工具栈 #06 讲的什么?",
        "什么是 Subagent?",
        "Gemini 上下文有多长?",
        "Faithfulness 衡量什么?",
    ],
    "answer": [
        "Claude Agent SDK · Python + TS 双语 · 6 大核心能力",
        "Subagent 是带 LLM 能力的子任务专家 · 有独立 context",
        "Gemini 2.5 Pro 支持 2M token 上下文",
        "Faithfulness 衡量答案是否忠于检索到的 context · 不编",
    ],
    "contexts": [
        ["#06 是 Claude Agent SDK 完整教程,Python + TypeScript 双语,6 大核心能力"],
        ["Subagent 是 Claude SDK 的多 Agent 编排机制,通过 .claude/agents/*.md 定义,独立 context"],
        ["Gemini 2.5 Pro 是当前上下文最长的主流模型,支持 2M token"],
        ["RAGAS 的 Faithfulness 指标衡量答案的事实陈述是否被检索到的 context 支持"],
    ],
    "ground_truth": [
        "Claude Agent SDK 完整教程",
        "Subagent 是有独立 context 的子任务专家",
        "2M token",
        "答案是否忠于 context",
    ],
}

dataset = Dataset.from_dict(data)

result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
print(result)
# {
#   'faithfulness':       0.95,
#   'answer_relevancy':   0.91,
#   'context_precision':  1.00,
#   'context_recall':     1.00,
# }
