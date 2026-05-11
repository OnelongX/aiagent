"""Settings API — 模型切换 + 日志查询。"""

import time
from collections import deque
from fastapi import APIRouter

from app.config import settings
from app.models.schemas import LogEntry

router = APIRouter(prefix="/api/settings", tags=["settings"])

# 简单内存日志(生产环境换 SQLite/file)
_LOG_BUFFER: deque = deque(maxlen=500)


def log_request(method: str, path: str, status: int, duration_ms: float):
    """关键纪律:字段名 timestamp,不是 time。
    
    旧 bug:前端读 timestamp,后端输出 time → 显示忽显忽空。
    修复:统一 timestamp。
    """
    _LOG_BUFFER.append({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "method": method,
        "path": path,
        "status": status,
        "duration_ms": round(duration_ms, 2),
    })


@router.get("/logs")
async def get_logs(limit: int = 100):
    return {"logs": list(_LOG_BUFFER)[-limit:]}


@router.get("/config")
async def get_config():
    """暴露关键配置(不含 API key)"""
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "llm_api_base": settings.llm_api_base,
        "llm_model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }
