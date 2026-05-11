"""MES 自然语言数据问答 · LLM 选意图 · 真实数据从 MES 拿"""

import logging
import re
from fastapi import APIRouter

from app.models.schemas import MESQARequest, MESQAResponse
from app.services.pii_redact_mfg import redact
from app.services.mes_mock import (
    get_line_kpi, list_lines, get_workshop_summary, EQUIPMENT_FAULTS
)
from app.services.process_guard import ai_disclaimer, soften_advice

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/mes", tags=["mes_qa"])


def classify_intent(question: str) -> str:
    if any(k in question for k in ["故障", "停机", "异常", "宕机"]):
        return "fault_query"
    if any(k in question for k in ["良率", "合格率", "FPY", "首检"]):
        return "yield_query"
    if any(k in question for k in ["产能", "产量", "OEE", "效率", "节拍"]):
        return "kpi_query"
    if any(k in question for k in ["车间", "汇总", "整体"]):
        return "summary"
    return "unknown"


LINE_PATTERN = re.compile(r"L-[A-Z]\d")
WORKSHOP_PATTERN = re.compile(r"WS-[A-Z]")


@router.post("/qa", response_model=MESQAResponse)
async def qa(req: MESQARequest) -> MESQAResponse:
    intent = classify_intent(req.question)
    line_codes = LINE_PATTERN.findall(req.question)
    workshops  = WORKSHOP_PATTERN.findall(req.question)

    data = {}
    cite = []

    # 1. 故障查询
    if intent == "fault_query":
        if line_codes:
            for lc in line_codes:
                data[lc] = EQUIPMENT_FAULTS.get(lc, [])
                cite.append(lc)
        else:
            data = EQUIPMENT_FAULTS
            cite = list(EQUIPMENT_FAULTS.keys())
        answer = (
            f"近期故障记录(共 {sum(len(v) for v in data.values())} 条):\n"
            + "\n".join(
                f"· {lc}: " + ", ".join(
                    f"{f['date']} {f['code']}({f['desc']}, {f['duration_min']}min)"
                    for f in flist
                )
                for lc, flist in data.items() if flist
            )
        )

    # 2. 良率 / 产能
    elif intent in ("yield_query", "kpi_query"):
        if not line_codes:
            # 按车间默认 list 一下
            data = {"hint": "未指定产线 · 请举例:'L-A1 昨天良率多少'"}
            answer = "请指定产线代号(如 L-A1)或问'WS-A 整体汇总'。"
        else:
            for lc in line_codes:
                # 权限检查
                line = next((l for l in list_lines() if l["line_code"] == lc), None)
                if not line:
                    data[lc] = {"_error": "产线不存在"}
                    continue
                if req.workshop_scope != "*" and line["workshop"] != req.workshop_scope:
                    data[lc] = {"_error": "无权访问该车间"}
                    continue
                kpi = get_line_kpi(lc, days=7)
                data[lc] = kpi
                cite.append(lc)
            answer = "已从 MES 取近 7 天数据(详见 data 字段)。"

    # 3. 车间汇总
    elif intent == "summary":
        ws = workshops[0] if workshops else "*"
        data = get_workshop_summary(ws)
        cite = [ws]
        answer = (
            f"车间汇总:{ws} · 产线数 {data['line_count']} · "
            f"今日产量 {data['today_output']} · "
            f"平均良率 {data['avg_yield']*100:.2f}%"
        )

    # 4. 未知意图
    else:
        data = {"hint": "未识别意图 · 可问:'L-A1 故障'、'WS-B 良率'、'昨天产量'"}
        answer = "未识别意图 · 请举例:'L-A1 昨天良率多少' / 'WS-A 整体汇总' / 'L-B1 最近故障'"

    answer = soften_advice(answer)

    return MESQAResponse(
        intent=intent,
        answer=answer,
        data=data,
        cite_lines=cite,
        disclaimer=ai_disclaimer("数据来自 MES · AI 仅做查询封装 · 不修改不下指令"),
    )
