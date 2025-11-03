from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import json

from app.core.database import get_db
from app.models.models import Project, CodeMetrics, Scan, Vulnerability
from app.core.metrics import CodeMetricsAnalyzer

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/{project_id}")
async def get_project_metrics(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive code metrics for a project
    
    Includes:
    - Complexity analysis (from radon)
    - Coverage metrics
    - Security score (from latest scan)
    - Code health score (computed)
    
    Args:
        project_id: Project ID
    
    Returns:
        Comprehensive metrics dictionary
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get or compute metrics
    try:
        analyzer = CodeMetricsAnalyzer(project.path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize analyzer: {str(e)}")
    
    # Analyze complexity (handle failures gracefully)
    try:
        complexity_results = analyzer.analyze_complexity()
    except Exception as e:
        print(f"❌ Complexity analysis failed: {e}")
        complexity_results = {
            "status": "error",
            "files": {},
            "average_complexity": 0.0,
            "error": str(e)
        }
    
    # Analyze coverage (handle failures gracefully)
    try:
        coverage_results = analyzer.analyze_coverage()
    except Exception as e:
        print(f"❌ Coverage analysis failed: {e}")
        coverage_results = {
            "status": "error",
            "coverage_percent": 0.0,
            "lines_covered": 0,
            "lines_total": 0,
            "files": {},
            "error": str(e)
        }
    
    # Get security score from latest scan
    latest_scan = db.query(Scan).filter(
        Scan.project_id == project_id,
        Scan.scan_type == "security"
    ).order_by(Scan.started_at.desc()).first()
    
    security_score = 0.0
    if latest_scan and latest_scan.total_issues is not None:
        # Simple heuristic: 100 - (issues * 2), capped at 0
        security_score = max(0.0, 100.0 - (latest_scan.total_issues * 2))
    
    # Compute health score
    coverage_score = coverage_results.get("coverage_percent", 0.0)
    health = analyzer.compute_code_health_score(
        security_score=security_score,
        coverage_score=coverage_score
    )
    
    # Store metrics in database (only if we have some valid data)
    try:
        code_metrics = CodeMetrics(
            project_id=project_id,
            coverage_percent=coverage_score,
            lines_covered=coverage_results.get("lines_covered", 0),
            lines_total=coverage_results.get("lines_total", 0),
            complexity_data=json.dumps(complexity_results.get("files", {})),
            average_complexity=complexity_results.get("average_complexity", 0.0),
            security_score=security_score,
            coverage_score=coverage_score,
            code_health_score=health["code_health_score"]
        )
        db.add(code_metrics)
        db.commit()
    except Exception as db_err:
        print(f"⚠️  Failed to save metrics to database: {db_err}")
        db.rollback()
        # Continue anyway - return the computed metrics even if DB save fails
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "timestamp": datetime.utcnow().isoformat(),
        "complexity": {
            "status": complexity_results["status"],
            "average_complexity": complexity_results.get("average_complexity", 0.0),
            "files_analyzed": len(complexity_results.get("files", {})),
            "files": complexity_results.get("files", {}),
            "error": complexity_results.get("error") if complexity_results["status"] == "error" else None
        },
        "coverage": {
            "status": coverage_results["status"],
            "coverage_percent": coverage_score,
            "lines_covered": coverage_results.get("lines_covered", 0),
            "lines_total": coverage_results.get("lines_total", 0),
            "error": coverage_results.get("error") if coverage_results["status"] == "error" else None
        },
        "security": {
            "score": security_score,
            "total_issues": latest_scan.total_issues if latest_scan else 0,
            "last_scan": latest_scan.started_at.isoformat() if latest_scan and latest_scan.started_at else None
        },
        "health": health
    }


@router.get("/{project_id}/history")
async def get_metrics_history(
    project_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get historical metrics for a project
    
    Args:
        project_id: Project ID
        limit: Number of records to return
    
    Returns:
        List of historical metrics
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get metrics history
    metrics = db.query(CodeMetrics).filter(
        CodeMetrics.project_id == project_id
    ).order_by(CodeMetrics.created_at.desc()).limit(limit).all()
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "history": [
            {
                "id": m.id,
                "timestamp": m.created_at.isoformat() if m.created_at else None,
                "coverage_percent": m.coverage_percent,
                "average_complexity": m.average_complexity,
                "security_score": m.security_score,
                "coverage_score": m.coverage_score,
                "code_health_score": m.code_health_score
            }
            for m in metrics
        ]
    }


@router.get("/{project_id}/complexity")
async def get_complexity_details(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed complexity analysis for a project
    
    Args:
        project_id: Project ID
    
    Returns:
        Detailed complexity breakdown by file and function
    """
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Run complexity analysis
    try:
        analyzer = CodeMetricsAnalyzer(project.path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize analyzer: {str(e)}")
    
    try:
        complexity_results = analyzer.analyze_complexity()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Complexity analysis failed: {str(e)}"
        )
    
    if complexity_results["status"] == "error":
        # Return error details but don't crash
        return {
            "project_id": project_id,
            "project_name": project.name,
            "status": "error",
            "error": complexity_results.get("error"),
            "average_complexity": 0.0,
            "files": {},
            "summary": {
                "total_files": 0,
                "high_complexity_files": 0
            }
        }
    
    return {
        "project_id": project_id,
        "project_name": project.name,
        "average_complexity": complexity_results.get("average_complexity", 0.0),
        "files": complexity_results.get("files", {}),
        "summary": {
            "total_files": len(complexity_results.get("files", {})),
            "high_complexity_files": len([
                f for f, data in complexity_results.get("files", {}).items()
                if data.get("complexity", 0) > 10
            ])
        }
    }


@router.post("/{project_id}/compute")
async def compute_metrics(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Trigger computation of all metrics for a project
    
    Args:
        project_id: Project ID
    
    Returns:
        Computed metrics
    """
    # Just call the main metrics endpoint which computes and stores
    return await get_project_metrics(project_id, db)
