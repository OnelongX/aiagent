"""适当性匹配 · 客户风险等级 vs 产品风险等级"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import SuitabilityRequest, SuitabilityResponse
from app.services.market_db import lookup_product, is_suitable, CUSTOMER_RISK_LEVELS
from app.services.compliance_block import ai_disclaimer

router = APIRouter(prefix="/api/suitability", tags=["suitability"])


@router.post("/check", response_model=SuitabilityResponse)
async def check(req: SuitabilityRequest) -> SuitabilityResponse:
    product = lookup_product(req.product_code)
    if product is None:
        raise HTTPException(404, f"产品代号 {req.product_code} 不存在")

    suitable, reason = is_suitable(req.customer_level, product["risk"])
    warnings = []

    if not suitable:
        warnings.append(
            f"违反适当性匹配:客户 {req.customer_level}({CUSTOMER_RISK_LEVELS[req.customer_level]})"
            f"不可购买 {product['risk']} 级产品({product['name']})"
        )
        warnings.append("如客户坚持购买 · 需签订《风险揭示书》+ 合规专员审批")

    # 大额申购 · 额外双录提示
    if req.invest_amount >= 1_000_000:
        warnings.append("单笔投资 ≥100 万 · 触发双录(录音录像)+ 风险揭示书")

    # 持有周期 vs 产品类型
    if product["risk"] in ("R4", "R5") and req.holding_horizon in ("3个月", "6个月"):
        warnings.append(
            f"{product['name']} 风险等级 {product['risk']} · "
            f"建议持有周期 ≥1 年 · 短期持有可能放大波动损失"
        )

    return SuitabilityResponse(
        is_suitable=suitable,
        reason=reason,
        product=product,
        additional_warnings=warnings,
        must_signed_confirmation=True,
        disclaimer=ai_disclaimer("适当性以纸面 / 双录签字结果为准"),
    )
