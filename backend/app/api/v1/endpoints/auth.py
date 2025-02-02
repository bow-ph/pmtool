from datetime import timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.auth import (
    get_password_hash,
    create_access_token,
    get_current_active_user,
    verify_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, User as UserSchema

router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """OAuth2 compatible token login, supports both form data and JSON"""
    try:
        username = None
        password = None
        
        # Try to get credentials from JSON body first
        try:
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
            print(f"Received JSON request with username: {username}")
        except:
            # Fallback to form data
            username = form_data.username
            password = form_data.password
            print(f"Using form data with username: {username}")
            
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing username or password"
            )
            
        print(f"Processing login attempt for user: {username}")
        
        user = db.query(User).filter(User.email == username).first()
        if not user:
            print(f"User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not verify_password(password, user.hashed_password):
            print(f"Invalid password for user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user.is_active:
            print(f"Inactive user: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Register new user"""
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        subscription_type=user_in.subscription_type.value if user_in.subscription_type else "trial",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send welcome email
    from app.services.email_service import EmailService
    email_service = EmailService()
    email_service.send_welcome_email(db_user.email, db_user.email)
    
    return db_user



@router.post("/test-token", response_model=UserSchema)
def test_token(current_user: User = Depends(get_current_active_user)) -> Any:
    """Test access token"""
    return current_user

@router.post("/reset-password/{email}")
def reset_password(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """Send password reset email"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system",
        )
    from app.services.email_service import EmailService
    email_service = EmailService()
    
    # Generate reset token
    reset_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(hours=24)
    )
    
    # Send reset email
    if email_service.send_password_reset_email(user.email, reset_token):
        return {"msg": "Password reset email sent"}
    raise HTTPException(status_code=500, detail="Failed to send reset email")
