from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import NotificationType, OfferCategory

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    phone: str
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    notify_whatsapp: Optional[bool] = None
    notify_telegram: Optional[bool] = None
    telegram_chat_id: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    email_verified: bool
    phone_verified: bool
    is_admin: bool
    created_at: datetime
    notify_email: bool
    notify_sms: bool
    notify_whatsapp: bool
    notify_telegram: bool
    telegram_chat_id: Optional[str] = None

    class Config:
        from_attributes = True

# Admin User Management
class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    email_verified: Optional[bool] = None
    phone_verified: Optional[bool] = None
    is_admin: Optional[bool] = None
    notify_email: Optional[bool] = None
    notify_sms: Optional[bool] = None
    notify_whatsapp: Optional[bool] = None
    notify_telegram: Optional[bool] = None
    telegram_chat_id: Optional[str] = None

class AdminUserResponse(UserResponse):
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    updated_at: Optional[datetime] = None

# Offer schemas
class OfferBase(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    provider_name: str
    category: OfferCategory
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    original_price: Optional[float] = None
    discounted_price: Optional[float] = None
    referral_link: Optional[str] = None
    promo_code: Optional[str] = None
    terms_conditions: Optional[str] = None
    instructions: Optional[str] = None
    expiry_date: datetime

class OfferCreate(OfferBase):
    pass

class OfferUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    provider_name: Optional[str] = None
    category: Optional[OfferCategory] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[float] = None
    original_price: Optional[float] = None
    discounted_price: Optional[float] = None
    referral_link: Optional[str] = None
    promo_code: Optional[str] = None
    terms_conditions: Optional[str] = None
    instructions: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class OfferResponse(OfferBase):
    id: int
    is_active: bool
    created_at: datetime
    time_until_expiry: Optional[str] = None

    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class OAuthRequest(BaseModel):
    provider: str  # google, apple
    token: str

class VerificationRequest(BaseModel):
    email: EmailStr
    phone: str
    email_code: str
    phone_code: str

class VerificationCodeRequest(BaseModel):
    email: EmailStr
    phone: str

class MessageResponse(BaseModel):
    message: str

# Swipe schemas
class SwipeRequest(BaseModel):
    offer_id: int
    action: str  # like, dislike

# Admin Action schemas
class AdminActionResponse(BaseModel):
    id: int
    admin_user_id: int
    action_type: str
    resource_type: str
    resource_id: int
    details: Optional[str] = None
    created_at: datetime
    admin_user: Optional[AdminUserResponse] = None

    class Config:
        from_attributes = True

# Statistics schemas
class AdminStats(BaseModel):
    total_users: int
    total_offers: int
    total_likes: int
    total_dislikes: int
    active_offers: int
    verified_users: int
    admin_users: int

# Notification schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    offer_id: int
    notification_type: NotificationType
    message: str
    sent_at: datetime
    is_read: bool

    class Config:
        from_attributes = True
