"""FastAPI server for PageIndex Smart Customer Service."""

import os
import json
import uuid
import shutil
import asyncio
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from collections import defaultdict
import time as _time

load_dotenv()

from app.indexer import index_pdf, index_file, list_indexes, get_all_structures, KNOWLEDGE_DIR, INDEXES_DIR
from app.retriever import retrieve_context, generate_answer
from app import database as db
from app import task_queue as tq

from contextlib import asynccontextmanager

def _handle_index_task(task_id, input_data, progress_cb):
    """Background handler for document indexing."""
    file_path = input_data.get("file_path", "")
    model = input_data.get("model", "gpt-4o-mini")
    library_id = input_data.get("library_id", "default")
    filename = Path(file_path).stem

    progress_cb(10, "正在解析文档...")

    try:
        result = index_file(file_path, model)
    except Exception as e:
        raise RuntimeError(f"索引失败: {str(e)}")

    progress_cb(80, "正在注册到知识库...")

    db.register_document(
        library_id=library_id,
        filename=filename,
        doc_name=result.get("doc_name", Path(file_path).name),
        doc_description=result.get("doc_description_zh", result.get("doc_description", "")),
        doc_type=result.get("doc_type", ""),
        keywords=result.get("keywords", []),
        sections=len(result.get("structure", [])),
        enhanced=result.get("enhanced", False),
    )

    db.log_event("upload", data={
        "doc_name": Path(file_path).name,
        "sections": len(result.get("structure", [])),
    }, library_id=library_id)

    progress_cb(100, "索引完成")

    return {
        "doc_name": result.get("doc_name", Path(file_path).name),
        "sections": len(result.get("structure", [])),
        "library_id": library_id,
        "doc_type": result.get("doc_type", ""),
    }


tq.register_handler("index_document", _handle_index_task)


@asynccontextmanager
async def lifespan(a):
    _migrate_indexes()
    tq.start_worker()
    yield
    tq.stop_worker()

app = FastAPI(title="PageIndex Smart Customer Service", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple rate limiter middleware
_rate_limits = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 60  # requests per window

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        client_ip = request.client.host
        now = _time.time()
        _rate_limits[client_ip] = [t for t in _rate_limits[client_ip] if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_limits[client_ip]) >= RATE_LIMIT_MAX:
            return JSONResponse(status_code=429, content={"detail": "请求过于频繁，请稍后再试"})
        _rate_limits[client_ip].append(now)
    return await call_next(request)

# Thread pool
_executor = ThreadPoolExecutor(max_workers=2)

# Serve static files
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Settings store (persisted to JSON file)
SETTINGS_FILE = Path(__file__).parent / "settings.json"

def load_settings() -> dict:
    defaults = {
        "profile": {
            "name": "Demo User",
            "email": "demo@example.com",
            "role": "客服专员",
            "timezone": "UTC+8 (Asia/Shanghai)",
            "avatar": "",
        },
        "ai": {
            "model": "gpt-4o-mini",
            "auto_suggest": True,
            "rag_enabled": True,
            "logging_enabled": False,
            "temperature": 0.7,
            "max_tokens": 2048,
        },
        "notifications": {
            "new_conversation": True,
            "resolution": True,
            "escalation": True,
            "weekly_report": False,
            "sound": True,
        },
    }
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE) as f:
                saved = json.load(f)
            for key in defaults:
                if key in saved:
                    defaults[key].update(saved[key])
        except Exception:
            pass
    return defaults

