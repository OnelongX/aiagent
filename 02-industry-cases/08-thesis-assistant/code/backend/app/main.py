"""FastAPI 入口 · 学生论文助手"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import outline, section, polish, cite, dedupe, defense
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
        "学生论文助手 API · 行业落地 #8\n\n"
        "**重要**:本工具是 AI 辅助,不是 AI 代笔。\n"
        "- 引用必须 DOI 校验(Crossref 验真)\n"
        "- 章节起草自动标 [AI 辅助]\n"
        "- 降重提示禁止包装抄袭语\n"
        "- 学术诚信责任在作者本人"
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


app.include_router(outline.router)
app.include_router(section.router)
app.include_router(polish.router)
app.include_router(cite.router)
app.include_router(dedupe.router)
app.include_router(defense.router)


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": [
            "/api/outline",
            "/api/section",
            "/api/polish",
            "/api/cite/search",
            "/api/cite/format",
            "/api/dedupe",
            "/api/defense",
        ],
        "notice": (
            "本工具是学术辅助 · 不是代笔。"
            "请按所在学术机构的诚信规范使用。"
        ),
    }


@app.get("/api/health", response_model=HealthResponse)
async def health():
    components = {}

    # LLM 客户端
    try:
        from app.services.llm import get_client
        client = get_client()
        components["llm_client"] = "ok"
        components["llm_endpoint"] = settings.llm_api_base
        components["llm_model"] = settings.llm_model
    except Exception as e:
        components["llm_client"] = f"fail: {e}"

    # 学术 API(快速 ping arxiv)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get("http://export.arxiv.org/api/query?search_query=test&max_results=1")
            components["arxiv"] = "ok" if r.status_code == 200 else f"http_{r.status_code}"
    except Exception as e:
        components["arxiv"] = f"fail: {e}"

    return HealthResponse(status="ok", components=components)
