"""FastAPI 入口 · 医疗行业 AI Assistant"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import imaging, triage, medication, discharge, cdss, education, pii
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
        "医疗行业 AI Assistant · 行业落地 #11\n\n"
        "**重要**:本工具是医师辅助 · 不替代医师 · 不构成诊断 / 处方。\n"
        "- 影像 AI:出建议复核 · 100% 医师二审\n"
        "- 分诊 AI:ESI 5 级 · 不替代分诊护士\n"
        "- 用药审查:接药品数据库 · 处方医师签字\n"
        "- 出院小结:AI 起草 · 主治签字担责\n"
        "- CDSS:提示性 · 不下医嘱\n"
        "- 患者科普:不诊断 · 首诊转线下\n"
        "- 急救场景:不进 LLM · 直推 120"
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

app.include_router(imaging.router)
app.include_router(triage.router)
app.include_router(medication.router)
app.include_router(discharge.router)
app.include_router(cdss.router)
app.include_router(education.router)
app.include_router(pii.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": [
            "/api/imaging/review",
            "/api/triage/",
            "/api/medication/check",
            "/api/discharge/summary",
            "/api/cdss/",
            "/api/education/qa",
            "/api/pii/redact",
        ],
        "compliance": {
            "pii_redact":           settings.pii_redact_enabled,
            "emergency_intercept":  settings.emergency_intercept_enabled,
            "doctor_review":        settings.doctor_review_required,
            "drug_db_verify":       settings.drug_db_verify_enabled,
        },
        "notice": "AI 辅助 · 医师签字 · 医师担责 · 不替代医师面诊",
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
    components["emergency_intercept"] = "enabled" if settings.emergency_intercept_enabled else "DISABLED (⚠️)"
    components["doctor_review"]       = "required" if settings.doctor_review_required else "optional"
    components["drug_db_verify"]      = "enabled" if settings.drug_db_verify_enabled else "disabled"

    return HealthResponse(status="ok", components=components)
