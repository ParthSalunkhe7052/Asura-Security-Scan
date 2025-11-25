"""Quick migration to add AI suggestions columns"""
import sqlite3
from pathlib import Path

# Get database path
db_path = Path(__file__).parent / "asura.db"

print("=" * 60)
print("AI SUGGESTIONS MIGRATION")
print("=" * 60)
print(f"\nDatabase: {db_path}")

if not db_path.exists():
    print("\n❌ Database not found!")
    exit(1)

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

try:
    # Check if columns already exist
    cursor.execute("PRAGMA table_info(scans)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'ai_suggestions' in columns:
        print("\n✅ AI suggestions columns already exist!")
        print("   No migration needed.")
    else:
        print("\n📝 Adding AI suggestions columns...")
        
        # Add columns
        cursor.execute("ALTER TABLE scans ADD COLUMN ai_suggestions TEXT NULL")
        print("   ✅ Added ai_suggestions")
        
        cursor.execute("ALTER TABLE scans ADD COLUMN ai_model VARCHAR NULL")
        print("   ✅ Added ai_model")
        
        cursor.execute("ALTER TABLE scans ADD COLUMN ai_generated_at TIMESTAMP NULL")
        print("   ✅ Added ai_generated_at")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\nAI suggestions feature is now ready!")
        print("Restart your backend server to use it.")
        
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    conn.rollback()
    exit(1)
finally:
    conn.close()
