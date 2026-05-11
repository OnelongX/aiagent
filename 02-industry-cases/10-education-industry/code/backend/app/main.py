"""FastAPI 入口 · 教育行业 AI Assistant"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import grade, analytics, communication, recommend, pii
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
        "教育行业 AI Assistant · 行业落地 #10\n\n"
        "**重要**:本工具是教师辅助,不是教师替代。\n"
        "- 未成年人 PII 严格脱敏(GDPR + PIPL)\n"
        "- 主观题 LLM 初评必须教师二审\n"
        "- 家校沟通 5 条红线检测\n"
        "- 焦虑信号监控 → 引导不强化\n"
        "- 双减对齐 · 不推付费课程\n"
        "- 教师签字 · 教师担责"
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

app.include_router(grade.router)
app.include_router(analytics.router)
app.include_router(communication.router)
app.include_router(recommend.router)
app.include_router(pii.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": [
            "/api/grade/objective",
            "/api/grade/essay",
            "/api/analytics/class",
            "/api/communication/weekly-report",
            "/api/communication/parent-qa",
            "/api/recommend",
            "/api/pii/redact",
        ],
        "compliance": {
            "pii_redact": settings.pii_redact_enabled,
            "parent_consent": settings.parent_consent_required,
            "double_reduction": settings.double_reduction_mode,
        },
        "notice": "AI 辅助 · 教师签字 · 教师担责 · 不替代教学评价",
    }


@app.get("/api/health", response_model=HealthResponse)
async def health():
    components = {}

    try:
        from app.services.llm import get_client
        get_client()
        components["llm_client"] = "ok"
        components["llm_endpoint"] = settings.llm_api_base
        components["llm_model"] = settings.llm_model
    except Exception as e:
        components["llm_client"] = f"fail: {e}"

    components["pii_redact"] = "enabled" if settings.pii_redact_enabled else "DISABLED (⚠️)"
    components["double_reduction"] = "enabled" if settings.double_reduction_mode else "DISABLED"
    components["grade_stage"] = settings.grade_stage

    return HealthResponse(status="ok", components=components)
