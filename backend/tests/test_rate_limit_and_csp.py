import os
import pytest
from fastapi.testclient import TestClient

def test_rate_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "3")
    monkeypatch.setenv("RATE_LIMIT_WINDOW", "60")
    from app.main import app
    client = TestClient(app)
    # Trigger startup to re-init limiter with env
    with client:
        pass
    statuses = []
    for _ in range(4):
        r = client.get("/health/live")
        statuses.append(r.status_code)
    assert statuses[:3] == [200, 200, 200]
    assert statuses[3] == 429

def test_csp_env_prod(monkeypatch):
    monkeypatch.setenv("ENV", "prod")
    from app.main import app
    client = TestClient(app)
    resp = client.get("/")
    csp = resp.headers.get("Content-Security-Policy", "")
    assert "unsafe-inline" not in csp
    assert "script-src 'self'" in csp