from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.scan import ScanCreate, ScanResponse, ScanDetailResponse, VulnerabilityResponse
from app.services.scan_service import ScanService
from app.core import llm_adapter
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

@router.get("/{scan_id}/vulnerabilities", response_model=Dict[str, Any])
async def get_scan_vulnerabilities(
    scan_id: int,
    skip: int = 0,
    limit: int = 50,
    severity: str = None,
    tool: str = None,
    db: Session = Depends(get_db)
):
    """
    Get vulnerabilities for a specific scan with pagination and filtering.
    
    Args:
        scan_id: ID of the scan
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (max: 200)
        severity: Optional filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
        tool: Optional filter by tool (bandit, safety, semgrep)
    
    Returns:
        Dict with vulnerabilities, total count, and pagination info
    """
    from app.models.models import Vulnerability, SeverityEnum
    
    # Check if scan exists
    scan = ScanService.get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Enforce limit bounds
    limit = min(limit, 200)  # Max 200 items per page
    
    # Build query with filters
    query = db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id)
    
    # Apply severity filter if provided
    if severity:
        try:
            severity_enum = SeverityEnum[severity.upper()]
            query = query.filter(Vulnerability.severity == severity_enum)
        except KeyError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid severity. Must be one of: {', '.join([s.name for s in SeverityEnum])}"
            )
    
    # Apply tool filter if provided
    if tool:
        valid_tools = ["bandit", "safety", "semgrep"]
        if tool.lower() not in valid_tools:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid tool. Must be one of: {', '.join(valid_tools)}"
            )
        query = query.filter(Vulnerability.tool == tool.lower())
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination and order by severity (CRITICAL first)
    vulnerabilities = query.order_by(
        Vulnerability.severity,
        Vulnerability.id
    ).offset(skip).limit(limit).all()
    
    # Convert ORM objects to Pydantic schemas for proper serialization
    vulnerability_responses = [
        VulnerabilityResponse.from_orm(v) for v in vulnerabilities
    ]
    
    # Calculate pagination metadata
    has_next = (skip + limit) < total_count
    has_prev = skip > 0
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    current_page = (skip // limit) + 1
    
    return {
        "vulnerabilities": vulnerability_responses,
        "pagination": {
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "current_page": current_page,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_prev": has_prev
        },
        "filters": {
            "severity": severity,
            "tool": tool
        }
    }


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
            "CRITICAL": len([v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "CRITICAL"]),
            "HIGH": len([v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "HIGH"]),
            "MEDIUM": len([v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "MEDIUM"]),
            "LOW": len([v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "LOW"])
        }
        
        # Build detailed vulnerability summary for LLM
        critical_vulns = [v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "CRITICAL"]
        high_vulns = [v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "HIGH"]
        medium_vulns = [v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "MEDIUM"]
        low_vulns = [v for v in vulnerabilities if getattr(v.severity, "value", str(v.severity)) == "LOW"]
        
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
        
        # Build AI Auto Fix Prompt section with all vulnerabilities
        auto_fix_prompt_parts = [
            "",
            "---",
            "",
            "## 🤖 AI AUTO FIX PROMPT",
            "",
            "I need you to fix the following security vulnerabilities in my codebase:",
            ""
        ]
        
        # Group vulnerabilities by file
        from collections import defaultdict
        vulns_by_file = defaultdict(list)
        for vuln in vulnerabilities:
            vulns_by_file[vuln.file_path].append(vuln)
        
        # Add each file's vulnerabilities to the auto-fix prompt
        for file_path, file_vulns in sorted(vulns_by_file.items()):
            auto_fix_prompt_parts.append(f"**File: `{file_path}`**")
            for vuln in file_vulns:
                severity = getattr(vuln.severity, "value", str(vuln.severity))
                line_info = f" at line {vuln.line_number}" if vuln.line_number else ""
                auto_fix_prompt_parts.append(f"- **[{severity}]** {vuln.vulnerability_type}{line_info}")
                auto_fix_prompt_parts.append(f"  - Tool: {vuln.tool}")
                if vuln.description:
                    desc = vuln.description[:200] + "..." if len(vuln.description) > 200 else vuln.description
                    auto_fix_prompt_parts.append(f"  - Issue: {desc}")
            auto_fix_prompt_parts.append("")
        
        auto_fix_prompt_parts.append("Please make the necessary changes to address these security issues while maintaining code functionality and following security best practices.")
        
        auto_fix_prompt = "\n".join(auto_fix_prompt_parts)
        
        prompt += f"""
Based on this security scan, provide a **comprehensive and engaging security report**. 

**Role**: You are an elite Cybersecurity Consultant advising a development team. Your tone should be professional yet encouraging, authoritative but accessible.

**Format Requirements**:
- Use **Markdown** heavily (headers, bolding, lists).
- Use **Emojis** 🛡️ ⚠️ 🚀 to make sections pop.
- Use **Code Blocks** for specific fix examples.
- Avoid walls of text; use bullet points and short paragraphs.

**Report Structure**:
1.  **🚨 Executive Summary**: A 2-sentence high-level assessment of the project's security posture.
2.  **🔥 Critical Fixes (Priority Actions)**: The top 3-5 things that must be fixed TODAY. Explain *why* and *how* (with code examples).
3.  **🕵️ Root Cause Analysis**: What patterns are causing these issues? (e.g., "Lack of input sanitization", "Hardcoded secrets").
4.  **🛡️ Defense Strategy**: 2-3 best practices to prevent this in the future.
5.  **✨ Quick Wins**: Low-hanging fruit that improves security with minimal effort.

**IMPORTANT**: End your report with the exact AI Auto Fix Prompt section below (copy it exactly as-is):

{auto_fix_prompt}

Make the developer feel empowered to fix these issues!
"""
        
        print(f"🤖 Requesting AI suggestions for scan #{scan_id}")
        print(f"   Total vulnerabilities: {len(vulnerabilities)}")
        
        # Send to LLM (with automatic fallback)
        result = llm_adapter.send_prompt(prompt, max_tokens=2000, temperature=0.5)
        
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
            fallback = [
                "AI suggestions unavailable.",
                f"Critical issues: {severity_counts['CRITICAL']}",
                f"High issues: {severity_counts['HIGH']}",
                "Focus on remediating critical findings first, then high.",
                "Apply security best practices, update vulnerable dependencies, and add input validation."
            ]
            message = result.get("error") or "LLM unavailable"
            return {
                "success": True,
                "suggestions": "\n".join(fallback),
                "model": None,
                "summary": {
                    "total_issues": len(vulnerabilities),
                    "critical": severity_counts["CRITICAL"],
                    "high": severity_counts["HIGH"],
                    "medium": severity_counts["MEDIUM"],
                    "low": severity_counts["LOW"]
                },
                "cached": False,
                "generated_at": None,
                "usage": {},
                "message": message
            }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error generating AI suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate AI suggestions: {str(e)}"
        )
