from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, not_
from app.database import get_db
from app.models import User, Offer, UserLike, OfferCategory
from app.schemas import (
    OfferResponse, SwipeRequest,
    MessageResponse
)
from app.auth import get_current_verified_user

router = APIRouter(prefix="/offers", tags=["offers"])


def calculate_time_until_expiry(expiry_date: datetime) -> str:
    """Calculate time until expiry in human readable format"""
    now = datetime.now(timezone.utc)
    if expiry_date <= now:
        return "Expired"
    
    diff = expiry_date - now
    days = diff.days
    hours = diff.seconds // 3600
    minutes = (diff.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


@router.get("/", response_model=List[OfferResponse])
async def get_offers(
    category: Optional[OfferCategory] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get available offers for swiping"""
    # Get offers that user hasn't liked yet and are still active
    query = db.query(Offer).filter(
        and_(
            Offer.is_active == True,
            Offer.expiry_date > datetime.now(timezone.utc),
            not_(
                Offer.id.in_(
                    db.query(UserLike.offer_id).filter(UserLike.user_id == current_user.id)
                )
            )
        )
    )
    
    if category:
        query = query.filter(Offer.category == category)
    
    offers = query.order_by(Offer.created_at.desc()).all()
    
    # Add time until expiry to each offer
    for offer in offers:
        offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    
    return offers


@router.get("/next", response_model=OfferResponse)
async def get_next_offer(
    category: Optional[OfferCategory] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get the next offer for swiping"""
    query = db.query(Offer).filter(
        and_(
            Offer.is_active == True,
            Offer.expiry_date > datetime.now(timezone.utc),
            not_(
                Offer.id.in_(
                    db.query(UserLike.offer_id).filter(UserLike.user_id == current_user.id)
                )
            )
        )
    )
    
    if category:
        query = query.filter(Offer.category == category)
    
    offer = query.order_by(Offer.created_at.desc()).first()
    
    if not offer:
        raise HTTPException(
            status_code=404,
            detail="No more offers available"
        )
    
    offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    return offer


@router.post("/swipe", response_model=MessageResponse)
async def swipe_offer(
    swipe_data: SwipeRequest,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Swipe on an offer (like or dislike)"""
    # Check if offer exists and is active
    offer = db.query(Offer).filter(
        and_(
            Offer.id == swipe_data.offer_id,
            Offer.is_active == True,
            Offer.expiry_date > datetime.now(timezone.utc)
        )
    ).first()
    
    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Offer not found or expired"
        )
    
    # Check if user already liked this offer
    existing_like = db.query(UserLike).filter(
        and_(
            UserLike.user_id == current_user.id,
            UserLike.offer_id == swipe_data.offer_id
        )
    ).first()
    
    if existing_like:
        raise HTTPException(
            status_code=400,
            detail="You have already swiped on this offer"
        )
    
    if swipe_data.action.lower() in ["like", "dislike"]:
        # Create swipe record
        user_like = UserLike(
            user_id=current_user.id,
            offer_id=swipe_data.offer_id,
            action=swipe_data.action.lower()
        )
        db.add(user_like)
        db.commit()
        
        if swipe_data.action.lower() == "like":
            return {"message": "Offer liked successfully"}
        else:
            return {"message": "Offer disliked"}
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid action. Use 'like' or 'dislike'"
        )


@router.get("/liked", response_model=List[OfferResponse])
async def get_liked_offers(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get user's liked offers"""
    liked_offers = db.query(Offer).join(UserLike).filter(
        and_(
            UserLike.user_id == current_user.id,
            UserLike.action == "like",
            Offer.is_active == True
        )
    ).order_by(UserLike.created_at.desc()).all()
    
    # Add time until expiry to each offer
    for offer in liked_offers:
        offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    
    return liked_offers


@router.get("/liked/{offer_id}", response_model=OfferResponse)
async def get_liked_offer_details(
    offer_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific liked offer"""
    offer = db.query(Offer).join(UserLike).filter(
        and_(
            UserLike.user_id == current_user.id,
            Offer.id == offer_id,
            Offer.is_active == True
        )
    ).first()
    
    if not offer:
        raise HTTPException(
            status_code=404,
            detail="Liked offer not found"
        )
    
    offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    return offer


@router.delete("/liked/{offer_id}", response_model=MessageResponse)
async def unlike_offer(
    offer_id: int,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Unlike an offer"""
    user_like = db.query(UserLike).filter(
        and_(
            UserLike.user_id == current_user.id,
            UserLike.offer_id == offer_id
        )
    ).first()
    
    if not user_like:
        raise HTTPException(
            status_code=404,
            detail="Liked offer not found"
        )
    
    db.delete(user_like)
    db.commit()
    
    return {"message": "Offer unliked successfully"}
