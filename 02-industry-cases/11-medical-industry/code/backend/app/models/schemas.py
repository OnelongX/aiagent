"""Pydantic 数据契约 · 医疗行业"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


# ============ 通用 ============
class HealthResponse(BaseModel):
    status: str
    components: dict


# ============ 1. 影像辅助 ============
class ImagingReviewRequest(BaseModel):
    modality:         Literal["CT", "MRI", "X-ray", "US", "DR", "其他"] = "CT"
    body_part:        str = Field(..., description="检查部位 · 如 胸部 / 头颅")
    clinical_history: str = Field("", description="病史 / 主诉")
    findings_text:    str = Field(..., description="放射科医师初读所见 / 自动描述")


class ImagingFinding(BaseModel):
    region:           str
    description:      str
    suggested_review: str       # AI 给"建议复核"语言 · 不下诊断
    confidence:       Literal["低", "中", "高"]
    references:       list[str] = []


class ImagingReviewResponse(BaseModel):
    modality:           str
    body_part:          str
    suggested_reviews:  list[ImagingFinding]
    must_human_review:  bool = True   # 影像 AI 100% 二审
    disclaimer:         str
    pii_summary:        dict
    ai_drafted:         bool = True


# ============ 2. 智能分诊(ESI 5 级)============
class TriageRequest(BaseModel):
    age:              int
    sex:              Literal["male", "female", "other"]
    chief_complaint:  str        = Field(..., description="主诉")
    vital_signs:      Optional[dict] = None   # 血压 / 心率 / 体温 / SpO2
    duration:         str        = ""         # 持续时间
    history:          str        = ""


class TriageResponse(BaseModel):
    esi_level:           Literal[1, 2, 3, 4, 5]
    level_name:          str       # 红色 / 橙色 / 黄色 / 绿色 / 蓝色
    is_emergency:        bool
    emergency_action:    str = ""  # 急救场景的应急指令
    suggested_department: str
    suggested_workup:    list[str]
    red_flags:           list[str] # 危险信号
    pii_summary:         dict
    disclaimer:          str
    ai_drafted:          bool = True


# ============ 3. 用药审查 ============
class MedicationCheckRequest(BaseModel):
    drugs:                list[str] = Field(..., description="通用名列表")
    patient_age:          int       = 40
    patient_weight_kg:    float     = 70.0
    pregnancy:            bool      = False
    lactation:            bool      = False
    renal_function:       Literal["normal", "mild", "moderate", "severe"] = "normal"
    hepatic_function:     Literal["normal", "mild", "moderate", "severe"] = "normal"
    allergies:            list[str] = []


class DrugIssue(BaseModel):
    type:        Literal["interaction", "contraindication", "dose", "population", "commercial_name"]
    severity:    Literal["high", "moderate", "low"]
    drugs:       list[str]
    description: str
    advice:      str


class MedicationCheckResponse(BaseModel):
    drugs_resolved:    list[dict]  # 每个药的基础属性
    interactions:      list[dict]
    issues:            list[DrugIssue]
    overall_severity:  Literal["high", "moderate", "low", "none"]
    must_pharmacist_review: bool = True
    disclaimer:        str
    ai_drafted:        bool = True


# ============ 4. 出院小结 / 病程摘要 ============
class DischargeSummaryRequest(BaseModel):
    admission_date:   str
    discharge_date:   str
    chief_complaint:  str
    admission_dx:     str
    discharge_dx:     str
    course:           str             # 住院过程
    medications:      list[str]       # 出院带药通用名
    follow_up:        str = ""


class DischargeSummaryResponse(BaseModel):
    summary:        str
    drafted_at:     str
    doctor_block:   str       # 强制签字栏
    disclaimer:     str
    pii_summary:    dict
    ai_drafted:     bool = True


# ============ 5. 临床决策支持 CDSS ============
class CDSSRequest(BaseModel):
    age:               int
    sex:               Literal["male", "female", "other"]
    chief_complaint:   str
    history:           str = ""
    labs:              Optional[dict] = None
    current_dx:        str = ""


class CDSSSuggestion(BaseModel):
    category:    Literal["diagnostic_workup", "differential", "red_flag", "guideline"]
    suggestion:  str
    rationale:   str
    references:  list[str] = []


class CDSSResponse(BaseModel):
    suggestions:      list[CDSSSuggestion]
    not_a_diagnosis:  bool = True
    must_doctor_decide: bool = True
    disclaimer:       str
    pii_summary:      dict
    ai_drafted:       bool = True


# ============ 6. 患者科普 + 复诊咨询 ============
class PatientQARequest(BaseModel):
    question:    str
    patient_age: int = 30
    is_followup: bool = False    # 是否复诊


class PatientQAResponse(BaseModel):
    intent:               Literal["科普", "复诊咨询", "首诊倾向", "急救", "心理危机"]
    answer:               str
    refer_to_clinic:      bool      # 是否建议线下面诊
    emergency_contacts:   list[dict] = []
    disclaimer:           str
    ai_drafted:           bool = True


# ============ 7. PII 脱敏(独立工具)============
class PIIRedactRequest(BaseModel):
    text: str


class PIIRedactResponse(BaseModel):
    original_length: int
    redacted_text:   str
    pii_summary:     dict