def save_settings(data: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

app_settings = load_settings()


class ChatRequest(BaseModel):
    session_id: str | None = None
    library_id: str = "default"
    message: str
    model: str = "gpt-4o-mini"


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    sources: list[dict]
    search_time: float
    tree_path: list[str]
    reasoning: str


def _migrate_indexes():
    """Migrate existing index files into the database if not already registered."""
    existing = {d["filename"] for d in db.list_documents()}
    for f in INDEXES_DIR.glob("*_structure.json"):
        filename = f.stem.replace("_structure", "")
        if filename not in existing:
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                db.register_document(
                    library_id="default",
                    filename=filename,
                    doc_name=data.get("doc_name", filename),
                    doc_description=data.get("doc_description_zh", data.get("doc_description", "")),
                    doc_type=data.get("doc_type", ""),
                    keywords=data.get("keywords", []),
                    sections=len(data.get("structure", [])),
                    enhanced=data.get("enhanced", False),
                )
                print(f"Migrated index: {filename}")
            except Exception as e:
                print(f"Failed to migrate {filename}: {e}")


@app.get("/")
async def root():
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/login")
async def login_page():
    return FileResponse(str(STATIC_DIR / "login.html"))


@app.get("/api/libraries")
async def list_libraries():
    """List all knowledge libraries."""
    return db.list_libraries()


@app.post("/api/libraries")
async def create_library(data: dict):
    """Create a new knowledge library."""
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(400, "Library name is required")
    return db.create_library(
        name=name,
        description=data.get("description", ""),
        color=data.get("color", "#2563EB"),
        icon=data.get("icon", "book-open"),
    )


@app.get("/api/libraries/{lib_id}")
async def get_library(lib_id: str):
    """Get library details."""
    lib = db.get_library(lib_id)
    if not lib:
        raise HTTPException(404, "Library not found")
    return lib


@app.put("/api/libraries/{lib_id}")
async def update_library(lib_id: str, data: dict):
    """Update library metadata."""
    if not db.update_library(lib_id, data):
        raise HTTPException(404, "Library not found or no changes")
    return {"status": "ok"}


@app.delete("/api/libraries/{lib_id}")
async def delete_library(lib_id: str):
    """Delete a library and all its data."""
    if lib_id == "default":
        raise HTTPException(400, "Cannot delete default library")
    # Delete library's index files
    docs = db.list_documents(lib_id)
    for doc in docs:
        idx_path = INDEXES_DIR / f"{doc['filename']}_structure.json"
        if idx_path.exists():
            idx_path.unlink()
        for pdf in KNOWLEDGE_DIR.glob("*.pdf"):
            if pdf.stem == doc["filename"]:
                pdf.unlink()
                break
    if not db.delete_library(lib_id):
        raise HTTPException(404, "Library not found")
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(req: ChatRequest):
    # Get or create session
    session_id = req.session_id or str(uuid.uuid4())
    session = db.get_session(session_id)
    if not session:
        session = db.create_session(session_id, req.message[:50], req.library_id)

    query_count = session["query_count"] + 1
    history = session.get("history", [])

    # Use model from settings if not explicitly provided
    if req.model == "gpt-4o-mini":
        model_from_settings = app_settings.get("ai", {}).get("model", "gpt-4o-mini")
        req.model = model_from_settings

    loop = asyncio.get_event_loop()

    # Retrieve context scoped to session's library
    lib_id = session.get("library_id", "default")
    lib_docs = db.list_documents(lib_id)
    doc_filenames = [d["filename"] for d in lib_docs] if lib_docs else None
    all_structures = get_all_structures(doc_filenames)

    if all_structures:
        context = await loop.run_in_executor(
            _executor, retrieve_context, req.message, all_structures, req.model
        )
        sources = context.get("sources", [])
        search_time = context.get("search_time", 0)
    else:
        context = {"sources": [], "search_time": 0, "total_docs_searched": 0}
        sources = []
        search_time = 0

    # Generate answer in thread pool (blocking OpenAI call)
    answer = await loop.run_in_executor(
        _executor, generate_answer, req.message, context, history, req.model
    )

    # Persist to database
    db.add_message(session_id, "user", req.message)
    db.add_message(session_id, "assistant", answer)
    source_count = session["source_count"] + len(sources)
    db.update_session_stats(session_id, query_count, source_count)

    # Log analytics event
    db.log_event("search", session_id, {"search_time": search_time, "sources": len(sources)}, lib_id)

    # Build response
    tree_path = sources[0].get("search_path", []) if sources else []
    reasoning = sources[0].get("reasoning", "") if sources else ""

    source_cards = []
    for s in sources:
        source_cards.append({
            "doc_name": s.get("doc_name", "Unknown"),
            "title": s.get("title", "Unknown"),
            "start_page": s.get("start_index", 0),
            "end_page": s.get("end_index", 0),
            "relevance_score": round(s.get("relevance_score", 0) * 100),
            "reason": s.get("reason", ""),
            "search_path": s.get("search_path", []),
        })

    return ChatResponse(
        session_id=session_id,
        reply=answer,
        sources=source_cards,
        search_time=search_time,
        tree_path=tree_path,
        reasoning=reasoning,
    )


SUPPORTED_EXTENSIONS = {".pdf", ".md", ".markdown"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), model: str = "gpt-4o-mini", library_id: str = "default"):
    """Upload file and submit async indexing task. Returns task_id immediately."""
    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件类型。支持：{', '.join(SUPPORTED_EXTENSIONS)}")

    # Save file
    save_path = KNOWLEDGE_DIR / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Use model from settings if default
    if model == "gpt-4o-mini":
        model = app_settings.get("ai", {}).get("model", model)

    # Submit to task queue — returns immediately
    task_id = tq.create_task("index_document", {
        "file_path": str(save_path),
        "file_name": file.filename,
        "model": model,
        "library_id": library_id,
    })

    return {
        "status": "queued",
        "task_id": task_id,
        "file_name": file.filename,
        "message": "文件已上传，正在后台索引...",
    }


