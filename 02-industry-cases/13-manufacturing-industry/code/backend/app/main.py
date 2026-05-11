"""FastAPI 入口 · 制造行业 AI Assistant"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import mes_qa, process, qc, pdm, scheduling, sop_ecn, pii
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
        "制造行业 AI Assistant · 行业落地 #13\n\n"
        "**重要**:本工具是工艺 / QC / 维护团队辅助 · 不替代签字判断。\n"
        "- MES 默认只读 · 写操作必须工艺工程师授权\n"
        "- 工艺参数推荐 · 物理边界硬阻断 · 必须先试跑\n"
        "- 质检 AI 出初判 · QC 工程师终判盖章\n"
        "- PdM 建议 · 维修组按 SOP 执行\n"
        "- 排程辅助 · 计划员审核下发\n"
        "- SOP / ECN 引用必须带版本号 + 生效日期\n"
        "- 安全事故关键词 · 不进 LLM · 直接 EHS"
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

app.include_router(mes_qa.router)
app.include_router(process.router)
app.include_router(qc.router)
app.include_router(pdm.router)
app.include_router(scheduling.router)
app.include_router(sop_ecn.router)
app.include_router(pii.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": [
            "/api/mes/qa",
            "/api/process/recommend",
            "/api/qc/inspect",
            "/api/pdm/check",
            "/api/scheduling/plan",
            "/api/sop/qa",
            "/api/pii/redact",
        ],
        "compliance": {
            "pii_redact":              settings.pii_redact_enabled,
            "process_boundary":        settings.process_boundary_enforced,
            "qc_double_check":         settings.qc_double_check_required,
            "mes_readonly":            settings.mes_readonly_mode,
            "recipe_secret_mask":      settings.recipe_secret_mask,
        },
        "notice": "AI 辅助 · 工艺签字 · QC 终判 · 维修按 SOP · 不替代签字",
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

    components["pii_redact"]        = "enabled" if settings.pii_redact_enabled else "DISABLED (⚠️)"
    components["process_boundary"]  = "enabled" if settings.process_boundary_enforced else "DISABLED (⚠️)"
    components["qc_double_check"]   = "required" if settings.qc_double_check_required else "optional"
    components["mes_readonly"]      = "readonly" if settings.mes_readonly_mode else "WRITE-ENABLED (⚠️)"
    components["recipe_secret"]     = "masked" if settings.recipe_secret_mask else "PLAIN (⚠️)"

    return HealthResponse(status="ok", components=components)
