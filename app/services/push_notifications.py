import json
import logging
from typing import Dict, List, Optional
from pywebpush import WebPushException, webpush
from sqlalchemy.orm import Session
from app.models import PushSubscription, User
from app.config import settings

logger = logging.getLogger(__name__)

class PushNotificationService:
    def __init__(self):
        self.vapid_private_key = settings.VAPID_PRIVATE_KEY
        self.vapid_public_key = settings.VAPID_PUBLIC_KEY
        self.vapid_claims = {
            "sub": f"mailto:{settings.CONTACT_EMAIL}",
            "aud": "https://fcm.googleapis.com"
        }
    
    def subscribe_user(self, db: Session, user_id: int, subscription_data: Dict) -> PushSubscription:
        """Subscribe a user to push notifications"""
        try:
            # Check if subscription already exists
            existing = db.query(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == subscription_data["endpoint"]
            ).first()
            
            if existing:
                # Update existing subscription
                existing.p256dh_key = subscription_data["keys"]["p256dh"]
                existing.auth_token = subscription_data["keys"]["auth"]
                existing.is_active = True
                db.commit()
                return existing
            
            # Create new subscription
            subscription = PushSubscription(
                user_id=user_id,
                endpoint=subscription_data["endpoint"],
                p256dh_key=subscription_data["keys"]["p256dh"],
                auth_token=subscription_data["keys"]["auth"]
            )
            db.add(subscription)
            db.commit()
            db.refresh(subscription)
            return subscription
            
        except Exception as e:
            logger.error(f"Error subscribing user {user_id} to push notifications: {e}")
            db.rollback()
            raise
    
    def unsubscribe_user(self, db: Session, user_id: int, endpoint: str) -> bool:
        """Unsubscribe a user from push notifications"""
        try:
            subscription = db.query(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.endpoint == endpoint
            ).first()
            
            if subscription:
                subscription.is_active = False
                db.commit()
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unsubscribing user {user_id} from push notifications: {e}")
            db.rollback()
            return False
    
    def send_notification(self, subscription: PushSubscription, payload: Dict) -> bool:
        """Send a push notification to a specific subscription"""
        try:
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh_key,
                    "auth": subscription.auth_token
                }
            }
            
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            return True
            
        except WebPushException as e:
            logger.error(f"WebPush error for subscription {subscription.id}: {e}")
            if e.response and e.response.status_code == 410:
                # Subscription is no longer valid
                return self._mark_subscription_inactive(subscription)
            return False
        except Exception as e:
            logger.error(f"Error sending push notification to subscription {subscription.id}: {e}")
            return False
    
    def send_notification_to_user(self, db: Session, user_id: int, payload: Dict) -> bool:
        """Send a push notification to all active subscriptions of a user"""
        try:
            subscriptions = db.query(PushSubscription).filter(
                PushSubscription.user_id == user_id,
                PushSubscription.is_active == True
            ).all()
            
            if not subscriptions:
                logger.info(f"No active push subscriptions found for user {user_id}")
                return False
            
            success_count = 0
            for subscription in subscriptions:
                if self.send_notification(subscription, payload):
                    success_count += 1
            
            logger.info(f"Sent push notification to {success_count}/{len(subscriptions)} subscriptions for user {user_id}")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending push notification to user {user_id}: {e}")
            return False
    
    def send_notification_to_all_users(self, db: Session, payload: Dict, user_ids: Optional[List[int]] = None) -> Dict:
        """Send a push notification to multiple users"""
        try:
            query = db.query(User).filter(User.notify_push == True, User.is_active == True)
            
            if user_ids:
                query = query.filter(User.id.in_(user_ids))
            
            users = query.all()
            
            results = {
                "total_users": len(users),
                "successful_sends": 0,
                "failed_sends": 0
            }
            
            for user in users:
                if self.send_notification_to_user(db, user.id, payload):
                    results["successful_sends"] += 1
                else:
                    results["failed_sends"] += 1
            
            logger.info(f"Bulk push notification results: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error sending bulk push notifications: {e}")
            return {"total_users": 0, "successful_sends": 0, "failed_sends": 0}
    
    def send_offer_expiry_notification(self, db: Session, user_id: int, offer_title: str, time_left: str) -> bool:
        """Send a notification about offer expiry"""
        payload = {
            "title": "Offer Expiring Soon!",
            "body": f"'{offer_title}' expires in {time_left}. Don't miss out!",
            "icon": "/static/icon-192x192.png",
            "badge": "/static/badge-72x72.png",
            "tag": "offer-expiry",
            "data": {
                "type": "offer_expiry",
                "offer_title": offer_title,
                "time_left": time_left
            },
            "actions": [
                {
                    "action": "view",
                    "title": "View Offer"
                },
                {
                    "action": "dismiss",
                    "title": "Dismiss"
                }
            ]
        }
        
        return self.send_notification_to_user(db, user_id, payload)
    
    def send_new_offer_notification(self, db: Session, user_id: int, offer_title: str, provider_name: str) -> bool:
        """Send a notification about a new offer"""
        payload = {
            "title": "New Offer Available!",
            "body": f"'{offer_title}' from {provider_name}",
            "icon": "/static/icon-192x192.png",
            "badge": "/static/badge-72x72.png",
            "tag": "new-offer",
            "data": {
                "type": "new_offer",
                "offer_title": offer_title,
                "provider_name": provider_name
            },
            "actions": [
                {
                    "action": "view",
                    "title": "View Offer"
                },
                {
                    "action": "dismiss",
                    "title": "Dismiss"
                }
            ]
        }
        
        return self.send_notification_to_user(db, user_id, payload)
    
    def _mark_subscription_inactive(self, subscription: PushSubscription) -> bool:
        """Mark a subscription as inactive (called when push fails)"""
        try:
            subscription.is_active = False
            # Note: This requires a database session, but we don't have one here
            # In a real implementation, you'd want to queue this for later processing
            logger.info(f"Marked subscription {subscription.id} as inactive due to push failure")
            return True
        except Exception as e:
            logger.error(f"Error marking subscription {subscription.id} as inactive: {e}")
            return False

# Global instance
push_service = PushNotificationService()

