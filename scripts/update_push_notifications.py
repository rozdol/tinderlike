#!/usr/bin/env python3
"""
Update existing users to include notify_push field
Run this script to add the notify_push field to existing users in the database
"""

import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import User
from app.config import settings

def update_push_notifications():
    """Update existing users to include notify_push field"""
    
    # Create database engine
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        updated_count = 0
        for user in users:
            # Check if notify_push field is None (not set)
            if not hasattr(user, 'notify_push') or user.notify_push is None:
                user.notify_push = True  # Default to enabled
                updated_count += 1
                print(f"Updated user {user.email} with notify_push=True")
        
        if updated_count > 0:
            db.commit()
            print(f"\n✅ Successfully updated {updated_count} users with notify_push field")
        else:
            print("\n✅ All users already have notify_push field set")
            
    except Exception as e:
        print(f"❌ Error updating users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔄 Updating existing users with notify_push field...")
    update_push_notifications()
    print("✅ Update complete!")

