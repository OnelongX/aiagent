"""SQLite persistence with multi-library isolation."""

import json
import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "data.db"


def _init_db():
    """Create tables with library isolation."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS libraries (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                color TEXT DEFAULT '#2563EB',
                icon TEXT DEFAULT 'book-open',
                created_at TEXT NOT NULL,
                doc_count INTEGER DEFAULT 0,
                session_count INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                library_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                doc_name TEXT NOT NULL,
                doc_description TEXT DEFAULT '',
                doc_type TEXT DEFAULT '',
                keywords TEXT DEFAULT '[]',
                sections INTEGER DEFAULT 0,
                enhanced INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                library_id TEXT NOT NULL,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL,
                query_count INTEGER DEFAULT 0,
                source_count INTEGER DEFAULT 0,
                FOREIGN KEY (library_id) REFERENCES libraries(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                library_id TEXT,
                event_type TEXT NOT NULL,
                session_id TEXT,
                data TEXT,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_docs_library ON documents(library_id);
            CREATE INDEX IF NOT EXISTS idx_sessions_library ON sessions(library_id);
            CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);
            CREATE INDEX IF NOT EXISTS idx_analytics_library ON analytics(library_id);
        """)

        # Create default library if none exists
        count = conn.execute("SELECT COUNT(*) as c FROM libraries").fetchone()["c"]
        if count == 0:
            now = datetime.now().isoformat()
            conn.execute(
                "INSERT INTO libraries (id, name, description, color, icon, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("default", "默认知识库", "通用知识库，包含所有未分类的文档", "#2563EB", "book-open", now),
            )


@contextmanager
def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# === Library CRUD ===

def create_library(name: str, description: str = "", color: str = "#2563EB", icon: str = "book-open") -> dict:
    lib_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO libraries (id, name, description, color, icon, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (lib_id, name, description, color, icon, now),
        )
    return {"id": lib_id, "name": name, "description": description, "color": color, "icon": icon,
            "created_at": now, "doc_count": 0, "session_count": 0}


