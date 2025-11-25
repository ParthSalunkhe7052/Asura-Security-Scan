import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def setup_module(module):
    # Ensure DB initialized
    from app.core.database import init_db
    init_db()


def test_ai_suggestions_failure_message(monkeypatch):
    from app.main import app
    from app.core.database import SessionLocal
    from app.services.scan_service import ScanService
    from app.models.models import Project, Vulnerability, SeverityEnum

    # Mock LLM to always fail
    import importlib
    llm = importlib.import_module("app.core.llm_adapter")

    def mock_send_with_fallback(prompt, **kwargs):
        return {
            "success": False,
            "response": None,
            "error": "Rate limit exceeded. Please try again later.",
            "model": "meta-llama/llama-3.2-3b-instruct:free",
            "usage": {},
        }

    monkeypatch.setattr(llm, "send_prompt", lambda prompt, **kw: mock_send_with_fallback(prompt, **kw))

    db: Session = SessionLocal()
    try:
        # Check if project exists first to avoid IntegrityError
        project = db.query(Project).filter(Project.name == "X").first()
        if not project:
            project = Project(name="X", path=str(os.getcwd()))
            db.add(project)
            db.commit()
            db.refresh(project)
        scan = ScanService.create_scan(db, project.id, "security")
        vuln = Vulnerability(
            scan_id=scan.id,
            tool="bandit",
            severity=SeverityEnum.CRITICAL,
            file_path="x.py",
            line_number=1,
            vulnerability_type="B101",
            description="desc",
        )
        db.add(vuln)
        db.commit()

        client = TestClient(app)
        resp = client.post(f"/api/scans/{scan.id}/ai-suggestions")
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["model"] is None
        assert "suggestions" in data
        assert "message" in data
        assert "Rate limit" in data["message"]
    finally:
        db.close()