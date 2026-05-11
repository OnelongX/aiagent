"""RAGAS · CI 集成 · 跌 5% 自动 block

依赖:pip install ragas datasets
用法:python 02_ragas_ci.py · exit code 0 通过 / 1 失败
"""
import sys
import json
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset


# 评测阈值 · CI 阻断红线
THRESHOLDS = {
    "faithfulness":      0.85,
    "answer_relevancy":  0.85,
    "context_precision": 0.80,
    "context_recall":    0.85,
}

# 历史基线(从上次成功的 eval 落盘)
HISTORICAL_BASELINE_FILE = "eval_history.json"
DRIFT_TOLERANCE = 0.05   # 跌 5% block


def load_golden_set(path: str = "golden_set.json"):
    """加载黄金例子"""
    return json.load(open(path))


def run_agent(question: str):
    """跑你的 Agent · 返回 (answer, contexts)"""
    # TODO: 替换为你的真实 Agent 调用
    return ("mock answer", ["mock context"])


def eval_pipeline(golden):
    rows = []
    for case in golden:
        answer, contexts = run_agent(case["question"])
        rows.append({
            "question":     case["question"],
            "answer":       answer,
            "contexts":     contexts,
            "ground_truth": case.get("ground_truth", ""),
        })

    dataset = Dataset.from_list(rows)
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
    )
    return {k: float(v) for k, v in result.items()}


def check_thresholds(scores: dict, thresholds: dict) -> list[str]:
    failed = []
    for k, threshold in thresholds.items():
        if scores.get(k, 0) < threshold:
            failed.append(f"  · {k} = {scores[k]:.3f} < {threshold} (threshold)")
    return failed


def check_drift(scores: dict, baseline_path: str, tolerance: float) -> list[str]:
    import os
    if not os.path.exists(baseline_path):
        return []   # 第一次跑 · 没基线

    baseline = json.load(open(baseline_path))
    drifts = []
    for k, base in baseline.items():
        cur = scores.get(k, 0)
        if cur < base * (1 - tolerance):
            drifts.append(f"  · {k}: {cur:.3f} (was {base:.3f}, drop {(base-cur)/base*100:.1f}%)")
    return drifts


def save_baseline(scores: dict, path: str):
    json.dump(scores, open(path, "w"), indent=2)


if __name__ == "__main__":
    print("=== 跑黄金集评测 ===")
    golden = load_golden_set()
    scores = eval_pipeline(golden)

    print("\n评测结果:")
    for k, v in scores.items():
        print(f"  {k}: {v:.3f}")

    # 检查 1:阈值
    fails = check_thresholds(scores, THRESHOLDS)
    if fails:
        print("\n[FAIL] 指标低于阈值:")
        print("\n".join(fails))
        sys.exit(1)

    # 检查 2:drift
    drifts = check_drift(scores, HISTORICAL_BASELINE_FILE, DRIFT_TOLERANCE)
    if drifts:
        print(f"\n[FAIL] 相比基线下跌超 {DRIFT_TOLERANCE*100:.0f}%:")
        print("\n".join(drifts))
        sys.exit(1)

    # 成功 · 更新基线
    save_baseline(scores, HISTORICAL_BASELINE_FILE)
    print("\n[PASS] 所有指标达标 · 已更新基线")
    sys.exit(0)
