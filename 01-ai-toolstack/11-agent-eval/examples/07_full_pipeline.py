"""端到端 Eval 管线 · CI 集成

依赖:pip install ragas datasets
用法:
    python 07_full_pipeline.py
    exit 0 = 通过 · exit 1 = 不通过 → CI 阻断
"""
import sys
import json
import time
from pathlib import Path
from typing import Callable

# 评测维度阈值 · 5 维同时盯
THRESHOLDS = {
    "pass_rate":        0.90,     # golden 集通过率
    "faithfulness":     0.85,     # RAGAS
    "answer_relevancy": 0.85,     # RAGAS
    "p95_latency_ms":   3000,     # 注意:这条反向 · 不能超
    "avg_cost_rmb":     0.05,     # 不能超
}


GOLDEN_PATH = Path(__file__).parent / "golden_set.json"


# =====================================================================
# 1. 替换为你的真实 Agent
# =====================================================================
def your_agent(question: str) -> dict:
    """
    返回 dict:
      - answer: 答案文本
      - contexts: list · RAG 用的 chunk
      - tools_called: list · 调用的工具
      - tokens: int
      - cost_rmb: float
      - latency_ms: int
    """
    # TODO: 替换为你的 Agent 调用
    return {
        "answer":       "mock answer",
        "contexts":     ["mock context"],
        "tools_called": ["get_weather"],
        "tokens":       150,
        "cost_rmb":     0.012,
        "latency_ms":   1200,
    }


# =====================================================================
# 2. 跑评测
# =====================================================================
def run_eval(golden: list, agent: Callable):
    results = []
    print(f"跑 {len(golden)} 条 golden 集...")

    for i, case in enumerate(golden, 1):
        t0 = time.time()
        try:
            out = agent(case["question"])
            elapsed_ms = int((time.time() - t0) * 1000)
            out["latency_ms"] = elapsed_ms

            # 自定义指标:答案是否含期望关键词
            expected = case.get("expected_answer_contains", [])
            passed = all(kw in out["answer"] for kw in expected) if expected else True

            # 工具调用是否符合期望
            if "expected_tools" in case:
                passed = passed and set(case["expected_tools"]).issubset(set(out["tools_called"]))

            results.append({
                "question":  case["question"],
                "answer":    out["answer"],
                "contexts":  out["contexts"],
                "ground_truth": case.get("ground_truth", ""),
                "passed":    passed,
                "tokens":    out["tokens"],
                "cost_rmb":  out["cost_rmb"],
                "latency_ms": out["latency_ms"],
            })
            print(f"  [{i}/{len(golden)}] {'✓' if passed else '✗'} {case['question'][:30]}")

        except Exception as e:
            print(f"  [{i}/{len(golden)}] ✗ ERROR · {e}")
            results.append({"passed": False, "error": str(e)})

    return results


# =====================================================================
# 3. 算指标
# =====================================================================
def compute_metrics(results: list) -> dict:
    valid = [r for r in results if "passed" in r and "error" not in r]
    pass_rate = sum(1 for r in valid if r["passed"]) / len(valid) if valid else 0

    latencies = sorted(r["latency_ms"] for r in valid)
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    avg_cost = sum(r["cost_rmb"] for r in valid) / len(valid) if valid else 0

    # RAGAS 指标(可选 · 较慢)
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy
        from datasets import Dataset

        ragas_ds = Dataset.from_list([
            {"question": r["question"], "answer": r["answer"],
             "contexts": r["contexts"], "ground_truth": r["ground_truth"]}
            for r in valid
        ])
        ragas_result = evaluate(ragas_ds, metrics=[faithfulness, answer_relevancy])
        ragas_scores = {k: float(v) for k, v in ragas_result.items()}
    except ImportError:
        ragas_scores = {}

    return {
        "pass_rate":        round(pass_rate, 3),
        "p95_latency_ms":   p95,
        "avg_cost_rmb":     round(avg_cost, 4),
        **ragas_scores,
    }


# =====================================================================
# 4. 阈值检查
# =====================================================================
def check_thresholds(scores: dict, thresholds: dict) -> list[str]:
    fails = []
    for k, threshold in thresholds.items():
        v = scores.get(k)
        if v is None:
            continue

        # latency 是反向(越小越好)
        if "latency" in k or "cost" in k:
            if v > threshold:
                fails.append(f"  · {k} = {v} > {threshold} (max)")
        else:
            if v < threshold:
                fails.append(f"  · {k} = {v:.3f} < {threshold} (min)")
    return fails


# =====================================================================
# 5. 主入口
# =====================================================================
if __name__ == "__main__":
    golden = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    results = run_eval(golden, your_agent)
    scores = compute_metrics(results)

    print("\n=== 评测结果 ===")
    for k, v in scores.items():
        print(f"  {k}: {v}")

    fails = check_thresholds(scores, THRESHOLDS)
    if fails:
        print("\n[FAIL] 以下指标不达标:")
        print("\n".join(fails))
        sys.exit(1)

    print("\n[PASS] 所有指标达标")
    sys.exit(0)
