#!/usr/bin/env python3
"""
Seed script to populate the database with sample data for testing.
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import User, Offer, OfferCategory
from app.auth import get_password_hash
from app.database import get_db
from app.config import settings

def seed_data():
    # Create database engine
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Get default password from environment or use default
        default_password = os.getenv("SEED_USER_PASSWORD", "password123")
        
        # Create admin user
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                phone="+1234567890",
                username="admin",
                full_name="Admin User",
                password_hash=get_password_hash(default_password),
                is_active=True,
                is_verified=True,
                email_verified=True,
                phone_verified=True,
                is_admin=True,  # Make this user an admin
                notify_email=True,
                notify_sms=False,
                notify_whatsapp=False,
                notify_telegram=False
            )
            db.add(admin_user)
            print("Created admin user: admin@example.com")
        else:
            # Update existing user to be admin
            admin_user.is_admin = True
            admin_user.password_hash = get_password_hash(default_password)
            print("Updated existing user to admin: admin@example.com")
        
        # Create regular users
        users_data = [
            {
                "email": "john@example.com",
                "phone": "+1234567891",
                "username": "john_doe",
                "full_name": "John Doe",
                "is_admin": False
            },
            {
                "email": "jane@example.com", 
                "phone": "+1234567892",
                "username": "jane_smith",
                "full_name": "Jane Smith",
                "is_admin": False
            },
            {
                "email": "bob@example.com",
                "phone": "+1234567893", 
                "username": "bob_wilson",
                "full_name": "Bob Wilson",
                "is_admin": False
            }
        ]
        
        for user_data in users_data:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if not user:
                user = User(
                    email=user_data["email"],
                    phone=user_data["phone"],
                    username=user_data["username"],
                    full_name=user_data["full_name"],
                    password_hash=get_password_hash(default_password),
                    is_active=True,
                    is_verified=True,
                    email_verified=True,
                    phone_verified=True,
                    is_admin=user_data["is_admin"],
                    notify_email=True,
                    notify_sms=False,
                    notify_whatsapp=False,
                    notify_telegram=False
                )
                db.add(user)
                print(f"Created user: {user_data['email']}")
            else:
                # Update existing user with password hash and admin status
                user.password_hash = get_password_hash(default_password)
                user.is_admin = user_data["is_admin"]
                print(f"Updated existing user: {user_data['email']}")
        
        # Create offers
        offers_data = [
            {
                "title": "50% Off Electronics",
                "description": "Get 50% off on all electronics at TechStore",
                "image_url": "https://picsum.photos/300/200?random=1",
                "provider_name": "TechStore",
                "category": OfferCategory.ECOMMERCE,
                "discount_percentage": 50.0,
                "original_price": 1000.0,
                "discounted_price": 500.0,
                "referral_link": "https://techstore.com/ref/123",
                "promo_code": "TECH50",
                "terms_conditions": "Valid for new customers only",
                "instructions": "Use promo code TECH50 at checkout",
                "expiry_date": datetime.now(timezone.utc) + timedelta(days=7)
            },
            {
                "title": "Free Delivery on Food Orders",
                "description": "Free delivery on all food orders over $30",
                "image_url": "https://picsum.photos/300/200?random=2",
                "provider_name": "FoodExpress",
                "category": OfferCategory.FOOD,
                "discount_amount": 5.0,
                "original_price": 35.0,
                "discounted_price": 30.0,
                "referral_link": "https://foodexpress.com/ref/456",
                "promo_code": "FREEDEL",
                "terms_conditions": "Minimum order $30",
                "instructions": "Add items to cart and use code FREEDEL",
                "expiry_date": datetime.now(timezone.utc) + timedelta(days=3)
            },
            {
                "title": "Movie Tickets Buy 1 Get 1",
                "description": "Buy one movie ticket, get one free at CineMax",
                "image_url": "https://picsum.photos/300/200?random=3",
                "provider_name": "CineMax",
                "category": OfferCategory.ENTERTAINMENT,
                "discount_percentage": 50.0,
                "original_price": 20.0,
                "discounted_price": 10.0,
                "referral_link": "https://cinemax.com/ref/789",
                "promo_code": "BOGO",
                "terms_conditions": "Valid for any movie, any day",
                "instructions": "Purchase one ticket and use code BOGO for second ticket",
                "expiry_date": datetime.now(timezone.utc) + timedelta(days=14)
            },
            {
                "title": "Hotel Booking 30% Off",
                "description": "30% off on hotel bookings worldwide",
                "image_url": "https://picsum.photos/300/200?random=4",
                "provider_name": "TravelPro",
                "category": OfferCategory.TRAVEL,
                "discount_percentage": 30.0,
                "original_price": 200.0,
                "discounted_price": 140.0,
                "referral_link": "https://travelpro.com/ref/101",
                "promo_code": "TRAVEL30",
                "terms_conditions": "Valid for bookings made 7 days in advance",
                "instructions": "Book your hotel and use code TRAVEL30",
                "expiry_date": datetime.now(timezone.utc) + timedelta(days=30)
            },
            {
                "title": "Investment Platform Zero Fees",
                "description": "Zero trading fees for first 10 trades",
                "image_url": "https://picsum.photos/300/200?random=5",
                "provider_name": "InvestSmart",
                "category": OfferCategory.FINANCE,
                "discount_amount": 10.0,
                "original_price": 10.0,
                "discounted_price": 0.0,
                "referral_link": "https://investsmart.com/ref/202",
                "promo_code": "ZEROFEES",
                "terms_conditions": "New accounts only, first 10 trades",
                "instructions": "Open account and use code ZEROFEES",
                "expiry_date": datetime.now(timezone.utc) + timedelta(days=60)
            }
        ]
        
        for offer_data in offers_data:
            existing_offer = db.query(Offer).filter(
                Offer.title == offer_data["title"],
                Offer.provider_name == offer_data["provider_name"]
            ).first()
            
            if not existing_offer:
                offer = Offer(**offer_data)
                db.add(offer)
                print(f"Created offer: {offer_data['title']}")
            else:
                print(f"Offer already exists: {offer_data['title']}")
        
        db.commit()
        print("\n✅ Database seeded successfully!")
        print(f"\n📋 Login Credentials:")
        print(f"Admin: admin@example.com / {default_password}")
        print(f"User 1: john@example.com / {default_password}")
        print(f"User 2: jane@example.com / {default_password}")
        print(f"User 3: bob@example.com / {default_password}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