# === Task Status API ===

@app.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Poll task status."""
    task = tq.get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@app.get("/api/tasks")
async def list_all_tasks(limit: int = 20):
    """List recent tasks."""
    return tq.list_tasks(limit)


@app.get("/api/documents")
async def get_documents(library_id: str = None):
    """List indexed documents, optionally filtered by library."""
    if library_id:
        return db.list_documents(library_id)
    return list_indexes()


@app.get("/api/sessions")
async def get_sessions(library_id: str = None, page: int = 1, page_size: int = 50):
    """List chat sessions with pagination."""
    sessions = db.list_sessions(library_id)
    total = len(sessions)
    start = (page - 1) * page_size
    return sessions[start:start + page_size]


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get a specific session's history."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    if not db.delete_session(session_id):
        raise HTTPException(404, "Session not found")
    return {"status": "deleted"}


@app.get("/api/analytics")
async def get_analytics(library_id: str = None):
    """Get analytics summary, optionally filtered by library."""
    return db.get_analytics_summary(library_id)


MIME_TYPES = {".pdf": "application/pdf", ".md": "text/markdown", ".markdown": "text/markdown"}

@app.get("/api/documents/{doc_id}/file")
async def get_document_file(doc_id: str):
    """Serve the original document file (PDF or Markdown)."""
    doc_id_lower = doc_id.lower()
    for f in KNOWLEDGE_DIR.iterdir():
        if f.is_file() and (f.stem.lower() == doc_id_lower or doc_id_lower in f.stem.lower() or f.stem.lower() in doc_id_lower):
            mime = MIME_TYPES.get(f.suffix.lower(), "application/octet-stream")
            return FileResponse(
                str(f),
                media_type=mime,
                filename=f.name,
                headers={"Content-Disposition": f"inline; filename=\"{f.name}\""},
            )
    raise HTTPException(404, "文件未找到")


@app.get("/api/documents/{doc_id:path}")
async def get_document_detail(doc_id: str):
    """Get full document detail including all chunks."""
    index_path = _find_index_file(doc_id)
    if not index_path:
        raise HTTPException(404, "Document not found")
    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["id"] = doc_id
    return data


@app.put("/api/documents/{doc_id}")
async def update_document(doc_id: str, data: dict):
    """Update document metadata and/or chunks."""
    index_path = _find_index_file(doc_id)
    if not index_path:
        raise HTTPException(404, "Document not found")
    with open(index_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    # Update allowed fields
    if "doc_description" in data:
        doc["doc_description"] = data["doc_description"]
    if "structure" in data:
        doc["structure"] = data["structure"]

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "doc_id": doc_id}


@app.put("/api/documents/{doc_id}/chunk/{chunk_id}")
async def update_chunk(doc_id: str, chunk_id: str, data: dict):
    """Update a single chunk's title or summary."""
    index_path = _find_index_file(doc_id)
    if not index_path:
        raise HTTPException(404, "Document not found")
    with open(index_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    found = False
    for chunk in doc.get("structure", []):
        if chunk.get("node_id") == chunk_id:
            if "title" in data:
                chunk["title"] = data["title"]
            if "summary" in data:
                chunk["summary"] = data["summary"]
            if "start_index" in data:
                chunk["start_index"] = data["start_index"]
            if "end_index" in data:
                chunk["end_index"] = data["end_index"]
            found = True
            break

    if not found:
        raise HTTPException(404, "Chunk not found")

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "chunk_id": chunk_id}


@app.delete("/api/documents/{doc_id}/chunk/{chunk_id}")
async def delete_chunk(doc_id: str, chunk_id: str):
    """Delete a chunk from a document's index."""
    index_path = _find_index_file(doc_id)
    if not index_path:
        raise HTTPException(404, "Document not found")
    with open(index_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    original_len = len(doc.get("structure", []))
    doc["structure"] = [c for c in doc.get("structure", []) if c.get("node_id") != chunk_id]

    if len(doc["structure"]) == original_len:
        raise HTTPException(404, "Chunk not found")

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "remaining_chunks": len(doc["structure"])}


