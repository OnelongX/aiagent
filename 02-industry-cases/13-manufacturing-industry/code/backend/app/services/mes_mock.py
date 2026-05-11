"""MES 数据 mock · 自然语言问答的底层

生产环境替换为:
- 真 MES 系统(SAP MES / 西门子 Opcenter / 鼎捷 / 用友 / 光因)
- 历史数据库(InfluxDB / TimescaleDB)
- PLM / BOM 接口
- SCADA / DCS 数据网关

本 mock 含 4 个车间 · 8 条产线 · 2 周历史数据 · 直接 docker 跑通。
"""

from datetime import datetime, timedelta
import random

# 4 个车间 · 8 条产线(2 个车间各 2 条 + 2 个车间各 2 条)
WORKSHOPS = {
    "WS-A": "前段车间 · 涂层 / 烧结",
    "WS-B": "中段车间 · 组装 / SMT",
    "WS-C": "测试车间 · 老化 / 终测",
    "WS-D": "包装车间 · 包装 / 出货",
}

LINES = {
    "L-A1": {"workshop": "WS-A", "type": "涂层", "designed_speed": 2000},
    "L-A2": {"workshop": "WS-A", "type": "烧结", "designed_speed": 800},
    "L-B1": {"workshop": "WS-B", "type": "SMT",  "designed_speed": 3000},
    "L-B2": {"workshop": "WS-B", "type": "组装", "designed_speed": 1500},
    "L-C1": {"workshop": "WS-C", "type": "老化", "designed_speed": 600},
    "L-C2": {"workshop": "WS-C", "type": "终测", "designed_speed": 1200},
    "L-D1": {"workshop": "WS-D", "type": "包装", "designed_speed": 4000},
    "L-D2": {"workshop": "WS-D", "type": "出货", "designed_speed": 5000},
}

# 设备故障代码 mock
EQUIPMENT_FAULTS = {
    "L-A1": [{"date": "2026-05-09", "code": "E102", "desc": "涂头压力波动", "duration_min": 23}],
    "L-A2": [{"date": "2026-05-08", "code": "E301", "desc": "炉温区温度梯度异常", "duration_min": 47}],
    "L-B1": [{"date": "2026-05-10", "code": "E205", "desc": "贴片机吸嘴磨损", "duration_min": 12}],
}


def _seeded_random(line_code: str, day_offset: int) -> random.Random:
    return random.Random(hash((line_code, day_offset)) & 0xFFFFFFFF)


def get_line_kpi(line_code: str, days: int = 7) -> dict:
    """生成 KPI mock 数据(确定性 · seed 固定)"""
    line = LINES.get(line_code)
    if line is None:
        return {"_error": f"line {line_code} not found"}

    today = datetime(2026, 5, 11)
    daily = []
    for d in range(days):
        date = today - timedelta(days=d)
        rng = _seeded_random(line_code, d)
        actual = int(line["designed_speed"] * 24 * rng.uniform(0.65, 0.92))
        # 良率 92-99%(seed 固定)
        yield_pct = round(rng.uniform(0.92, 0.99), 4)
        scrap = int(actual * (1 - yield_pct))
        daily.append({
            "date":            date.strftime("%Y-%m-%d"),
            "output":          actual,
            "yield":           yield_pct,
            "scrap":           scrap,
            "oee":             round(rng.uniform(0.70, 0.90), 3),
            "downtime_min":    int(rng.uniform(0, 120)),
            "first_pass_yield": round(yield_pct - rng.uniform(0, 0.03), 4),
        })

    return {
        "line_code":   line_code,
        "type":        line["type"],
        "workshop":    line["workshop"],
        "designed_speed_per_h": line["designed_speed"],
        "daily":       list(reversed(daily)),
    }


def list_lines(workshop: str = "*") -> list[dict]:
    rows = []
    for code, info in LINES.items():
        if workshop == "*" or info["workshop"] == workshop:
            rows.append({"line_code": code, **info, "workshop_name": WORKSHOPS[info["workshop"]]})
    return rows


def get_workshop_summary(workshop: str = "*") -> dict:
    """车间汇总"""
    lines = list_lines(workshop)
    total_output = 0
    yield_sum, yield_count = 0.0, 0
    for line in lines:
        kpi = get_line_kpi(line["line_code"], days=1)
        if "_error" in kpi:
            continue
        for d in kpi["daily"]:
            total_output += d["output"]
            yield_sum   += d["yield"]
            yield_count += 1
    avg_yield = round(yield_sum / yield_count, 4) if yield_count else 0
    return {
        "workshop":        workshop,
        "line_count":      len(lines),
        "today_output":    total_output,
        "avg_yield":       avg_yield,
    }


# ============ 设备 PdM mock · 健康度评分 ============
def equipment_health(line_code: str) -> dict:
    """返回该产线主要设备的健康度评分(0-100 · 越高越健康)"""
    rng = _seeded_random(line_code, 0)
    return {
        "line_code": line_code,
        "equipments": [
            {"name": f"{line_code}-M01", "type": "主机", "health_score": int(rng.uniform(60, 95)),
             "vibration_rms": round(rng.uniform(0.5, 4.5), 2),
             "temperature_c": round(rng.uniform(45, 85), 1),
             "current_a":     round(rng.uniform(8, 22), 1),
             "last_maintain": "2026-04-15"},
            {"name": f"{line_code}-M02", "type": "辅机", "health_score": int(rng.uniform(70, 95)),
             "vibration_rms": round(rng.uniform(0.3, 3.0), 2),
             "temperature_c": round(rng.uniform(35, 65), 1),
             "current_a":     round(rng.uniform(4, 12), 1),
             "last_maintain": "2026-04-20"},
        ],
    }


# ============ SOP / ECN 知识库 mock ============
SOP_DOCS = {
    "SOP-CT-001": {
        "title":   "涂层产线开机标准作业",
        "version": "v3.2",
        "effective_date": "2026-03-01",
        "scope":   "L-A1 涂层产线",
        "summary": "开机前确认温度 / 压力联锁 · 启动按 6 步顺序",
    },
    "SOP-SM-014": {
        "title":   "SMT 回流焊温区设定",
        "version": "v2.1",
        "effective_date": "2026-02-15",
        "scope":   "L-B1 SMT 产线",
        "summary": "无铅工艺 · 峰值 245±5℃ · TAL 60±15s",
    },
    "ECN-2026-038": {
        "title":   "客户 X 料号 PN-A0815 喷涂厚度变更",
        "version": "ECN v1.0",
        "effective_date": "2026-05-15",
        "scope":   "L-A1 · 客户 X 全部 PN-A0815 批次",
        "summary": "喷涂厚度 12μm → 15μm · 老批次走完为止 · 新工单生效",
        "impact":  [
            "在制品(WIP):允许走完原工艺",
            "已交付:无召回需求",
            "QC:首件须重新 PPAP 提交",
            "BOM:维持不变",
        ],
    },
}


def search_sop(query: str) -> list[dict]:
    """简单关键词检索"""
    results = []
    for doc_id, doc in SOP_DOCS.items():
        if query in doc["title"] or query in doc["summary"] or query in doc.get("scope", ""):
            results.append({"doc_id": doc_id, **doc})
    return results


def get_ecn(ecn_id: str) -> dict | None:
    return SOP_DOCS.get(ecn_id)
