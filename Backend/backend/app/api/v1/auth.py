from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.postgres import get_db
from backend.app.auth.schemas import Token, LoginRequest
from backend.app.auth.models import User
from backend.app.auth.security import verify_password, create_access_token
from backend.app.audit.service import AuditService
from backend.app.audit.models import ActionCategory

from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

# A safe dummy hash to mitigate email enumeration timing attacks.
# This ensures verify_password is run and takes roughly the same amount of CPU time
# regardless of whether the email exists in the database.
DUMMY_HASH = "$2b$12$EO0kz/HnmLlIpqi/0yFTNumxKopnB4Y3JONTY7QC52f9988K0dKjy"

def _process_login(db: Session, email: str, password: str) -> str:
    """Core login logic shared by both JSON and Form endpoints."""
    user = db.scalar(select(User).where(User.email == email))
    
    # Generic exception to prevent email enumeration
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not user:
        # Run dummy verification to prevent timing attack
        verify_password(password, DUMMY_HASH)
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.ADMIN,
            action_detail="Failed login attempt",
            action_metadata={"email": email}
        )
        db.commit()
        raise auth_exception
        
    if not verify_password(password, user.hashed_password):
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.ADMIN,
            action_detail="Failed login attempt",
            user_id=user.id,
            action_metadata={"email": email}
        )
        db.commit()
        raise auth_exception
        
    if not user.is_active:
        AuditService.log_action(
            db=db,
            action_category=ActionCategory.ADMIN,
            action_detail="Failed login attempt (inactive user)",
            user_id=user.id,
            action_metadata={"email": email}
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    AuditService.log_action(
        db=db,
        action_category=ActionCategory.ADMIN,
        action_detail="User login successful",
        user_id=user.id
    )
    db.commit()
    return access_token

@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user via JSON and return a JWT access token.
    """
    access_token = _process_login(db, request.email, request.password)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate a user via Form Data and return a JWT access token.
    Provides native Swagger UI authorization support.
    """
    access_token = _process_login(db, form_data.username, form_data.password)
    
    return {"access_token": access_token, "token_type": "bearer"}


from pydantic import BaseModel
from backend.app.auth.dependencies import get_current_user

class UserProfileResponse(BaseModel):
    id: str
    email: str
    roles: list[str]

@router.get("/me", response_model=UserProfileResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current user profile including roles.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "roles": [r.name for r in current_user.roles]
    }
