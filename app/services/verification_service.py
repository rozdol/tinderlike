import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import User, VerificationCode
from app.services.notification_service import notification_service
from app.models import NotificationType


class VerificationService:
    def __init__(self):
        self.code_length = 6
        self.code_expiry_minutes = 10
    
    def generate_verification_code(self) -> str:
        """Generate a random 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=self.code_length))
    
    def create_verification_code(self, db: Session, user_id: int, code_type: str) -> VerificationCode:
        """Create a new verification code for user"""
        code = self.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=self.code_expiry_minutes)
        
        verification_code = VerificationCode(
            user_id=user_id,
            code=code,
            type=code_type,
            expires_at=expires_at
        )
        
        db.add(verification_code)
        db.commit()
        db.refresh(verification_code)
        
        return verification_code
    
    async def send_email_verification(self, db: Session, user: User) -> bool:
        """Send email verification code"""
        verification_code = self.create_verification_code(db, user.id, "email")
        
        subject = "Email Verification - TinderLike Offers"
        body = f"""
        <html>
        <body>
            <h2>Email Verification</h2>
            <p>Your verification code is: <strong>{verification_code.code}</strong></p>
            <p>This code will expire in {self.code_expiry_minutes} minutes.</p>
            <p>If you didn't request this verification, please ignore this email.</p>
        </body>
        </html>
        """
        
        return await notification_service.send_email(user.email, subject, body)
    
    async def send_phone_verification(self, db: Session, user: User) -> bool:
        """Send phone verification code via SMS"""
        verification_code = self.create_verification_code(db, user.id, "phone")
        
        message = f"Your verification code is: {verification_code.code}. Expires in {self.code_expiry_minutes} minutes."
        
        return await notification_service.send_sms(user.phone, message)
    
    def verify_code(self, db: Session, user_id: int, code: str, code_type: str) -> bool:
        """Verify the provided code"""
        verification_code = db.query(VerificationCode).filter(
            VerificationCode.user_id == user_id,
            VerificationCode.code == code,
            VerificationCode.type == code_type,
            VerificationCode.is_used == False,
            VerificationCode.expires_at > datetime.utcnow()
        ).first()
        
        if verification_code:
            verification_code.is_used = True
            db.commit()
            return True
        
        return False
    
    def mark_user_verified(self, db: Session, user: User, verification_type: str):
        """Mark user as verified based on verification type"""
        if verification_type == "email":
            user.email_verified = True
        elif verification_type == "phone":
            user.phone_verified = True
        
        # Check if both email and phone are verified
        if user.email_verified and user.phone_verified:
            user.is_verified = True
            user.is_active = True
        
        db.commit()
        db.refresh(user)


verification_service = VerificationService()
