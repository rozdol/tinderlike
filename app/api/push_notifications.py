from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.auth import get_current_user
from app.models import User, PushSubscription
from app.services.push_notifications import push_service
from app.schemas import PushSubscriptionCreate, PushSubscriptionResponse, MessageResponse

router = APIRouter()

@router.post("/subscribe", response_model=PushSubscriptionResponse)
async def subscribe_to_push_notifications(
    subscription_data: PushSubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subscribe user to push notifications"""
    try:
        # Check if user has push notifications enabled
        if not current_user.notify_push:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Push notifications are disabled for this user"
            )
        
        subscription = push_service.subscribe_user(db, current_user.id, subscription_data.dict())
        
        return PushSubscriptionResponse(
            id=subscription.id,
            user_id=subscription.user_id,
            endpoint=subscription.endpoint,
            is_active=subscription.is_active,
            created_at=subscription.created_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to subscribe to push notifications: {str(e)}"
        )

@router.delete("/unsubscribe", response_model=MessageResponse)
async def unsubscribe_from_push_notifications(
    endpoint: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unsubscribe user from push notifications"""
    try:
        success = push_service.unsubscribe_user(db, current_user.id, endpoint)
        
        if success:
            return {"message": "Successfully unsubscribed from push notifications"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Push subscription not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unsubscribe from push notifications: {str(e)}"
        )

@router.get("/subscriptions", response_model=List[PushSubscriptionResponse])
async def get_user_push_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all push subscriptions for the current user"""
    try:
        subscriptions = db.query(PushSubscription).filter(
            PushSubscription.user_id == current_user.id,
            PushSubscription.is_active == True
        ).all()
        
        return [
            PushSubscriptionResponse(
                id=sub.id,
                user_id=sub.user_id,
                endpoint=sub.endpoint,
                is_active=sub.is_active,
                created_at=sub.created_at
            )
            for sub in subscriptions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get push subscriptions: {str(e)}"
        )

@router.post("/test", response_model=MessageResponse)
async def test_push_notification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a test push notification to the current user"""
    try:
        # Check if user has push notifications enabled
        if not current_user.notify_push:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Push notifications are disabled for this user"
            )
        
        # Send test notification
        payload = {
            "title": "Test Notification",
            "body": "This is a test push notification from Tinder-like App!",
            "icon": "/static/icon-192x192.png",
            "badge": "/static/badge-72x72.png",
            "tag": "test",
            "data": {
                "type": "test",
                "message": "Test notification received successfully"
            }
        }
        
        success = push_service.send_notification_to_user(db, current_user.id, payload)
        
        if success:
            return {"message": "Test push notification sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active push subscriptions found for this user"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test push notification: {str(e)}"
        )

@router.get("/vapid-public-key")
async def get_vapid_public_key():
    """Get the VAPID public key for client-side subscription"""
    return {"public_key": push_service.vapid_public_key}

