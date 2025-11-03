"""
Migration script to add scan_name field to existing scans
Run this once after updating the models.py
"""

import sqlite3
from pathlib import Path

def migrate_scan_names():
    """Add scan_name column and populate existing scans"""
    
    db_path = Path(__file__).parent / "asura.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(scans)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'scan_name' not in columns:
            print("📝 Adding scan_name column...")
            cursor.execute("ALTER TABLE scans ADD COLUMN scan_name TEXT")
            print("✅ Column added successfully")
        else:
            print("ℹ️  scan_name column already exists")
        
        # Get all projects
        cursor.execute("SELECT id, name FROM projects")
        projects = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Update existing scans with names
        cursor.execute("SELECT id, project_id FROM scans WHERE scan_name IS NULL")
        scans_to_update = cursor.fetchall()
        
        if not scans_to_update:
            print("ℹ️  No scans need updating")
        else:
            print(f"📝 Updating {len(scans_to_update)} scans...")
            
            # Count scans per project to generate correct numbers
            project_scan_counts = {}
            
            for scan_id, project_id in scans_to_update:
                if project_id not in project_scan_counts:
                    project_scan_counts[project_id] = 1
                else:
                    project_scan_counts[project_id] += 1
                
                project_name = projects.get(project_id, f"Project {project_id}")
                scan_number = project_scan_counts[project_id]
                scan_name = f"{project_name} - Scan #{scan_number}"
                
                cursor.execute(
                    "UPDATE scans SET scan_name = ? WHERE id = ?",
                    (scan_name, scan_id)
                )
            
            print(f"✅ Updated {len(scans_to_update)} scans")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting scan_name migration...")
    print("=" * 50)
    success = migrate_scan_names()
    print("=" * 50)
    
    if success:
        print("✨ You can now restart your backend server")
    else:
        print("⚠️  Please check the error and try again")
