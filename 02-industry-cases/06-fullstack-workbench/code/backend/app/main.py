"""FastAPI entrypoint."""

import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import chat, knowledge, settings as settings_api

logger = logging.getLogger(__name__)


async def _warm_embedding():
    """后台预加载 embedding 模型,不阻塞启动。"""
    import asyncio
    loop = asyncio.get_event_loop()
    try:
        from app.services.rag import EmbeddingModel
        logger.info("Loading embedding model in background...")
        await loop.run_in_executor(None, EmbeddingModel.get)
        logger.info("Embedding model loaded.")
    except Exception as e:
        logger.warning(f"Failed to load embedding: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.app_name} starting...")
    import asyncio
    asyncio.create_task(_warm_embedding())
    yield
    logger.info(f"{settings.app_name} shutting down...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="全栈 AI 工作台 · livetoken 案例",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    if request.url.path.startswith("/api"):
        from app.api.settings import log_request
        log_request(request.method, request.url.path, response.status_code, duration_ms)
    return response


app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(settings_api.router)


@app.get("/")
async def root():
    return {"name": settings.app_name, "version": settings.app_version, "status": "running"}


@app.get("/api/health")
async def health():
    """完整健康检查 — 用于 docker healthcheck"""
    components = {}
    try:
        import sqlite3
        from app.services.chat import DB_PATH
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("SELECT 1")
        components["sqlite"] = "ok"
    except Exception as e:
        components["sqlite"] = f"fail: {e}"
    try:
        from app.services.rag import vector_store
        vector_store.client.heartbeat()
        components["chroma"] = "ok"
    except Exception as e:
        components["chroma"] = f"fail: {e}"
    return {"status": "ok", "components": components}