def _find_index_file(doc_id: str) -> Path | None:
    """Find index file by doc_id with fuzzy matching for special characters."""
    # Exact match first
    exact = INDEXES_DIR / f"{doc_id}_structure.json"
    if exact.exists():
        return exact
    # Fuzzy match — handle encoding differences in filenames
    doc_id_lower = doc_id.lower()
    for f in INDEXES_DIR.glob("*_structure.json"):
        stem = f.stem.replace("_structure", "")
        if stem.lower() == doc_id_lower or doc_id_lower in stem.lower() or stem.lower() in doc_id_lower:
            return f
    return None


@app.delete("/api/documents/{doc_id:path}")
async def delete_document(doc_id: str):
    """Delete a document's index, source file, and database record."""
    deleted_something = False

    # 1. Try delete index file
    index_path = _find_index_file(doc_id)
    doc_name = ""
    filename = doc_id
    if index_path:
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                doc_data = json.load(f)
            doc_name = doc_data.get("doc_name", "")
            filename = index_path.stem.replace("_structure", "")
        except Exception:
            pass
        index_path.unlink()
        deleted_something = True

    # 2. Try delete source file (PDF/MD)
    doc_id_lower = doc_id.lower()
    for src in KNOWLEDGE_DIR.iterdir():
        if src.is_file():
            stem_lower = src.stem.lower()
            name_lower = src.name.lower()
            if (stem_lower == doc_id_lower or doc_id_lower in stem_lower
                    or stem_lower in doc_id_lower or name_lower == doc_name.lower()):
                src.unlink()
                deleted_something = True
                break

    # 3. Always try delete from database (handles case where file is gone but DB record remains)
    db.delete_document_record(filename)
    db.delete_document_record(doc_id)  # Try with original ID too
    deleted_something = True

    if not deleted_something:
        raise HTTPException(404, "Document not found")

    return {"status": "ok", "doc_id": doc_id}


@app.post("/api/documents/{doc_id}/reindex")
async def reindex_document(doc_id: str, model: str = "gpt-4o-mini"):
    """Re-index a document from its PDF."""
    index_path = _find_index_file(doc_id)
    if not index_path:
        raise HTTPException(404, "Document not found")

    with open(index_path, "r", encoding="utf-8") as f:
        doc = json.load(f)
    doc_name = doc.get("doc_name", "")

    # Find PDF
    pdf_path = None
    for pdf in KNOWLEDGE_DIR.glob("*.pdf"):
        if pdf.stem.lower() == doc_id.lower() or doc_name.lower().startswith(pdf.stem.lower()):
            pdf_path = str(pdf)
            break

    if not pdf_path:
        raise HTTPException(404, "PDF file not found for re-indexing")

    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(_executor, index_pdf, pdf_path, model)
        return {
            "status": "ok",
            "sections": len(result.get("structure", [])),
        }
    except Exception as e:
        raise HTTPException(500, f"Re-indexing failed: {str(e)}")


@app.get("/api/settings")
async def get_settings():
    """Get all settings."""
    return app_settings


@app.put("/api/settings/{section}")
async def update_settings(section: str, data: dict):
    """Update a settings section (profile, ai, notifications)."""
    if section not in app_settings:
        raise HTTPException(400, f"Unknown section: {section}")
    app_settings[section].update(data)
    save_settings(app_settings)
    return {"status": "ok", "section": section, "data": app_settings[section]}


@app.post("/api/settings/reset")
async def reset_ai_data():
    """Reset AI training data (clear all indexes)."""
    import shutil as sh
    try:
        for f in INDEXES_DIR.glob("*"):
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                sh.rmtree(f)
        return {"status": "ok", "message": "All indexes cleared"}
    except Exception as e:
        raise HTTPException(500, str(e))


@app.delete("/api/settings/workspace")
async def delete_workspace():
    """Delete workspace — clears database, indexes, and knowledge files."""
    import shutil as sh
    # Clear database
    if db.DB_PATH.exists():
        db.DB_PATH.unlink()
    db._init_db()
    for d in [INDEXES_DIR, KNOWLEDGE_DIR]:
        for f in d.glob("*"):
            if f.is_file():
                f.unlink()
            elif f.is_dir():
                sh.rmtree(f)
    if SETTINGS_FILE.exists():
        SETTINGS_FILE.unlink()
    return {"status": "ok", "message": "Workspace deleted"}


@app.get("/{path:path}")
async def catch_all(path: str):
    """Catch-all route for 404 pages."""
    return FileResponse(str(STATIC_DIR / "404.html"), status_code=404)
