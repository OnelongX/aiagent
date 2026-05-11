"""Pydantic 数据契约 · 制造行业"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    components: dict


# ============ 1. MES 数据问答 ============
class MESQARequest(BaseModel):
    question: str = Field(..., description="自然语言提问 · 如 昨天 L-A1 良率多少")
    workshop_scope: str = "*"   # 行级权限 · "*" 或单车间代号


class MESQAResponse(BaseModel):
    intent:        Literal["kpi_query", "yield_query", "fault_query", "summary", "unknown"]
    answer:        str
    data:          dict        # 真实从 MES 拉的数据
    cite_lines:    list[str]   # 引用的产线代号(便于追溯)
    must_engineer_review: bool = True
    disclaimer:    str
    ai_drafted:    bool = True


# ============ 2. 工艺参数推荐 ============
class ProcessParamRequest(BaseModel):
    line_code:       str
    process_step:    Literal["sinter", "coating", "smt_reflow", "injection", "cvd"]
    target_yield:    float = 0.97        # 目标良率
    current_params:  dict                # 当前参数(键值对)
    issue_desc:      str = ""            # 当前的问题描述


class ProcessParamSuggestion(BaseModel):
    param_key:     str
    current_value: float
    suggested_value: float
    boundary_ok:   bool
    boundary_note: str
    rationale:     str


class ProcessParamResponse(BaseModel):
    line_code:       str
    suggestions:     list[ProcessParamSuggestion]
    boundary_violations: list[str]     # 推荐值违反物理边界的项
    must_process_engineer: bool = True
    must_pilot_run:  bool = True       # 必须先试跑 · 不能直接批量
    disclaimer:      str
    pii_summary:     dict
    ai_drafted:      bool = True


# ============ 3. 质检视觉缺陷 ============
class QCInspectionRequest(BaseModel):
    line_code:      str
    product_type:   str
    defect_obs:     str = Field(..., description="操作工 / 视觉系统描述")
    image_caption:  str = ""    # 图片可选描述(本 demo 无 vision · 用文本)


class QCDefectFinding(BaseModel):
    defect_type:    str
    region:         str
    description:    str
    severity:       Literal["high", "medium", "low"]
    suggested_action: Literal["scrap", "rework", "release", "hold_for_qc"]
    confidence:     Literal["低", "中", "高"]


class QCInspectionResponse(BaseModel):
    findings:           list[QCDefectFinding]
    overall_decision:   Literal["release", "rework", "scrap", "hold_for_qc"]
    must_qc_engineer:   bool = True
    cite_sop:           list[str]
    disclaimer:         str
    pii_summary:        dict
    ai_drafted:         bool = True


# ============ 4. 设备 PdM 预测性维护 ============
class PdMRequest(BaseModel):
    line_code: str
    extra_observations: str = ""     # 班组长附加观察


class PdMFinding(BaseModel):
    equipment:        str
    health_score:     int
    risk_level:       Literal["high", "medium", "low"]
    suggested_action: str
    suggested_window: str     # 建议维护时间窗


class PdMResponse(BaseModel):
    line_code:           str
    findings:            list[PdMFinding]
    next_maintenance:    str
    must_maintenance_team: bool = True
    disclaimer:          str
    ai_drafted:          bool = True


# ============ 5. 排程辅助 ============
class SchedulingOrder(BaseModel):
    order_id:       str
    customer:       str = ""
    product:        str
    qty:            int
    due_date:       str
    priority:       Literal["urgent", "high", "normal", "low"] = "normal"


class SchedulingRequest(BaseModel):
    orders:           list[SchedulingOrder]
    available_lines:  list[str]
    horizon_days:     int = 7


class SchedulingPlan(BaseModel):
    line_code:  str
    order_id:   str
    start_date: str
    end_date:   str
    qty_assigned: int
    note:       str


class SchedulingResponse(BaseModel):
    plans:               list[SchedulingPlan]
    unscheduled:         list[str]      # 排不下的订单
    bottleneck_notes:    list[str]
    must_planner_review: bool = True
    disclaimer:          str
    ai_drafted:          bool = True


# ============ 6. SOP / ECN 知识 ============
class SOPRequest(BaseModel):
    question: str
    line_code: Optional[str] = None


class SOPResponse(BaseModel):
    intent:      Literal["sop_query", "ecn_query", "general"]
    answer:      str
    cite_docs:   list[dict]      # SOP / ECN 引用 · 必须有版本号 + 日期
    must_engineer_review: bool = True
    disclaimer:  str
    ai_drafted:  bool = True


# ============ 7. PII / 商业秘密脱敏 ============
class PIIRedactRequest(BaseModel):
    text: str


class PIIRedactResponse(BaseModel):
    original_length: int
    redacted_text:   str
    pii_summary:     dict
