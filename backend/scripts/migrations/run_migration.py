#!/usr/bin/env python3
"""
Database Migration Script for AI Suggestions
Adds AI suggestions fields to the Scan table
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.database import DATABASE_URL

def run_migration():
    """Run the migration to add AI suggestions fields"""
    print("=" * 60)
    print("AI SUGGESTIONS MIGRATION")
    print("=" * 60)
    
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)
        
        print("\n1. Connecting to database...")
        with engine.connect() as conn:
            print("   ✅ Connected")
            
            # Check if columns already exist
            print("\n2. Checking if migration is needed...")
            result = conn.execute(text(
                "SELECT COUNT(*) FROM pragma_table_info('scans') WHERE name='ai_suggestions'"
            ))
            exists = result.scalar() > 0
            
            if exists:
                print("   ⚠️  AI suggestions columns already exist. Skipping migration.")
                return
            
            print("   Migration needed. Adding columns...")
            
            # Add columns
            print("\n3. Adding ai_suggestions column...")
            conn.execute(text("ALTER TABLE scans ADD COLUMN ai_suggestions TEXT NULL"))
            print("   ✅ Added ai_suggestions")
            
            print("\n4. Adding ai_model column...")
            conn.execute(text("ALTER TABLE scans ADD COLUMN ai_model VARCHAR NULL"))
            print("   ✅ Added ai_model")
            
            print("\n5. Adding ai_generated_at column...")
            conn.execute(text("ALTER TABLE scans ADD COLUMN ai_generated_at TIMESTAMP NULL"))
            print("   ✅ Added ai_generated_at")
            
            # Commit changes
            conn.commit()
            
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL")
        print("=" * 60)
        print("\nAI suggestions feature is now ready to use!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
