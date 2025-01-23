from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.orm import joinedload
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema
from app.core.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    client_type: Optional[str] = None,
    subscription_type: Optional[str] = None,
    is_active: Optional[bool] = None,
):
    """
    Get all users with their details.
    Only accessible by superusers.
    
    Parameters:
    - sort_by: Field to sort by (created_at, email, client_type, subscription_type)
    - sort_order: asc or desc
    - client_type: Filter by client type (private or company)
    - subscription_type: Filter by subscription type (trial, team, enterprise)
    - is_active: Filter by active status
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint"
        )
    
    # Start query
    query = db.query(User)
    
    # Apply filters
    if client_type:
        query = query.filter(User.client_type == client_type)
    if subscription_type:
        query = query.filter(User.subscription_type == subscription_type)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Apply sorting
    sort_field = getattr(User, sort_by, User.created_at)
    if sort_order == "desc":
        sort_field = sort_field.desc()
    query = query.order_by(sort_field)
    
    users = query.all()
    return users

@router.get("/users/{user_id}", response_model=UserSchema)
async def get_user_details(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific user including subscription history.
    Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint"
        )
    
    # Get user with related data
    user = db.query(User)\
        .options(
            joinedload(User.invoices),
            joinedload(User.projects)
        )\
        .filter(User.id == user_id)\
        .first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a user's active status.
    Only accessible by superusers.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can access this endpoint"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    db.commit()
    return {"status": "success", "message": "User status updated"}
