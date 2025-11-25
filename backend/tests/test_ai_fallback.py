import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal, init_db
from app.services.scan_service import ScanService
from app.models.models import Project, Vulnerability, SeverityEnum

def setup_module(module):
    init_db()

def test_ai_suggestions_fallback(monkeypatch):
    monkeypatch.delenv("OPENROUTER_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    db: Session = SessionLocal()
    try:
        # Check if project exists first to avoid IntegrityError
        project = db.query(Project).filter(Project.name == "TestProj").first()
        if not project:
            project = Project(name="TestProj", path=str(os.getcwd()))
            db.add(project)
            db.commit()
            db.refresh(project)
            
        scan = ScanService.create_scan(db, project.id, "security")
        vuln = Vulnerability(
            scan_id=scan.id,
            tool="bandit",
            severity=SeverityEnum.HIGH,
            file_path="x.py",
            line_number=1,
            vulnerability_type="B101",
            description="test",
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
        assert data["summary"]["total_issues"] >= 1
    finally:
        db.close()