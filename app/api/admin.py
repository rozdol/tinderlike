from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
import json
from datetime import datetime, timezone

from app.database import get_db
from app.models import User, Offer, UserLike, AdminAction
from app.schemas import (
    AdminUserResponse, AdminUserUpdate, OfferResponse, OfferCreate, 
    OfferUpdate, AdminActionResponse, AdminStats, MessageResponse
)
from app.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

# Helper function to log admin actions
def log_admin_action(
    db: Session, 
    admin_user: User, 
    action_type: str, 
    resource_type: str, 
    resource_id: int, 
    details: dict = None
):
    admin_action = AdminAction(
        admin_user_id=admin_user.id,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        details=json.dumps(details) if details else None
    )
    db.add(admin_action)
    db.commit()

# User Management
@router.get("/users", response_model=List[AdminUserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_admin: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with filtering and pagination"""
    query = db.query(User)
    
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            User.phone.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    
    if is_verified is not None:
        query = query.filter(User.is_verified == is_verified)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    # Log admin action
    log_admin_action(
        db, current_admin, "update", "user", user_id, 
        {"updated_fields": list(update_data.keys())}
    )
    
    return user

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_admin:
        raise HTTPException(status_code=400, detail="Cannot delete admin users")
    
    # Log admin action before deletion
    log_admin_action(
        db, current_admin, "delete", "user", user_id,
        {"user_email": user.email, "user_full_name": user.full_name}
    )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

# Offer Management
@router.get("/offers", response_model=List[OfferResponse])
async def get_offers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all offers with filtering and pagination"""
    query = db.query(Offer)
    
    if search:
        search_filter = or_(
            Offer.title.ilike(f"%{search}%"),
            Offer.description.ilike(f"%{search}%"),
            Offer.provider_name.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    if category:
        query = query.filter(Offer.category == category)
    
    if is_active is not None:
        query = query.filter(Offer.is_active == is_active)
    
    offers = query.offset(skip).limit(limit).all()
    
    # Add time until expiry
    for offer in offers:
        offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    
    return offers

@router.get("/offers/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific offer by ID"""
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    return offer

@router.post("/offers", response_model=OfferResponse)
async def create_offer(
    offer_create: OfferCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new offer"""
    offer = Offer(**offer_create.dict())
    db.add(offer)
    db.commit()
    db.refresh(offer)
    
    # Log admin action
    log_admin_action(
        db, current_admin, "create", "offer", offer.id,
        {"title": offer.title, "provider": offer.provider_name}
    )
    
    offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    return offer

@router.put("/offers/{offer_id}", response_model=OfferResponse)
async def update_offer(
    offer_id: int,
    offer_update: OfferUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update an offer"""
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Update fields
    update_data = offer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(offer, field, value)
    
    offer.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(offer)
    
    # Log admin action
    log_admin_action(
        db, current_admin, "update", "offer", offer_id,
        {"updated_fields": list(update_data.keys())}
    )
    
    offer.time_until_expiry = calculate_time_until_expiry(offer.expiry_date)
    return offer

@router.delete("/offers/{offer_id}", response_model=MessageResponse)
async def delete_offer(
    offer_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete an offer"""
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Log admin action before deletion
    log_admin_action(
        db, current_admin, "delete", "offer", offer_id,
        {"title": offer.title, "provider": offer.provider_name}
    )
    
    db.delete(offer)
    db.commit()
    
    return {"message": "Offer deleted successfully"}

# Admin Actions Log
@router.get("/actions", response_model=List[AdminActionResponse])
async def get_admin_actions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    action_type: Optional[str] = None,
    resource_type: Optional[str] = None,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin actions log"""
    query = db.query(AdminAction).join(User, AdminAction.admin_user_id == User.id)
    
    if action_type:
        query = query.filter(AdminAction.action_type == action_type)
    
    if resource_type:
        query = query.filter(AdminAction.resource_type == resource_type)
    
    actions = query.order_by(AdminAction.created_at.desc()).offset(skip).limit(limit).all()
    return actions

# Statistics
@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    total_users = db.query(func.count(User.id)).scalar()
    total_offers = db.query(func.count(Offer.id)).scalar()
    total_likes = db.query(func.count(UserLike.id)).filter(UserLike.action == "like").scalar()
    total_dislikes = db.query(func.count(UserLike.id)).filter(UserLike.action == "dislike").scalar()
    active_offers = db.query(func.count(Offer.id)).filter(
        and_(Offer.is_active == True, Offer.expiry_date > datetime.now(timezone.utc))
    ).scalar()
    verified_users = db.query(func.count(User.id)).filter(User.is_verified == True).scalar()
    admin_users = db.query(func.count(User.id)).filter(User.is_admin == True).scalar()
    
    return AdminStats(
        total_users=total_users,
        total_offers=total_offers,
        total_likes=total_likes,
        total_dislikes=total_dislikes,
        active_offers=active_offers,
        verified_users=verified_users,
        admin_users=admin_users
    )

# Helper function for time calculation
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
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"
