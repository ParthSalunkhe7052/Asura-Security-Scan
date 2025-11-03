"""
Quick migration to add progress_log column
Run this after restarting the server
"""

import sqlite3
from pathlib import Path

def add_progress_log():
    db_path = Path(__file__).parent / "asura.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(scans)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'progress_log' not in columns:
            print("📝 Adding progress_log column...")
            cursor.execute("ALTER TABLE scans ADD COLUMN progress_log TEXT")
            conn.commit()
            print("✅ progress_log column added successfully")
        else:
            print("ℹ️  progress_log column already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Adding progress_log column...")
    add_progress_log()
