"""工艺参数推荐 · 物理边界硬阻断 · 必须试跑"""

import logging
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ProcessParamRequest, ProcessParamResponse, ProcessParamSuggestion
)
from app.services.pii_redact_mfg import redact
from app.services.process_guard import (
    check_boundary, mask_recipe_secrets, soften_advice,
    detect_strong_advice, ai_disclaimer,
)
from app.services.llm import chat_json

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/process", tags=["process"])


SYSTEM_PROMPT = """你是制造行业工艺工程师 AI 辅助。

**硬规则**:
1. **不下最终工艺指令** —— 你的输出只是工艺工程师的参考
2. 参数建议必须给 rationale(变更原因)
3. 必须建议**先试跑** · 不能直接批量
4. 不写"必须""一定""肯定包"等绝对化表达
5. 输出严格 JSON · 每个 suggestion 包含 param_key / suggested_value / rationale
6. 工艺机密(配方代号 / 专利号 / 催化剂 / 添加剂)已被脱敏 · 不要追问

输出格式:
{
  "suggestions": [
    {
      "param_key": "sinter_temp_c",
      "suggested_value": 720,
      "rationale": "当前 700°C 良率偏低 · 历史数据 720°C 良率最优 0.985"
    }
  ]
}"""


@router.post("/recommend", response_model=ProcessParamResponse)
async def recommend(req: ProcessParamRequest) -> ProcessParamResponse:
    # 1. PII + 配方机密脱敏
    masked_issue, secret_count = mask_recipe_secrets(req.issue_desc)
    redacted_issue, pii = redact(masked_issue)

    user_prompt = (
        f"产线:{req.line_code}\n工序:{req.process_step}\n"
        f"目标良率:{req.target_yield}\n"
        f"当前参数:{req.current_params}\n"
        f"问题描述:{redacted_issue}\n"
        f"(机密字段已脱敏 {secret_count} 处)"
    )

    try:
        data = chat_json(SYSTEM_PROMPT, user_prompt, max_tokens=2000)
    except Exception as e:
        raise HTTPException(500, f"LLM error: {e}")

    if "_error" in data:
        return ProcessParamResponse(
            line_code=req.line_code,
            suggestions=[],
            boundary_violations=["AI 解析失败 · 请工艺工程师手工评估"],
            disclaimer=ai_disclaimer("LLM 失败"),
            pii_summary=pii,
        )

    suggestions = []
    violations = []
    for s in data.get("suggestions", []):
        param_key = s.get("param_key", "")
        suggested = float(s.get("suggested_value", 0))
        current   = float(req.current_params.get(param_key, 0))
        ok, note  = check_boundary(param_key, suggested)
        rationale = soften_advice(s.get("rationale", ""))
        if detect_strong_advice(rationale):
            rationale = "[已软化绝对化语言] " + rationale

        if not ok:
            violations.append(note)

        suggestions.append(ProcessParamSuggestion(
            param_key=param_key,
            current_value=current,
            suggested_value=suggested,
            boundary_ok=ok,
            boundary_note=note,
            rationale=rationale,
        ))

    return ProcessParamResponse(
        line_code=req.line_code,
        suggestions=suggestions,
        boundary_violations=violations,
        must_process_engineer=True,
        must_pilot_run=True,
        disclaimer=ai_disclaimer(
            "工艺参数变更必须先试跑 · 试跑确认后方可上批量 · "
            "并按 ECN 流程归档"
        ),
        pii_summary=pii,
    )
