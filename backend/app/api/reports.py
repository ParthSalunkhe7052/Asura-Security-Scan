from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json

from app.core.database import get_db
from app.models.models import Project, Scan, Vulnerability, CodeMetrics

router = APIRouter(prefix="/api/reports", tags=["reports"])


def generate_json_report(
    project_id: int,
    scan_id: Optional[int],
    db: Session
) -> Dict[str, Any]:
    """Generate comprehensive JSON report"""
    
    # Get project
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    report = {
        "project": {
            "id": project.id,
            "name": project.name,
            "path": project.path,
            "description": project.description
        },
        "generated_at": datetime.utcnow().isoformat(),
        "report_type": "comprehensive"
    }
    
    # Get scan data
    if scan_id:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        scans = [scan] if scan else []
    else:
        scans = db.query(Scan).filter(
            Scan.project_id == project_id
        ).order_by(Scan.started_at.desc()).limit(5).all()
    
    report["scans"] = []
    for scan in scans:
        vulnerabilities = db.query(Vulnerability).filter(
            Vulnerability.scan_id == scan.id
        ).all()
        
        report["scans"].append({
            "id": scan.id,
            "scan_type": scan.scan_type,
            "status": scan.status.value,
            "started_at": scan.started_at.isoformat() if scan.started_at else None,
            "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
            "duration_seconds": scan.duration_seconds,
            "total_issues": scan.total_issues,
            "vulnerabilities": [
                {
                    "tool": v.tool,
                    "severity": v.severity.value,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "vulnerability_type": v.vulnerability_type,
                    "description": v.description,
                    "code_snippet": v.code_snippet,
                    "cwe_id": v.cwe_id,
                    "confidence": v.confidence
                }
                for v in vulnerabilities
            ]
        })
    
    # Get metrics data
    latest_metrics = db.query(CodeMetrics).filter(
        CodeMetrics.project_id == project_id
    ).order_by(CodeMetrics.created_at.desc()).first()
    
    if latest_metrics:
        report["metrics"] = {
            "timestamp": latest_metrics.created_at.isoformat() if latest_metrics.created_at else None,
            "coverage_percent": latest_metrics.coverage_percent,
            "lines_covered": latest_metrics.lines_covered,
            "lines_total": latest_metrics.lines_total,
            "average_complexity": latest_metrics.average_complexity,
            "security_score": latest_metrics.security_score,
            "coverage_score": latest_metrics.coverage_score,
            "code_health_score": latest_metrics.code_health_score
        }
    else:
        report["metrics"] = None
    
    return report


def generate_html_report(report_data: Dict[str, Any]) -> str:
    """Generate HTML report from report data"""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASURA Security Report - {report_data['project']['name']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 8px;
        }}
        h3 {{
            color: #7f8c8d;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .header-info {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .header-info p {{
            margin: 5px 0;
        }}
        .metric-card {{
            display: inline-block;
            width: 23%;
            margin: 1%;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .severity-critical {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .severity-high {{
            color: #e67e22;
            font-weight: bold;
        }}
        .severity-medium {{
            color: #f39c12;
        }}
        .severity-low {{
            color: #3498db;
        }}
        .status-killed {{
            color: #27ae60;
            font-weight: bold;
        }}
        .status-survived {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #7f8c8d;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ ASURA Security & Quality Report</h1>
        
        <div class="header-info">
            <p><strong>Project:</strong> {report_data['project']['name']}</p>
            <p><strong>Path:</strong> {report_data['project']['path']}</p>
            <p><strong>Generated:</strong> {report_data['generated_at']}</p>
        </div>
"""
    
    # Add metrics section if available
    if report_data.get('metrics'):
        metrics = report_data['metrics']
        html += f"""
        <h2>📊 Code Health Metrics</h2>
        <div style="text-align: center;">
            <div class="metric-card">
                <div class="metric-label">Code Health Score</div>
                <div class="metric-value">{metrics.get('code_health_score', 0):.1f}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <div class="metric-label">Security Score</div>
                <div class="metric-value">{metrics.get('security_score', 0):.1f}</div>
            </div>
            <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <div class="metric-label">Coverage</div>
                <div class="metric-value">{metrics.get('coverage_percent', 0):.1f}%</div>
            </div>
        </div>
"""
    
    # Add security scan results
    if report_data.get('scans'):
        html += """
        <h2>🔒 Security Scan Results</h2>
"""
        for scan in report_data['scans']:
            html += f"""
        <h3>Scan #{scan['id']} - {scan['status']} ({scan['total_issues']} issues)</h3>
        <p><em>Started: {scan['started_at']}</em></p>
"""
            if scan.get('vulnerabilities'):
                html += """
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Tool</th>
                    <th>Type</th>
                    <th>File</th>
                    <th>Line</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
"""
                for vuln in scan['vulnerabilities'][:50]:  # Limit to 50
                    severity_class = f"severity-{vuln['severity'].lower()}"
                    html += f"""
                <tr>
                    <td class="{severity_class}">{vuln['severity']}</td>
                    <td>{vuln['tool']}</td>
                    <td>{vuln['vulnerability_type']}</td>
                    <td>{vuln['file_path']}</td>
                    <td>{vuln['line_number'] or '-'}</td>
                    <td>{vuln['description'][:100]}...</td>
                </tr>
"""
                html += """
            </tbody>
        </table>
"""
    
    html += """
        <div class="footer">
            <p>Generated by ASURA - AI SecureLab</p>
            <p>Security Testing Platform</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


@router.get("/export/{project_id}")
async def export_report(
    project_id: int,
    format: str = "json",
    scan_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Export comprehensive report
    
    Args:
        project_id: Project ID
        format: "json" or "html"
        scan_id: Optional specific scan ID
    
    Returns:
        Report in requested format
    """
    # Generate report data
    report_data = generate_json_report(project_id, scan_id, db)
    
    if format == "json":
        return JSONResponse(content=report_data)
    
    elif format == "html":
        html_content = generate_html_report(report_data)
        return HTMLResponse(content=html_content)
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}. Use 'json' or 'html'"
        )


@router.get("/download/{project_id}")
async def download_report(
    project_id: int,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """
    Download report as file
    
    Args:
        project_id: Project ID
        format: "json" or "html"
    
    Returns:
        File download response
    """
    # Generate report
    report_data = generate_json_report(project_id, None, db)
    project_name = report_data['project']['name']
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    if format == "json":
        filename = f"{project_name}_report_{timestamp}.json"
        filepath = reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type="application/json"
        )
    
    elif format == "html":
        filename = f"{project_name}_report_{timestamp}.html"
        filepath = reports_dir / filename
        
        html_content = generate_html_report(report_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return FileResponse(
            path=str(filepath),
            filename=filename,
            media_type="text/html"
        )
    
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {format}"
        )
