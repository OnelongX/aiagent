"""Lightweight async task queue with SQLite backend + background worker thread."""

import json
import uuid
import threading
import traceback
import time as _time
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
import sqlite3

DB_PATH = Path(__file__).parent / "data" / "tasks.db"
DB_PATH.parent.mkdir(exist_ok=True)

_lock = threading.Lock()
_worker_thread = None
_running = True


def _init_db():
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress INTEGER DEFAULT 0,
                message TEXT DEFAULT '',
                input_data TEXT DEFAULT '{}',
                result_data TEXT DEFAULT '{}',
                error TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        """)


@contextmanager
def _get_conn():
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# === Task CRUD ===

def create_task(task_type: str, input_data: dict = None) -> str:
    task_id = str(uuid.uuid4())[:12]
    now = datetime.now().isoformat()
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO tasks (id, type, status, message, input_data, created_at) VALUES (?, ?, 'pending', '排队中...', ?, ?)",
            (task_id, task_type, json.dumps(input_data or {}, ensure_ascii=False), now),
        )
    return task_id


def get_task(task_id: str) -> dict | None:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["input_data"] = json.loads(d.get("input_data", "{}"))
        d["result_data"] = json.loads(d.get("result_data", "{}"))
        return d


def update_task(task_id: str, **kwargs):
    allowed = {"status", "progress", "message", "result_data", "error", "started_at", "completed_at"}
    fields = {k: v for k, v in kwargs.items() if k in allowed}
    if "result_data" in fields and isinstance(fields["result_data"], dict):
        fields["result_data"] = json.dumps(fields["result_data"], ensure_ascii=False)
    if not fields:
        return
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with _get_conn() as conn:
        conn.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", (*fields.values(), task_id))


def list_tasks(limit: int = 20) -> list[dict]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["input_data"] = json.loads(d.get("input_data", "{}"))
            d["result_data"] = json.loads(d.get("result_data", "{}"))
            result.append(d)
        return result


def get_next_pending() -> dict | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE status = 'pending' ORDER BY created_at ASC LIMIT 1"
        ).fetchone()
        if row:
            d = dict(row)
            d["input_data"] = json.loads(d.get("input_data", "{}"))
            return d
        return None


# === Worker ===

_task_handlers = {}


def register_handler(task_type: str, handler):
    """Register a handler function for a task type.
    Handler signature: handler(task_id, input_data, progress_callback)
    progress_callback(progress: int, message: str)
    """
    _task_handlers[task_type] = handler


def _process_task(task: dict):
    task_id = task["id"]
    task_type = task["type"]
    input_data = task["input_data"]

    handler = _task_handlers.get(task_type)
    if not handler:
        update_task(task_id, status="failed", error=f"Unknown task type: {task_type}",
                    completed_at=datetime.now().isoformat())
        return

    def progress_cb(progress: int, message: str = ""):
        update_task(task_id, progress=progress, message=message)

    update_task(task_id, status="running", progress=0, message="开始处理...",
                started_at=datetime.now().isoformat())

    try:
        result = handler(task_id, input_data, progress_cb)
        update_task(task_id, status="completed", progress=100, message="完成",
                    result_data=result or {}, completed_at=datetime.now().isoformat())
    except Exception as e:
        tb = traceback.format_exc()
        print(f"Task {task_id} failed: {e}\n{tb}")
        update_task(task_id, status="failed", error=str(e),
                    message=f"失败: {str(e)[:100]}", completed_at=datetime.now().isoformat())


def _worker_loop():
    global _running
    while _running:
        try:
            task = get_next_pending()
            if task:
                _process_task(task)
            else:
                _time.sleep(1)  # Poll interval
        except Exception as e:
            print(f"Worker error: {e}")
            _time.sleep(2)


def start_worker():
    global _worker_thread, _running
    _running = True
    if _worker_thread is None or not _worker_thread.is_alive():
        _worker_thread = threading.Thread(target=_worker_loop, daemon=True, name="task-worker")
        _worker_thread.start()
        print("Task worker started")


def stop_worker():
    global _running
    _running = False


# Init
_init_db()