def list_libraries() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT l.id, l.name, l.description, l.color, l.icon, l.created_at,
                   (SELECT COUNT(*) FROM documents WHERE library_id = l.id) as doc_count,
                   (SELECT COUNT(*) FROM sessions WHERE library_id = l.id) as session_count
            FROM libraries l ORDER BY l.created_at
        """).fetchall()
        return [dict(r) for r in rows]


def get_library(lib_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM libraries WHERE id = ?", (lib_id,)).fetchone()
        if not row:
            return None
        lib = dict(row)
        lib["doc_count"] = conn.execute("SELECT COUNT(*) as c FROM documents WHERE library_id = ?", (lib_id,)).fetchone()["c"]
        lib["session_count"] = conn.execute("SELECT COUNT(*) as c FROM sessions WHERE library_id = ?", (lib_id,)).fetchone()["c"]
        return lib


def update_library(lib_id: str, data: dict) -> bool:
    allowed = {"name", "description", "color", "icon"}
    fields = {k: v for k, v in data.items() if k in allowed}
    if not fields:
        return False
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with get_conn() as conn:
        result = conn.execute(f"UPDATE libraries SET {set_clause} WHERE id = ?", (*fields.values(), lib_id))
        return result.rowcount > 0


def delete_library(lib_id: str) -> bool:
    if lib_id == "default":
        return False  # Cannot delete default
    with get_conn() as conn:
        result = conn.execute("DELETE FROM libraries WHERE id = ?", (lib_id,))
        return result.rowcount > 0


# === Document Tracking ===

def register_document(library_id: str, filename: str, doc_name: str, doc_description: str = "",
                      doc_type: str = "", keywords: list = None, sections: int = 0, enhanced: bool = False):
    now = datetime.now().isoformat()
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO documents (id, library_id, filename, doc_name, doc_description,
            doc_type, keywords, sections, enhanced, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (filename, library_id, filename, doc_name, doc_description, doc_type,
              json.dumps(keywords or [], ensure_ascii=False), sections, int(enhanced), now))


def list_documents(library_id: str = None) -> list[dict]:
    with get_conn() as conn:
        if library_id:
            rows = conn.execute("SELECT * FROM documents WHERE library_id = ? ORDER BY created_at DESC", (library_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM documents ORDER BY created_at DESC").fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["keywords"] = json.loads(d.get("keywords", "[]"))
            d["enhanced"] = bool(d.get("enhanced", 0))
            result.append(d)
        return result


def delete_document_record(filename: str):
    with get_conn() as conn:
        # Exact match
        result = conn.execute("DELETE FROM documents WHERE id = ?", (filename,))
        if result.rowcount == 0:
            # Fuzzy match
            conn.execute("DELETE FROM documents WHERE id LIKE ? OR filename LIKE ? OR doc_name LIKE ?",
                         (f"%{filename}%", f"%{filename}%", f"%{filename}%"))


# === Session CRUD (scoped to library) ===

def create_session(session_id: str, title: str, library_id: str = "default") -> dict:
    now = datetime.now().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO sessions (id, library_id, title, created_at) VALUES (?, ?, ?, ?)",
            (session_id, library_id, title, now),
        )
    return {"id": session_id, "library_id": library_id, "title": title, "created_at": now,
            "query_count": 0, "source_count": 0, "history": []}


def get_session(session_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if not row:
            return None
        session = dict(row)
        msgs = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
        session["history"] = [{"role": m["role"], "content": m["content"]} for m in msgs]
        return session


def list_sessions(library_id: str = None) -> list[dict]:
    with get_conn() as conn:
        if library_id:
            rows = conn.execute(
                "SELECT id, library_id, title, created_at, query_count FROM sessions WHERE library_id = ? ORDER BY created_at DESC",
                (library_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, library_id, title, created_at, query_count FROM sessions ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def update_session_stats(session_id: str, query_count: int, source_count: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE sessions SET query_count = ?, source_count = ? WHERE id = ?",
            (query_count, source_count, session_id),
        )


def add_message(session_id: str, role: str, content: str):
    now = datetime.now().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, now),
        )


def delete_session(session_id: str) -> bool:
    with get_conn() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        result = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        return result.rowcount > 0


# === Analytics (scoped to library) ===

def log_event(event_type: str, session_id: str = None, data: dict = None, library_id: str = None):
    now = datetime.now().isoformat()
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO analytics (library_id, event_type, session_id, data, created_at) VALUES (?, ?, ?, ?, ?)",
            (library_id, event_type, session_id, json.dumps(data or {}, ensure_ascii=False), now),
        )


def get_analytics_summary(library_id: str = None) -> dict:
    with get_conn() as conn:
        if library_id:
            total = conn.execute("SELECT COUNT(*) as c FROM sessions WHERE library_id = ?", (library_id,)).fetchone()["c"]
            total_queries = conn.execute("SELECT COALESCE(SUM(query_count), 0) as c FROM sessions WHERE library_id = ?", (library_id,)).fetchone()["c"]
            avg_time_row = conn.execute(
                "SELECT AVG(json_extract(data, '$.search_time')) as avg FROM analytics WHERE event_type = 'search' AND library_id = ?",
                (library_id,),
            ).fetchone()
            events = conn.execute(
                "SELECT * FROM analytics WHERE library_id = ? ORDER BY created_at DESC LIMIT 20",
                (library_id,),
            ).fetchall()
        else:
            total = conn.execute("SELECT COUNT(*) as c FROM sessions").fetchone()["c"]
            total_queries = conn.execute("SELECT COALESCE(SUM(query_count), 0) as c FROM sessions").fetchone()["c"]
            avg_time_row = conn.execute(
                "SELECT AVG(json_extract(data, '$.search_time')) as avg FROM analytics WHERE event_type = 'search'"
            ).fetchone()
            events = conn.execute("SELECT * FROM analytics ORDER BY created_at DESC LIMIT 20").fetchall()

        avg_time = round(avg_time_row["avg"], 1) if avg_time_row["avg"] else 0
        return {
            "total_sessions": total,
            "total_queries": total_queries,
            "avg_search_time": avg_time,
            "events": [dict(e) for e in events],
        }


# Initialize on import
_init_db()
