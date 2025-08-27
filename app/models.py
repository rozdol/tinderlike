from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class NotificationType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"

class OfferCategory(str, enum.Enum):
    ECOMMERCE = "ecommerce"
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    TRAVEL = "travel"
    FINANCE = "finance"
    HEALTH = "health"
    EDUCATION = "education"
    OTHER = "other"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    # Password hash for password-based login
    password_hash = Column(String)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)  # Admin flag
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # OAuth fields
    oauth_provider = Column(String)  # google, apple, etc.
    oauth_id = Column(String)
    
    # Notification preferences
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_whatsapp = Column(Boolean, default=False)
    notify_telegram = Column(Boolean, default=False)
    telegram_chat_id = Column(String)
    
    # Relationships
    likes = relationship("UserLike", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    admin_actions = relationship("AdminAction", back_populates="admin_user")


class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    image_url = Column(String)
    provider_name = Column(String, nullable=False)
    category = Column(Enum(OfferCategory), nullable=False)
    discount_percentage = Column(Float)
    discount_amount = Column(Float)
    original_price = Column(Float)
    discounted_price = Column(Float)
    referral_link = Column(String)
    promo_code = Column(String)
    terms_conditions = Column(Text)
    instructions = Column(Text)
    expiry_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    likes = relationship("UserLike", back_populates="offer")


class UserLike(Base):
    __tablename__ = "user_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    action = Column(String, nullable=False)  # 'like' or 'dislike'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="likes")
    offer = relationship("Offer", back_populates="likes")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    is_read = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    offer = relationship("Offer")


class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String, nullable=False)
    type = Column(String, nullable=False)  # email, phone
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AdminAction(Base):
    __tablename__ = "admin_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # create, update, delete
    resource_type = Column(String, nullable=False)  # user, offer
    resource_id = Column(Integer, nullable=False)
    details = Column(Text)  # JSON string with action details
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    admin_user = relationship("User", back_populates="admin_actions")
