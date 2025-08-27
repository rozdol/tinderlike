from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import (
    UserCreate, UserResponse, Token, OAuthRequest,
    VerificationRequest, VerificationCodeRequest, MessageResponse,
    LoginRequest
)
from app.auth import create_access_token, get_current_user, get_password_hash, verify_password
from app.config import settings
from app.services.verification_service import verification_service
from app.services.oauth_service import oauth_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=MessageResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.phone == user_data.phone)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or phone already exists"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        phone=user_data.phone,
        username=user_data.username,
        full_name=user_data.full_name,
        password_hash=(get_password_hash(user_data.password) if user_data.password else None),
        is_active=False,
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification codes
    await verification_service.send_email_verification(db, user)
    await verification_service.send_phone_verification(db, user)
    
    return {"message": "Registration successful. Please verify your email and phone number."}


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login with email and password"""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not verified")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify", response_model=MessageResponse)
async def verify_account(verification_data: VerificationCodeRequest, db: Session = Depends(get_db)):
    """Verify user account with email and phone codes"""
    user = db.query(User).filter(User.email == verification_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify email code
    email_verified = verification_service.verify_code(
        db, user.id, verification_data.code, "email"
    )
    
    # Verify phone code (you might want to handle these separately)
    phone_verified = verification_service.verify_code(
        db, user.id, verification_data.code, "phone"
    )
    
    if email_verified:
        verification_service.mark_user_verified(db, user, "email")
    
    if phone_verified:
        verification_service.mark_user_verified(db, user, "phone")
    
    if email_verified or phone_verified:
        return {"message": "Account verified successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(verification_data: VerificationRequest, db: Session = Depends(get_db)):
    """Resend verification codes"""
    user = db.query(User).filter(User.email == verification_data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Resend verification codes
    await verification_service.send_email_verification(db, user)
    await verification_service.send_phone_verification(db, user)
    
    return {"message": "Verification codes sent successfully"}


@router.post("/oauth", response_model=Token)
async def oauth_login(oauth_data: OAuthRequest, db: Session = Depends(get_db)):
    """OAuth login with Google or Apple"""
    # Verify OAuth token
    user_info = await oauth_service.verify_oauth_token(oauth_data.provider, oauth_data.token)
    
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OAuth token"
        )
    
    # Check if user exists
    user = db.query(User).filter(
        (User.oauth_id == user_info["oauth_id"]) & 
        (User.oauth_provider == oauth_data.provider)
    ).first()
    
    if not user:
        # Create new user from OAuth
        user = User(
            email=user_info["email"] or f"{oauth_data.provider}_{user_info['oauth_id']}@example.com",
            phone="",  # OAuth users might not have phone initially
            full_name=user_info["name"],
            oauth_provider=oauth_data.provider,
            oauth_id=user_info["oauth_id"],
            is_active=True,
            is_verified=True,  # OAuth users are considered verified
            email_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
