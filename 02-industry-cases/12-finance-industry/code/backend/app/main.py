"""FastAPI 入口 · 金融行业 AI Assistant"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import kyc, aml, credit, advisory, suitability, customer, pii
from app.models.schemas import HealthResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.app_name} starting...")
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "金融行业 AI Assistant · 行业落地 #12\n\n"
        "**重要**:本工具是持牌机构辅助 · 不替代合规专员 / 信贷员 / 投顾。\n"
        "- AI 不荐股 · 不预测涨跌 · 不指名具体产品\n"
        "- AI 不授信 · 信贷决定以信贷员 / 风控委员会为准\n"
        "- AI 不替代真人 KYC · 不替代人脸核身\n"
        "- AML 评分仅辅助 · 上报决定以反洗钱专员为准\n"
        "- 适当性匹配硬约束(C1-C5 vs R1-R5)\n"
        "- 反诈关键词命中 → 不进 LLM · 直推反诈"
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kyc.router)
app.include_router(aml.router)
app.include_router(credit.router)
app.include_router(advisory.router)
app.include_router(suitability.router)
app.include_router(customer.router)
app.include_router(pii.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": [
            "/api/kyc/review",
            "/api/aml/screen",
            "/api/credit/score",
            "/api/advisory/qa",
            "/api/suitability/check",
            "/api/customer/insight",
            "/api/pii/redact",
        ],
        "compliance": {
            "pii_redact":          settings.pii_redact_enabled,
            "advisor_block":       settings.advisor_block_enabled,
            "aml_threshold_check": settings.aml_threshold_check,
            "suitability_match":   settings.suitability_match_required,
        },
        "notice": "AI 辅助 · 合规签字 · 持牌机构担责 · 不替代真人尽调 / 信贷 / 投顾",
    }


@app.get("/api/health", response_model=HealthResponse)
async def health():
    components = {}
    try:
        from app.services.llm import get_client
        get_client()
        components["llm_client"]   = "ok"
        components["llm_endpoint"] = settings.llm_api_base
        components["llm_model"]    = settings.llm_model
    except Exception as e:
        components["llm_client"] = f"fail: {e}"

    components["pii_redact"]          = "enabled" if settings.pii_redact_enabled else "DISABLED (⚠️)"
    components["advisor_block"]       = "enabled" if settings.advisor_block_enabled else "DISABLED (⚠️)"
    components["aml_threshold_check"] = "enabled" if settings.aml_threshold_check else "DISABLED"
    components["suitability_match"]   = "required" if settings.suitability_match_required else "optional"

    return HealthResponse(status="ok", components=components)
