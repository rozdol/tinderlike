import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings
from app.models import NotificationType
import httpx
import asyncio


class NotificationService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.twilio_account_sid = settings.twilio_account_sid
        self.twilio_auth_token = settings.twilio_auth_token
        self.twilio_phone_number = settings.twilio_phone_number
        self.telegram_bot_token = settings.telegram_bot_token
    
    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, to_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    async def send_sms(self, phone_number: str, message: str) -> bool:
        """Send SMS notification using Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            return False
        
        try:
            from twilio.rest import Client
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=phone_number
            )
            return True
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False
    
    async def send_telegram(self, chat_id: str, message: str) -> bool:
        """Send Telegram notification"""
        if not self.telegram_bot_token:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data)
                return response.status_code == 200
        except Exception as e:
            print(f"Telegram sending failed: {e}")
            return False
    
    async def send_whatsapp(self, phone_number: str, message: str) -> bool:
        """Send WhatsApp notification using Twilio"""
        if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            return False
        
        try:
            from twilio.rest import Client
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=f"whatsapp:{self.twilio_phone_number}",
                to=f"whatsapp:{phone_number}"
            )
            return True
        except Exception as e:
            print(f"WhatsApp sending failed: {e}")
            return False
    
    async def send_notification(self, notification_type: NotificationType, **kwargs) -> bool:
        """Send notification based on type"""
        if notification_type == NotificationType.EMAIL:
            return await self.send_email(
                kwargs.get('to_email'),
                kwargs.get('subject', 'Offer Notification'),
                kwargs.get('body')
            )
        elif notification_type == NotificationType.SMS:
            return await self.send_sms(
                kwargs.get('phone_number'),
                kwargs.get('message')
            )
        elif notification_type == NotificationType.TELEGRAM:
            return await self.send_telegram(
                kwargs.get('chat_id'),
                kwargs.get('message')
            )
        elif notification_type == NotificationType.WHATSAPP:
            return await self.send_whatsapp(
                kwargs.get('phone_number'),
                kwargs.get('message')
            )
        return False


notification_service = NotificationService()
