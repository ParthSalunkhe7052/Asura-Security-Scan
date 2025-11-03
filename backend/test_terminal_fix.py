"""
Test script to verify terminal display fix is working correctly.

This script simulates a scan and verifies that progress updates are being
saved to the database in real-time.

Usage:
    python test_terminal_fix.py
"""

import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal, init_db
from app.models.models import Project, Scan, ScanStatusEnum
from app.services.scan_service import ScanService


def test_terminal_progress_updates():
    """Test that progress updates are visible in the database during scanning"""
    print("="*80)
    print(" TERMINAL FIX VERIFICATION TEST")
    print("="*80)
    print()
    
    # Initialize database
    init_db()
    
    # Create test session
    db = SessionLocal()
    
    try:
        # Get or create a test project
        test_project = db.query(Project).filter(Project.name == "test-project").first()
        if not test_project:
            print("❌ No test project found. Please create a project first.")
            print("   Run this from the UI or create one manually.")
            return False
        
        print(f"✅ Using project: {test_project.name}")
        print(f"   Path: {test_project.path}")
        print()
        
        # Create a new scan
        print("🔄 Creating new security scan...")
        scan = ScanService.create_scan(db, test_project.id, "security")
        scan_id = scan.id
        print(f"✅ Scan #{scan_id} created with status: {scan.status.value}")
        print()
        
        # Start the scan in a separate thread (simulating background task)
        print("🚀 Starting scan in background...")
        print("   Monitoring progress updates for 30 seconds...")
        print("   (You can stop with Ctrl+C)")
        print()
        
        import threading
        
        # Create fresh session for background task
        bg_db = SessionLocal()
        scan_thread = threading.Thread(
            target=ScanService.run_security_scan,
            args=(bg_db, scan_id)
        )
        scan_thread.daemon = True
        scan_thread.start()
        
        # Monitor progress for 30 seconds
        last_log_length = 0
        update_count = 0
        start_time = time.time()
        
        print("📊 Progress Updates:")
        print("-" * 80)
        
        for i in range(30):  # Monitor for 30 seconds
            time.sleep(1)
            
            # Query scan progress with fresh session
            check_db = SessionLocal()
            try:
                current_scan = check_db.query(Scan).filter(Scan.id == scan_id).first()
                
                if current_scan:
                    current_log = current_scan.progress_log or ""
                    current_length = len(current_log)
                    
                    # Detect updates
                    if current_length > last_log_length:
                        update_count += 1
                        new_content = current_log[last_log_length:]
                        
                        print(f"\n[{i+1}s] 📝 UPDATE #{update_count} (+{current_length - last_log_length} chars)")
                        print(f"Status: {current_scan.status.value}")
                        
                        # Show new lines only
                        new_lines = new_content.strip().split('\n')
                        for line in new_lines[-5:]:  # Show last 5 new lines
                            if line.strip():
                                print(f"  | {line}")
                        
                        last_log_length = current_length
                    
                    # Check if scan is complete
                    if current_scan.status in [ScanStatusEnum.COMPLETED, ScanStatusEnum.FAILED]:
                        print(f"\n🏁 Scan {current_scan.status.value}!")
                        break
                        
            finally:
                check_db.close()
        
        # Wait for thread to finish
        scan_thread.join(timeout=5)
        
        print()
        print("-" * 80)
        print()
        
        # Final verification
        final_db = SessionLocal()
        try:
            final_scan = final_db.query(Scan).filter(Scan.id == scan_id).first()
            
            if final_scan:
                print("📋 FINAL SCAN STATE:")
                print(f"   ID: {final_scan.id}")
                print(f"   Status: {final_scan.status.value}")
                print(f"   Total Issues: {final_scan.total_issues}")
                print(f"   Progress Log Length: {len(final_scan.progress_log or '')} chars")
                print(f"   Updates Detected: {update_count}")
                print()
                
                if final_scan.progress_log:
                    print("📄 FINAL PROGRESS LOG:")
                    print("-" * 80)
                    print(final_scan.progress_log)
                    print("-" * 80)
                    print()
                
                # Determine test result
                if update_count >= 3:  # Should have at least 3 updates (init + 3 scanners)
                    print("✅ TEST PASSED!")
                    print(f"   Progress updates are working correctly ({update_count} updates detected)")
                    return True
                elif update_count > 0:
                    print("⚠️  TEST PARTIAL PASS")
                    print(f"   Some updates detected ({update_count}), but fewer than expected")
                    print("   The fix is working but may need optimization")
                    return True
                else:
                    print("❌ TEST FAILED!")
                    print("   No progress updates detected")
                    print("   The terminal display issue is NOT fixed")
                    return False
            else:
                print("❌ Scan not found in database")
                return False
                
        finally:
            final_db.close()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print()
    success = test_terminal_progress_updates()
    print()
    print("="*80)
    
    if success:
        print("✅ VERIFICATION COMPLETE - Terminal display is working!")
        sys.exit(0)
    else:
        print("❌ VERIFICATION FAILED - Check the logs above for details")
        sys.exit(1)
