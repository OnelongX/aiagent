"""FastAPI 入口 · 法律行业 AI Assistant"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import contract, cases, drafting, qa, regulation, pii
from app.models.schemas import HealthResponse

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.app_name} starting...")
    yield
    logger.info(f"{settings.app_name} shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "法律行业 AI Assistant · 行业落地 #9\n\n"
        "**重要**:本工具是律师辅助,不是律师替代。\n"
        "- 法条引用必须真实(接 legal_db 验真)\n"
        "- 文书顶部强制律师签字栏\n"
        "- 应急情况立即拦截(110 / 12348)\n"
        "- PII 双重脱敏(GDPR + PIPL)\n"
        "- 律师签字 · 律师担责"
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


app.include_router(contract.router)
app.include_router(cases.router)
app.include_router(drafting.router)
app.include_router(qa.router)
app.include_router(regulation.router)
app.include_router(pii.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": [
            "/api/contract/review",
            "/api/cases/search",
            "/api/drafting/generate",
            "/api/qa",
            "/api/regulation/track",
            "/api/pii/redact",
        ],
        "notice": (
            "本工具是律师辅助 · 不是律师替代。"
            "执业律师签字 · 律师承担最终责任。"
        ),
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

    try:
        from app.services.legal_db import verify_article
        # ping mock
        test = await verify_article("民法典", "第 675 条")
        components["legal_db"] = "ok (mock)" if test else "fail"
    except Exception as e:
        components["legal_db"] = f"fail: {e}"

    return HealthResponse(status="ok", components=components)
