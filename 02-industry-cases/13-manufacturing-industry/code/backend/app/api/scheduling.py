"""排程辅助 · 订单 × 产线 × 截止日 · AI 提建议 · 计划员决定"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    SchedulingRequest, SchedulingResponse, SchedulingPlan, SchedulingOrder
)
from app.services.process_guard import soften_advice, ai_disclaimer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])


PRIORITY_RANK = {"urgent": 0, "high": 1, "normal": 2, "low": 3}


@router.post("/plan", response_model=SchedulingResponse)
async def plan(req: SchedulingRequest) -> SchedulingResponse:
    """规则版排程 · 简单贪心
    实际生产请接 APS(Advanced Planning & Scheduling)系统
    或 OR-Tools / Gurobi · 本 demo 演示思路
    """
    if not req.orders:
        return SchedulingResponse(
            plans=[], unscheduled=[],
            bottleneck_notes=["无订单"],
            disclaimer=ai_disclaimer("空输入"),
        )
    if not req.available_lines:
        raise HTTPException(400, "available_lines 不能为空")

    # 1. 排序:优先级 + 截止日
    orders_sorted = sorted(
        req.orders,
        key=lambda o: (PRIORITY_RANK[o.priority], o.due_date),
    )

    # 2. 假设每条产线产能均匀 · 简单贪心
    today = datetime(2026, 5, 11)
    line_calendar: dict[str, datetime] = {l: today for l in req.available_lines}
    plans: list[SchedulingPlan] = []
    unscheduled: list[str] = []
    bottlenecks: list[str] = []

    for order in orders_sorted:
        # 选当前最空闲的产线
        best_line = min(line_calendar.items(), key=lambda kv: kv[1])
        line_code, line_start = best_line

        # 假设 1500 件/天的处理速度(均值)
        duration_days = max(1, order.qty // 1500)
        end_date = line_start + timedelta(days=duration_days)

        # 检查截止日
        try:
            due = datetime.fromisoformat(order.due_date)
        except ValueError:
            due = today + timedelta(days=14)

        if end_date > due:
            note = (
                f"订单 {order.order_id}(优先级 {order.priority})· "
                f"预计完工 {end_date.date()} 晚于截止 {due.date()} · "
                f"建议 1) 升级优先级 2) 增加产线 3) 与客户协商延期"
            )
            bottlenecks.append(note)
            unscheduled.append(order.order_id)
            continue

        plans.append(SchedulingPlan(
            line_code=line_code,
            order_id=order.order_id,
            start_date=line_start.date().isoformat(),
            end_date=end_date.date().isoformat(),
            qty_assigned=order.qty,
            note=f"贪心分配 · 截止日 {order.due_date}",
        ))
        line_calendar[line_code] = end_date

    # 软化语言
    bottlenecks = [soften_advice(b) for b in bottlenecks]

    return SchedulingResponse(
        plans=plans,
        unscheduled=unscheduled,
        bottleneck_notes=bottlenecks,
        must_planner_review=True,
        disclaimer=ai_disclaimer(
            "排程建议仅参考 · 实际下发 MES 工单以计划员确认为准 · "
            "本 demo 为简化贪心 · 生产环境对接 APS / OR-Tools"
        ),
    )
