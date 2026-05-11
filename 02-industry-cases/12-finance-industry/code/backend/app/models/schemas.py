"""Pydantic 数据契约 · 金融行业"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    components: dict


# ============ 1. KYC 智能审核 ============
class KYCRequest(BaseModel):
    customer_name:   str
    id_card:         str
    occupation:      str   = ""
    income_yearly:   int   = 0
    source_of_fund:  str   = ""
    purpose:         str   = ""
    pep_self_report: bool  = False   # 政要 / 公职 / 关联人


class KYCFinding(BaseModel):
    category:  Literal["identity", "income", "fund_source", "purpose", "pep", "sanctions"]
    issue:     str
    severity:  Literal["high", "medium", "low"]
    action:    str         # 建议人工动作


class KYCResponse(BaseModel):
    overall_risk:        Literal["high", "medium", "low"]
    findings:            list[KYCFinding]
    suggested_action:    str       # accept / enhanced_dd / reject(建议而已 · 最终人工)
    must_human_review:   bool = True
    pii_summary:         dict
    disclaimer:          str
    ai_drafted:          bool = True


# ============ 2. AML 反洗钱筛查 ============
class AMLTransaction(BaseModel):
    amount_rmb:          int
    count_24h:           int   = 1
    cross_border:        bool  = False
    counterparty_risky:  bool  = False
    night_time:          bool  = False
    cash_intensive:      bool  = False
    new_account_days:    int   = 999
    note:                str   = ""


class AMLRequest(BaseModel):
    transaction: AMLTransaction
    history_note: str = ""


class AMLResponse(BaseModel):
    score:               int                # 0-100
    level:               Literal["high", "medium", "low", "none"]
    rules_hit:           list[str]
    must_report:         bool               # ≥70 强制可疑交易报告
    suggested_action:    str
    disclaimer:          str
    ai_drafted:          bool = True


# ============ 3. 信贷反欺诈 + 评分 ============
class CreditRequest(BaseModel):
    customer_name:   str
    age:             int
    income_monthly:  int
    debt_monthly:    int   = 0
    employment:      str   = ""
    credit_history:  str   = ""
    loan_amount:     int
    loan_purpose:    str
    region:          str   = ""
    # 反欺诈信号(由设备指纹 / 关联图 / 黑名单填入)
    device_risk:     Literal["high", "medium", "low"] = "low"
    blacklist_hit:   bool  = False


class CreditFinding(BaseModel):
    category:    Literal["fraud", "income", "debt", "history", "policy", "discrimination"]
    description: str
    severity:    Literal["high", "medium", "low"]
    advice:      str


class CreditResponse(BaseModel):
    risk_score:           int           # 0-1000(类 FICO)
    risk_band:            Literal["AAA", "AA", "A", "B", "C", "D"]
    findings:             list[CreditFinding]
    suggested_decision:   Literal["approve", "approve_with_conditions", "decline", "manual_review"]
    suggested_limit:      int           # 建议授信额度
    discrimination_check: list[dict]    # 反歧视审计
    must_credit_officer:  bool = True
    pii_summary:          dict
    disclaimer:           str
    ai_drafted:           bool = True


# ============ 4. 投资陪伴(不荐股 · 仅投教)============
class AdvisoryRequest(BaseModel):
    question:        str
    customer_level:  Optional[Literal["C1", "C2", "C3", "C4", "C5"]] = None


class AdvisoryResponse(BaseModel):
    intent:               Literal["投教", "适当性提示", "反诈拦截", "拒答荐股", "复盘解释"]
    answer:               str
    refer_to_advisor:     bool
    disclaimer:           str
    ai_drafted:           bool = True


# ============ 5. 适当性匹配 ============
class SuitabilityRequest(BaseModel):
    customer_level:  Literal["C1", "C2", "C3", "C4", "C5"]
    product_code:    str
    invest_amount:   int = 0
    holding_horizon: str = ""   # 持有周期


class SuitabilityResponse(BaseModel):
    is_suitable:         bool
    reason:              str
    product:             dict
    additional_warnings: list[str]
    must_signed_confirmation: bool = True
    disclaimer:          str
    ai_drafted:          bool = True


# ============ 6. 客户分析 / 流失预警 ============
class CustomerInsightRequest(BaseModel):
    customer_id:           str
    age:                   int
    aum_rmb:               int             # 资产管理规模
    last_active_days:      int             # 上次登录距今
    products_held:         list[str]       # 持有产品代号
    redemption_30d:        int   = 0       # 30 天赎回额
    interaction_count_30d: int   = 0       # 30 天交互次数
    nps_score:             Optional[int] = None


class CustomerInsight(BaseModel):
    persona:               str            # 画像
    churn_risk:            Literal["high", "medium", "low"]
    churn_reasons:         list[str]
    retention_suggestions: list[str]      # 是建议给 RM · 不是营销话术
    must_relationship_manager: bool = True
    pii_summary:           dict
    disclaimer:            str
    ai_drafted:            bool = True


# ============ 7. PII 脱敏 ============
class PIIRedactRequest(BaseModel):
    text: str


class PIIRedactResponse(BaseModel):
    original_length: int
    redacted_text:   str
    pii_summary:     dict
