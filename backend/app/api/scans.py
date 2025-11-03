from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.scan import ScanCreate, ScanResponse, ScanDetailResponse, VulnerabilityResponse
from app.services.scan_service import ScanService
from app.core.llm_adapter import send_prompt
from typing import List, Dict, Any

router = APIRouter(prefix="/api/scans", tags=["scans"])

@router.post("/", response_model=ScanResponse, status_code=201)
async def create_scan(
    scan: ScanCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and start a new security scan"""
    try:
        # Create scan record
        db_scan = ScanService.create_scan(db, scan.project_id, scan.scan_type)
        scan_id = db_scan.id
        
        # Run scan in background if it's a security scan
        # NOTE: Don't pass the db session - it will create its own fresh sessions
        if scan.scan_type == "security":
            from app.core.database import SessionLocal
            # Create a dummy session just to pass the interface, but close it immediately
            dummy_db = SessionLocal()
            background_tasks.add_task(ScanService.run_security_scan, dummy_db, scan_id)
        
        return db_scan
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    """Get scan details with vulnerabilities"""
    scan = ScanService.get_scan_with_vulnerabilities(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan

@router.get("/project/{project_id}", response_model=List[ScanResponse])
async def get_project_scans(
    project_id: int, 
    skip: int = 0, 
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all scans for a specific project"""
    return ScanService.get_project_scans(db, project_id, skip, limit)

@router.post("/{scan_id}/run", response_model=ScanResponse)
async def run_scan(
    scan_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Manually trigger a scan execution"""
    scan = ScanService.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    if scan.scan_type == "security":
        # Create a fresh session for background task (don't reuse request session)
        from app.core.database import SessionLocal
        dummy_db = SessionLocal()
        background_tasks.add_task(ScanService.run_security_scan, dummy_db, scan_id)
    else:
        raise HTTPException(status_code=400, detail="Mutation testing not yet implemented")
    
    return scan

@router.get("/{scan_id}/vulnerabilities", response_model=List[VulnerabilityResponse])
async def get_scan_vulnerabilities(
    scan_id: int,
    db: Session = Depends(get_db)
):
    """Get all vulnerabilities for a specific scan"""
    from app.models.models import Vulnerability
    
    # Check if scan exists
    scan = ScanService.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Get vulnerabilities for this scan
    vulnerabilities = db.query(Vulnerability).filter(
        Vulnerability.scan_id == scan_id
    ).all()
    
    return vulnerabilities


@router.post("/{scan_id}/ai-suggestions")
async def get_ai_suggestions(
    scan_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get AI-powered suggestions for fixing vulnerabilities found in the scan.
    Uses LLM to analyze vulnerabilities and provide actionable recommendations.
    """
    from app.models.models import Vulnerability, Project
    
    try:
        # Get scan with project info
        scan = ScanService.get_scan(db, scan_id)
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Check if AI suggestions already exist (cached)
        if scan.ai_suggestions:
            print(f"📋 Returning cached AI suggestions for scan #{scan_id}")
            return {
                "success": True,
                "suggestions": scan.ai_suggestions,
                "model": scan.ai_model,
                "summary": {
                    "total_issues": scan.total_issues or 0,
                    "critical": len([v for v in scan.vulnerabilities if v.severity.value == "CRITICAL"]),
                    "high": len([v for v in scan.vulnerabilities if v.severity.value == "HIGH"]),
                    "medium": len([v for v in scan.vulnerabilities if v.severity.value == "MEDIUM"]),
                    "low": len([v for v in scan.vulnerabilities if v.severity.value == "LOW"])
                },
                "cached": True,
                "generated_at": scan.ai_generated_at.isoformat() if scan.ai_generated_at else None
            }
        
        # Get project info for new analysis
        project = db.query(Project).filter(Project.id == scan.project_id).first()
        project_name = project.name if project else f"Project #{scan.project_id}"
        
        # Get all vulnerabilities for this scan
        vulnerabilities = db.query(Vulnerability).filter(
            Vulnerability.scan_id == scan_id
        ).all()
        
        if not vulnerabilities:
            return {
                "success": True,
                "suggestions": "No vulnerabilities found! Your code is secure. 🎉",
                "model": None,
                "summary": {
                    "total_issues": 0,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0
                }
            }
        
        # Group vulnerabilities by severity
        severity_counts = {
            "CRITICAL": len([v for v in vulnerabilities if v.severity == "CRITICAL"]),
            "HIGH": len([v for v in vulnerabilities if v.severity == "HIGH"]),
            "MEDIUM": len([v for v in vulnerabilities if v.severity == "MEDIUM"]),
            "LOW": len([v for v in vulnerabilities if v.severity == "LOW"])
        }
        
        # Build detailed vulnerability summary for LLM
        critical_vulns = [v for v in vulnerabilities if v.severity == "CRITICAL"]
        high_vulns = [v for v in vulnerabilities if v.severity == "HIGH"]
        medium_vulns = [v for v in vulnerabilities if v.severity == "MEDIUM"]
        low_vulns = [v for v in vulnerabilities if v.severity == "LOW"]
        
        # Build optimized prompt focusing on critical issues
        prompt_parts = [
            f'You are a security expert analyzing a code security scan for "{project_name}".',
            "",
            "SCAN SUMMARY:",
            f"- Total Issues: {len(vulnerabilities)}",
            f"- Critical: {severity_counts['CRITICAL']}",
            f"- High: {severity_counts['HIGH']}",
            f"- Medium: {severity_counts['MEDIUM']}",
            f"- Low: {severity_counts['LOW']}",
            "",
            "CRITICAL & HIGH SEVERITY ISSUES:",
        ]
        
        # Add critical vulnerabilities with detail (max 5)
        if critical_vulns:
            prompt_parts.append("\n🔴 CRITICAL Issues:")
            for i, vuln in enumerate(critical_vulns[:5], 1):
                desc = vuln.description[:150] + "..." if len(vuln.description) > 150 else vuln.description
                prompt_parts.extend([
                    f"{i}. {vuln.vulnerability_type}",
                    f"   File: {vuln.file_path}{':' + str(vuln.line_number) if vuln.line_number else ''}",
                    f"   Tool: {vuln.tool}",
                    f"   Description: {desc}",
                ])
        
        # Add high vulnerabilities (max 5)
        if high_vulns:
            prompt_parts.append("\n🟠 HIGH Severity Issues:")
            for i, vuln in enumerate(high_vulns[:5], 1):
                prompt_parts.extend([
                    f"{i}. {vuln.vulnerability_type}",
                    f"   File: {vuln.file_path}",
                    f"   Tool: {vuln.tool}",
                ])
        
        # Mention other severities briefly
        if medium_vulns or low_vulns:
            prompt_parts.append(f"\n(Also found {len(medium_vulns)} MEDIUM and {len(low_vulns)} LOW severity issues)")
        
        prompt = "\n".join(prompt_parts)
        
        prompt += """
Based on this security scan, provide:

1. **Priority Actions** (3-5 most critical fixes needed immediately)
2. **Root Cause Analysis** (What patterns or practices are causing these issues?)
3. **Implementation Roadmap** (Step-by-step plan to fix major issues)
4. **Best Practices** (2-3 security practices to prevent these issues)
5. **Quick Wins** (Easy fixes that can be done right away)

Focus on ACTIONABLE advice. Be specific about what to change and why. Keep the response concise and developer-friendly.
"""
        
        print(f"🤖 Requesting AI suggestions for scan #{scan_id}")
        print(f"   Total vulnerabilities: {len(vulnerabilities)}")
        
        # Send to LLM (with automatic fallback)
        result = send_prompt(prompt, max_tokens=2000, temperature=0.5)
        
        if result["success"]:
            # Save AI suggestions to database for future use
            try:
                from datetime import datetime
                scan.ai_suggestions = result["response"]
                scan.ai_model = result["model"]
                scan.ai_generated_at = datetime.utcnow()
                db.commit()
                print(f"💾 Saved AI suggestions to database for scan #{scan_id}")
            except Exception as save_error:
                print(f"⚠️  Failed to save AI suggestions: {save_error}")
                db.rollback()
                # Continue anyway - user still gets the response
            
            return {
                "success": True,
                "suggestions": result["response"],
                "model": result["model"],
                "summary": {
                    "total_issues": len(vulnerabilities),
                    "critical": severity_counts["CRITICAL"],
                    "high": severity_counts["HIGH"],
                    "medium": severity_counts["MEDIUM"],
                    "low": severity_counts["LOW"]
                },
                "cached": False,
                "generated_at": scan.ai_generated_at.isoformat() if scan.ai_generated_at else None,
                "usage": result.get("usage", {})
            }
        else:
            # LLM failed, return error
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis failed: {result.get('error', 'Unknown error')}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating AI suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI suggestions: {str(e)}"
        )
