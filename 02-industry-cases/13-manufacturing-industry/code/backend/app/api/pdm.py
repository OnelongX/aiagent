"""设备 PdM 预测性维护 · 健康度评分 + 维护建议"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException

from app.models.schemas import PdMRequest, PdMResponse, PdMFinding
from app.services.mes_mock import equipment_health
from app.services.process_guard import (
    soften_advice, ai_disclaimer, is_safety_incident, SAFETY_RESPONSE
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pdm", tags=["pdm"])


SYSTEM_PROMPT = """你是设备 PdM(预测性维护)AI 辅助。

**硬规则**:
1. **不下最终维修指令** —— 维修组按 SOP 执行
2. 风险等级:high / medium / low
3. high → 建议立即上报值班工程师 · 评估停机维护
4. medium → 建议下个班次例行检查
5. low → 计划性维护即可
6. 不写"必须""一定要" · 用"建议"
7. 输出严格 JSON

输出格式:
{
  "findings": [
    {
      "equipment": "L-A1-M01",
      "health_score": 65,
      "risk_level": "medium",
      "suggested_action": "建议下个班次例行检查 · 重点关注主轴振动",
      "suggested_window": "本周内"
    }
  ],
  "next_maintenance": "建议本周内安排预防性维护"
}"""


@router.post("/check", response_model=PdMResponse)
async def check(req: PdMRequest) -> PdMResponse:
    # 1. 安全熔断
    is_safe, hits = is_safety_incident(req.extra_observations)
    if is_safe:
        return PdMResponse(
            line_code=req.line_code,
            findings=[PdMFinding(
                equipment="-",
                health_score=0,
                risk_level="high",
                suggested_action=SAFETY_RESPONSE,
                suggested_window="立即",
            )],
            next_maintenance="安全事故 · 走应急流程",
            disclaimer="安全熔断 · 不经 LLM",
        )

    # 2. 拉真实健康度数据 + LLM 解读
    health = equipment_health(req.line_code)
    user_prompt = (
        f"产线:{req.line_code}\n"
        f"班组长附加观察:{req.extra_observations or '无'}\n"
        f"设备健康度数据:{health['equipments']}"
    )
    try:
        data = chat_json(SYSTEM_PROMPT, user_prompt, max_tokens=2000)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        # fallback · 用阈值规则
        findings = []
        for eq in health["equipments"]:
            score = eq["health_score"]
            if score < 70:
                level, action = "high", "建议立即上报评估"
            elif score < 85:
                level, action = "medium", "下个班次例行检查"
            else:
                level, action = "low", "计划性维护即可"
            findings.append(PdMFinding(
                equipment=eq["name"], health_score=score,
                risk_level=level, suggested_action=action,
                suggested_window="本周内",
            ))
        return PdMResponse(
            line_code=req.line_code, findings=findings,
            next_maintenance="规则 fallback · 请维护组复核",
            disclaimer=ai_disclaimer("LLM 失败 · 规则评分"),
        )

    findings = []
    for f in data.get("findings", []):
        action = soften_advice(f.get("suggested_action", ""))
        findings.append(PdMFinding(
            equipment=f.get("equipment", "-"),
            health_score=int(f.get("health_score", 0)),
            risk_level=f.get("risk_level", "low"),
            suggested_action=action,
            suggested_window=f.get("suggested_window", "本周内"),
        ))

    return PdMResponse(
        line_code=req.line_code,
        findings=findings,
        next_maintenance=soften_advice(data.get("next_maintenance", "")),
        must_maintenance_team=True,
        disclaimer=ai_disclaimer("PdM 建议仅参考 · 维修组按 SOP 执行"),
    )
