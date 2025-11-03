from sqlalchemy.orm import Session
from app.models.models import Scan, Vulnerability, Project, ScanStatusEnum, SeverityEnum
from app.core.scanner import SecurityScanner
from app.core.database import SessionLocal
from datetime import datetime
from typing import Optional
import time
import threading

class ScanService:
    @staticmethod
    def create_scan(db: Session, project_id: int, scan_type: str) -> Scan:
        """Create a new scan"""
        # Verify project exists
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Count existing scans for this project to generate scan number
        scan_count = db.query(Scan).filter(Scan.project_id == project_id).count()
        scan_number = scan_count + 1
        scan_name = f"{project.name} - Scan #{scan_number}"
        
        db_scan = Scan(
            project_id=project_id,
            scan_type=scan_type,
            scan_name=scan_name,
            status=ScanStatusEnum.PENDING
        )
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        return db_scan
    
    @staticmethod
    def run_security_scan(db: Session, scan_id: int) -> Scan:
        """Execute a security scan"""
        # Get initial scan info, then close the session
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")
        
        project_id = scan.project_id
        project_path = scan.project.path
        project_name = scan.project.name
        
        # Don't use the passed db session - it's tied to the request lifecycle
        # We'll create fresh sessions for each update
        db.close()
        
        # Update status to RUNNING with fresh session
        fresh_db = SessionLocal()
        try:
            scan = fresh_db.query(Scan).filter(Scan.id == scan_id).first()
            scan.status = ScanStatusEnum.RUNNING
            scan.progress_log = f"🚀 Initializing scan for: {project_name}"
            fresh_db.commit()
        finally:
            fresh_db.close()
        
        start_time = time.time()
        
        try:
            # Define callback to update progress in real-time
            # Use lock to prevent race conditions
            progress_lock = threading.Lock()
            
            def update_progress(progress_log):
                """Update progress with fresh DB session to avoid stale session issues"""
                with progress_lock:
                    session = SessionLocal()
                    try:
                        scan_obj = session.query(Scan).filter(Scan.id == scan_id).first()
                        if scan_obj:
                            scan_obj.progress_log = progress_log
                            session.commit()
                            print(f"📝 Progress updated: {len(progress_log)} chars")
                    except Exception as e:
                        print(f"⚠️  Failed to update progress: {e}")
                        session.rollback()
                    finally:
                        session.close()
            
            # Run the security scanner with scan_id for logging
            scanner = SecurityScanner(project_path, scan_id=str(scan_id))
            results = scanner.run_all(progress_callback=update_progress)
            
            # Save vulnerabilities to database with fresh session
            save_db = SessionLocal()
            scan = save_db.query(Scan).filter(Scan.id == scan_id).first()
            
            # Final progress update
            if hasattr(scanner, 'progress_messages'):
                scan.progress_log = '\n'.join(scanner.progress_messages)
                save_db.commit()
            
            # Save vulnerabilities to database
            for vuln_data in results["vulnerabilities"]:
                try:
                    vulnerability = Vulnerability(
                        scan_id=scan_id,
                        tool=vuln_data["tool"],
                        severity=SeverityEnum[vuln_data["severity"]],
                        file_path=vuln_data["file_path"],
                        line_number=vuln_data.get("line_number"),
                        vulnerability_type=vuln_data["vulnerability_type"],
                        description=vuln_data["description"],
                        code_snippet=vuln_data.get("code_snippet"),
                        cwe_id=vuln_data.get("cwe_id"),
                        confidence=vuln_data.get("confidence")
                    )
                    save_db.add(vulnerability)
                except Exception as vuln_err:
                    print(f"⚠️  Failed to save vulnerability: {vuln_err}")
                    # Continue with other vulnerabilities
                    continue
            
            # Determine final status based on scanner results
            overall_status = results.get("overall_status", "complete")
            if overall_status == "failed":
                scan.status = ScanStatusEnum.FAILED
                print(f"❌ Scan failed: All scanners failed")
            elif overall_status == "partial_complete":
                scan.status = ScanStatusEnum.COMPLETED
                failed_tools = results.get("failed_tools", [])
                print(f"⚠️  Scan partially completed. Failed tools: {', '.join(failed_tools)}")
                print(f"   Logs available at: {results.get('logs_path', 'logs/scans')}")
            else:
                scan.status = ScanStatusEnum.COMPLETED
                print(f"✅ Scan completed: {results['total_issues']} issues found")
            
            # Update scan with results
            scan.completed_at = datetime.utcnow()
            scan.duration_seconds = time.time() - start_time
            scan.total_issues = results["total_issues"]
            scan.health_score = ScanService._calculate_health_score(results["severity_counts"])
            
            # Add completion message to progress log
            completion_msg = f"\n\n✅ Scan completed in {scan.duration_seconds:.1f}s\n📊 Total issues found: {scan.total_issues}"
            if hasattr(scanner, 'progress_messages'):
                scan.progress_log = '\n'.join(scanner.progress_messages) + completion_msg
            else:
                scan.progress_log = (scan.progress_log or "") + completion_msg
            
            # Commit in a try-catch to ensure we handle any DB errors
            try:
                save_db.commit()
                print(f"✅ Scan #{scan_id} saved to database successfully")
            except Exception as commit_err:
                print(f"❌ Failed to commit scan: {commit_err}")
                save_db.rollback()
                # Try a simpler commit with just the scan, no vulnerabilities
                try:
                    scan.status = ScanStatusEnum.COMPLETED
                    scan.total_issues = results["total_issues"]
                    save_db.commit()
                    print(f"✅ Scan #{scan_id} saved (without vulnerabilities)")
                except:
                    print(f"❌ Could not save scan at all")
                    save_db.close()
                    raise
            
            save_db.refresh(scan)
            result_scan = scan
            save_db.close()
            return result_scan
            
        except Exception as e:
            print(f"❌ Scan failed with exception: {e}")
            # Always try to save the scan with failed status
            error_db = SessionLocal()
            try:
                scan = error_db.query(Scan).filter(Scan.id == scan_id).first()
                scan.status = ScanStatusEnum.FAILED
                scan.completed_at = datetime.utcnow()
                scan.duration_seconds = time.time() - start_time
                scan.total_issues = 0
                scan.health_score = 0
                scan.progress_log = (scan.progress_log or "") + f"\n\n❌ Scan failed: {str(e)}"
                error_db.commit()
                print(f"✅ Scan #{scan_id} marked as FAILED and saved")
                error_db.refresh(scan)
                result_scan = scan
                error_db.close()
                return result_scan
            except Exception as save_err:
                print(f"❌ Could not save failed scan status: {save_err}")
                error_db.rollback()
                error_db.close()
                raise
    
    @staticmethod
    def get_scan(db: Session, scan_id: int) -> Optional[Scan]:
        """Get a scan by ID"""
        return db.query(Scan).filter(Scan.id == scan_id).first()
    
    @staticmethod
    def get_scan_with_vulnerabilities(db: Session, scan_id: int) -> Optional[Scan]:
        """Get a scan with all its vulnerabilities"""
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if scan:
            # Eagerly load vulnerabilities
            _ = scan.vulnerabilities
        return scan
    
    @staticmethod
    def get_project_scans(db: Session, project_id: int, skip: int = 0, limit: int = 50):
        """Get all scans for a project"""
        return db.query(Scan).filter(Scan.project_id == project_id)\
            .order_by(Scan.started_at.desc())\
            .offset(skip).limit(limit).all()
    
    @staticmethod
    def _calculate_health_score(severity_counts: dict) -> float:
        """Calculate a health score based on vulnerabilities (0-100)"""
        # Weighted scoring: CRITICAL=10, HIGH=5, MEDIUM=2, LOW=1
        weights = {
            "CRITICAL": 10,
            "HIGH": 5,
            "MEDIUM": 2,
            "LOW": 1
        }
        
        total_penalty = sum(
            severity_counts.get(severity, 0) * weight 
            for severity, weight in weights.items()
        )
        
        # Convert to 0-100 score (100 = no issues, lower = more issues)
        # Using logarithmic scale for better distribution
        if total_penalty == 0:
            return 100.0
        
        score = max(0, 100 - (total_penalty * 2))
        return round(score, 2)
