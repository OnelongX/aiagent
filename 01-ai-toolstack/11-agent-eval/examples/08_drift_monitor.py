"""生产环境 Drift 监控 · 模型自动升级 / 输入分布变化告警

依赖:pip install langfuse
用法:cron · 每天跑一次 / 接进 Grafana
"""
import os
import statistics
from datetime import datetime, timedelta
from langfuse import Langfuse


langfuse = Langfuse(
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
)


DRIFT_TOLERANCE = 0.05    # 跌 5% 告警
HISTORY_DAYS    = 7       # 比过去 7 天平均


def fetch_window_metrics(start: datetime, end: datetime) -> dict:
    """拉某时段的 traces · 算关键指标"""
    traces = langfuse.fetch_traces(
        from_timestamp=start,
        to_timestamp=end,
        limit=10000,
    )

    if not traces.data:
        return {}

    scores = [s.value for t in traces.data for s in (t.scores or [])
              if s.name == "quality"]
    latencies = [t.latency for t in traces.data if t.latency is not None]
    tokens = [t.total_tokens for t in traces.data if t.total_tokens]

    return {
        "trace_count":     len(traces.data),
        "avg_quality":     statistics.mean(scores) if scores else 0,
        "p95_latency":     sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
        "avg_tokens":      statistics.mean(tokens) if tokens else 0,
        "score_count":     len(scores),
    }


def detect_drift():
    today    = datetime.now()
    yesterday = today - timedelta(days=1)
    week_ago  = today - timedelta(days=HISTORY_DAYS + 1)

    today_metrics  = fetch_window_metrics(yesterday, today)
    history_metrics = fetch_window_metrics(week_ago, yesterday)

    if not today_metrics or not history_metrics:
        print("数据不足 · 跳过")
        return []

    alerts = []
    for key in ["avg_quality"]:
        cur = today_metrics[key]
        hist = history_metrics[key]
        if hist > 0 and cur < hist * (1 - DRIFT_TOLERANCE):
            drop_pct = (hist - cur) / hist * 100
            alerts.append(f"[DRIFT] {key}: {cur:.3f} (was {hist:.3f}, drop {drop_pct:.1f}%)")

    # 延迟 / token 反向(变大才是问题)
    for key in ["p95_latency", "avg_tokens"]:
        cur = today_metrics[key]
        hist = history_metrics[key]
        if hist > 0 and cur > hist * (1 + DRIFT_TOLERANCE):
            rise_pct = (cur - hist) / hist * 100
            alerts.append(f"[DRIFT] {key}: {cur:.0f} (was {hist:.0f}, rise {rise_pct:.1f}%)")

    return alerts


def alert_to_slack(messages: list[str]):
    # 替换为你的 webhook
    import urllib.request, json
    webhook = os.getenv("SLACK_WEBHOOK", "")
    if not webhook:
        print("\n".join(messages))
        return
    data = json.dumps({"text": "AI Drift Alert:\n" + "\n".join(messages)}).encode()
    req = urllib.request.Request(webhook, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)


if __name__ == "__main__":
    alerts = detect_drift()
    if alerts:
        print("发现 drift:")
        for a in alerts:
            print(f"  {a}")
        alert_to_slack(alerts)
    else:
        print("[OK] 无 drift")
