"""Basic API tests for PageIndex Smart Customer Service."""

import pytest
from fastapi.testclient import TestClient

# Need to set env before importing app
import os
os.environ.setdefault("CHATGPT_API_KEY", "test-key")

from app.main import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "PageIndex AI" in r.text


def test_login():
    r = client.get("/login")
    assert r.status_code == 200


def test_404():
    r = client.get("/nonexistent-page")
    assert r.status_code == 404


def test_list_libraries():
    r = client.get("/api/libraries")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # default library
    assert data[0]["id"] == "default"


def test_create_library():
    r = client.post("/api/libraries", json={"name": "测试库", "description": "测试用"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "测试库"
    assert "id" in data


def test_list_sessions_empty():
    r = client.get("/api/sessions")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_list_documents():
    r = client.get("/api/documents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_settings():
    r = client.get("/api/settings")
    assert r.status_code == 200
    data = r.json()
    assert "profile" in data
    assert "ai" in data
    assert "notifications" in data


def test_update_settings():
    r = client.put("/api/settings/profile", json={"name": "Test User"})
    assert r.status_code == 200
    # Verify
    r2 = client.get("/api/settings")
    assert r2.json()["profile"]["name"] == "Test User"


def test_analytics():
    r = client.get("/api/analytics")
    assert r.status_code == 200
    data = r.json()
    assert "total_sessions" in data
    assert "total_queries" in data


def test_session_not_found():
    r = client.get("/api/session/nonexistent")
    assert r.status_code == 404


def test_delete_default_library_blocked():
    r = client.delete("/api/libraries/default")
    assert r.status_code == 400


def test_upload_non_pdf():
    r = client.post("/api/upload", files={"file": ("test.txt", b"hello", "text/plain")})
    assert r.status_code == 400


def test_upload_accepts_md():
    """Verify markdown file is accepted (may fail indexing without content, but should not 400)."""
    md_content = b"# Test\n\nHello world\n\n## Section 1\n\nContent here."
    r = client.post("/api/upload", files={"file": ("test.md", md_content, "text/markdown")})
    # Should not be 400 (unsupported type) — may be 200 or 500 depending on PageIndex
    assert r.status_code != 400
