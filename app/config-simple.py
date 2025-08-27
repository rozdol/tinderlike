import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    # Database (SQLite for immediate testing)
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./tinderlike.db")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Email Configuration
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "your-app-password")
    
    # SMS Configuration (Twilio)
    twilio_account_sid: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Telegram Configuration
    telegram_bot_token: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # OAuth Configuration
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    apple_client_id: Optional[str] = os.getenv("APPLE_CLIENT_ID")
    apple_team_id: Optional[str] = os.getenv("APPLE_TEAM_ID")
    apple_key_id: Optional[str] = os.getenv("APPLE_KEY_ID")
    apple_private_key: Optional[str] = os.getenv("APPLE_PRIVATE_KEY")
    
    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Frontend URL
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")


settings = Settings()
