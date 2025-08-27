from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate, MessageResponse
from app.auth import get_current_verified_user
from sqlalchemy import and_

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_verified_user)):
    """Get current user's profile"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update only provided fields
    if user_data.username is not None:
        # Check if username is already taken
        existing_user = db.query(User).filter(
            and_(User.username == user_data.username, User.id != current_user.id)
        ).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_data.username
    
    if user_data.full_name is not None:
        current_user.full_name = user_data.full_name
    
    if user_data.notify_email is not None:
        current_user.notify_email = user_data.notify_email
    
    if user_data.notify_sms is not None:
        current_user.notify_sms = user_data.notify_sms
    
    if user_data.notify_whatsapp is not None:
        current_user.notify_whatsapp = user_data.notify_whatsapp
    
    if user_data.notify_telegram is not None:
        current_user.notify_telegram = user_data.notify_telegram
    
    if user_data.telegram_chat_id is not None:
        current_user.telegram_chat_id = user_data.telegram_chat_id
    
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/telegram-connect", response_model=MessageResponse)
async def connect_telegram(
    chat_id: str,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Connect Telegram chat ID for notifications"""
    current_user.telegram_chat_id = chat_id
    current_user.notify_telegram = True
    db.commit()
    
    return {"message": "Telegram connected successfully"}


@router.delete("/telegram-disconnect", response_model=MessageResponse)
async def disconnect_telegram(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Disconnect Telegram notifications"""
    current_user.telegram_chat_id = None
    current_user.notify_telegram = False
    db.commit()
    
    return {"message": "Telegram disconnected successfully"}
