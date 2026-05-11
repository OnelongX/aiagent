"""Pydantic schemas · 字段契约。"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


# === 合同审查 ===
class ContractReviewRequest(BaseModel):
    contract_text: str
    contract_type: Literal["SaaS", "采购", "投资", "劳动", "保密", "代理", "其他"] = "其他"
    jurisdiction: Literal["中国大陆", "香港", "美国", "其他"] = "中国大陆"
    party_role: Literal["甲方", "乙方", "双方"] = "甲方"


class ContractRisk(BaseModel):
    clause: str
    level: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    issue: str
    suggestion: str
    ai_drafted: bool = True


class ContractReviewResponse(BaseModel):
    overall_level: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    risks: list[ContractRisk]
    summary: str
    ai_assist_notice: str = (
        "本审查由 AI 工具辅助完成,具体法律意见以执业律师审核为准。"
    )


# === 类案检索 ===
class CaseSearchRequest(BaseModel):
    case_facts: str = Field(..., description="案件事实描述(已脱敏)")
    claim_type: str = Field(..., description="案由(如:民间借贷 / 劳动争议)")
    jurisdiction: str = "中国大陆"
    top_k: int = 10


class JudicialCase(BaseModel):
    case_number: str   # 案号(必须真实)
    title: str
    court: str          # 审理法院
    court_level: Literal["基层", "中院", "高院", "最高院"]
    judgment_date: str
    claim_type: str
    similarity: float = 0.0
    factual_similarity: float = 0.0
    legal_basis_overlap: float = 0.0
    summary: Optional[str] = None
    url: Optional[str] = None
    source: str = ""   # 裁判文书网 / 北大法宝 / OpenLaw


class CaseSearchResponse(BaseModel):
    cases: list[JudicialCase]
    cross_jurisdiction_warning: bool = False
    notice: str = (
        "类案结果仅供参考。是否援引、如何援引,请由执业律师判断。"
    )


# === 文书起草 ===
class DraftDocumentRequest(BaseModel):
    document_type: Literal[
        "民事起诉状", "答辩状", "代理词", "法律意见书",
        "仲裁申请书", "律师函"
    ]
    case_info: dict   # 灵活字段:当事人 / 案由 / 主要事实 等
    jurisdiction: str = "中国大陆"


class LegalArticle(BaseModel):
    """法条引用 · 必须真实"""
    statute: str             # 法典名
    article_number: str      # 第 X 条
    text: Optional[str] = None
    effective_date: Optional[str] = None
    verified: bool = False   # 必须在真实数据库验真


class DraftDocumentResponse(BaseModel):
    document: str
    placeholders: list[str]  # [作者填入] 占位
    legal_basis: list[LegalArticle]
    lawyer_sign_block: str   # 强制签字栏
    ai_assist_disclaimer: str


# === 法律咨询 ===
class LegalQARequest(BaseModel):
    question: str
    jurisdiction: str = "中国大陆"


class LegalQAResponse(BaseModel):
    intent: Literal["普法", "个案咨询", "应急情况", "刑事相关", "拒答"]
    answer: str
    referenced_laws: list[LegalArticle] = Field(default_factory=list)
    emergency_contacts: list[str] = Field(default_factory=list)
    disclaimer: str = (
        "以上仅为法律知识科普,不构成法律建议。"
        "具体案件请咨询执业律师,以本地法院判决为准。"
    )


# === 法规追踪 ===
class RegulationUpdate(BaseModel):
    title: str
    source: str        # 国家法律法规数据库 / 证监会 / 税务总局 / ...
    publish_date: str
    effective_date: Optional[str] = None
    source_url: str    # 原文链接(强制)
    affected_industries: list[str] = Field(default_factory=list)
    summary: str


class RegulationTrackingResponse(BaseModel):
    updates: list[RegulationUpdate]
    warning: str = (
        "本预警为 AI 初步识别,具体合规改造请咨询执业律师。"
    )


# === PII 脱敏 ===
class PIIRedactRequest(BaseModel):
    text: str


class PIIRedactResponse(BaseModel):
    redacted_text: str
    redacted_entities: list[dict]  # [{"type": "身份证", "original": "...", "placeholder": "[ID_1]"}]


# === Health ===
class HealthResponse(BaseModel):
    status: str
    components: dict[str, str]
