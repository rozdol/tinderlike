#!/usr/bin/env python3
"""
Test script to verify push notification settings are working correctly
"""

import os
import sys
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import User
from app.config import settings

def test_push_settings():
    """Test push notification settings"""
    
    # Create database engine
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        print("🔍 Testing push notification settings...")
        print("=" * 50)
        
        for user in users:
            print(f"User: {user.email}")
            print(f"  - notify_push: {user.notify_push}")
            print(f"  - notify_email: {user.notify_email}")
            print(f"  - notify_sms: {user.notify_sms}")
            print(f"  - notify_whatsapp: {user.notify_whatsapp}")
            print(f"  - notify_telegram: {user.notify_telegram}")
            print()
        
        # Test updating a user's push notification setting
        test_user = db.query(User).filter(User.email == "john@example.com").first()
        if test_user:
            print("🧪 Testing push notification update...")
            original_setting = test_user.notify_push
            test_user.notify_push = not original_setting
            db.commit()
            
            # Verify the change
            db.refresh(test_user)
            if test_user.notify_push != original_setting:
                print("✅ Push notification setting update successful!")
            else:
                print("❌ Push notification setting update failed!")
            
            # Revert the change
            test_user.notify_push = original_setting
            db.commit()
            print("🔄 Reverted test change")
        
        print("=" * 50)
        print("✅ Push notification settings test complete!")
            
    except Exception as e:
        print(f"❌ Error testing push settings: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_push_settings()

