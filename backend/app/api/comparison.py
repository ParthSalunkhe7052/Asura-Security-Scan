"""
Scan Comparison API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from app.core.database import get_db
from app.models.models import Scan, Vulnerability

router = APIRouter(prefix="/api/comparison", tags=["comparison"])


@router.get("/scans/{scan_id_1}/compare/{scan_id_2}")
async def compare_scans(
    scan_id_1: int,
    scan_id_2: int,
    db: Session = Depends(get_db)
):
    """
    Compare two scans and show differences
    
    Returns:
        - Added vulnerabilities (in scan 2 but not in scan 1)
        - Removed vulnerabilities (in scan 1 but not in scan 2)
        - Common vulnerabilities
        - Statistics comparison
    """
    # Get both scans
    scan1 = db.query(Scan).filter(Scan.id == scan_id_1).first()
    scan2 = db.query(Scan).filter(Scan.id == scan_id_2).first()
    
    if not scan1 or not scan2:
        raise HTTPException(status_code=404, detail="One or both scans not found")
    
    # Get vulnerabilities for both scans
    vulns1 = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id_1).all()
    vulns2 = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id_2).all()
    
    # Create vulnerability signatures for comparison
    def get_signature(vuln):
        return f"{vuln.file_path}:{vuln.line_number}:{vuln.vulnerability_type}"
    
    vulns1_dict = {get_signature(v): v for v in vulns1}
    vulns2_dict = {get_signature(v): v for v in vulns2}
    
    # Find differences
    added_sigs = set(vulns2_dict.keys()) - set(vulns1_dict.keys())
    removed_sigs = set(vulns1_dict.keys()) - set(vulns2_dict.keys())
    common_sigs = set(vulns1_dict.keys()) & set(vulns2_dict.keys())
    
    # Build response
    result = {
        "scan1": {
            "id": scan1.id,
            "started_at": scan1.started_at.isoformat() if scan1.started_at else None,
            "total_issues": scan1.total_issues,
            "status": scan1.status.value
        },
        "scan2": {
            "id": scan2.id,
            "started_at": scan2.started_at.isoformat() if scan2.started_at else None,
            "total_issues": scan2.total_issues,
            "status": scan2.status.value
        },
        "comparison": {
            "added_count": len(added_sigs),
            "removed_count": len(removed_sigs),
            "common_count": len(common_sigs),
            "total_change": len(added_sigs) - len(removed_sigs),
            "improvement_percentage": ((len(removed_sigs) - len(added_sigs)) / max(len(vulns1), 1)) * 100
        },
        "added_vulnerabilities": [
            {
                "id": vulns2_dict[sig].id,
                "severity": vulns2_dict[sig].severity.value,
                "vulnerability_type": vulns2_dict[sig].vulnerability_type,
                "file_path": vulns2_dict[sig].file_path,
                "line_number": vulns2_dict[sig].line_number,
                "description": vulns2_dict[sig].description,
                "tool": vulns2_dict[sig].tool
            }
            for sig in added_sigs
        ],
        "removed_vulnerabilities": [
            {
                "id": vulns1_dict[sig].id,
                "severity": vulns1_dict[sig].severity.value,
                "vulnerability_type": vulns1_dict[sig].vulnerability_type,
                "file_path": vulns1_dict[sig].file_path,
                "line_number": vulns1_dict[sig].line_number,
                "description": vulns1_dict[sig].description,
                "tool": vulns1_dict[sig].tool
            }
            for sig in removed_sigs
        ],
        "severity_comparison": {
            "scan1": {
                "critical": len([v for v in vulns1 if v.severity.value == 'CRITICAL']),
                "high": len([v for v in vulns1 if v.severity.value == 'HIGH']),
                "medium": len([v for v in vulns1 if v.severity.value == 'MEDIUM']),
                "low": len([v for v in vulns1 if v.severity.value == 'LOW'])
            },
            "scan2": {
                "critical": len([v for v in vulns2 if v.severity.value == 'CRITICAL']),
                "high": len([v for v in vulns2 if v.severity.value == 'HIGH']),
                "medium": len([v for v in vulns2 if v.severity.value == 'MEDIUM']),
                "low": len([v for v in vulns2 if v.severity.value == 'LOW'])
            }
        }
    }
    
    return result


@router.get("/project/{project_id}/recent-scans")
async def get_recent_scans_for_comparison(
    project_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent scans for a project (for comparison dropdown)
    """
    scans = db.query(Scan).filter(
        Scan.project_id == project_id,
        Scan.status == 'COMPLETED'
    ).order_by(Scan.started_at.desc()).limit(limit).all()
    
    return [
        {
            "id": scan.id,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "total_issues": scan.total_issues,
            "duration_seconds": scan.duration_seconds
        }
        for scan in scans
    ]
