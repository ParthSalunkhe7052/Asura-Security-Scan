"""
Database migration to add notifications table
Run this script to update the database schema
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.database import init_db, SessionLocal, engine
from app.models.models import Base, Notification
from sqlalchemy import inspect

def migrate():
    print("=" * 60)
    print("DATABASE MIGRATION: Adding Notifications Table")
    print("=" * 60)
    
    # Initialize database (creates all tables if they don't exist)
    init_db()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Check if notifications table already exists
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'notifications' in tables:
            print("✅ Notifications table already exists")
        else:
            print("📝 Creating notifications table...")
            # Create only the notifications table
            Notification.__table__.create(engine, checkfirst=True)
            print("✅ Notifications table created successfully")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Restart the backend server")
        print("2. Start a new scan to see real notifications")
        print("3. Check the notification bell icon in the UI")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
