from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.postgres import get_db
from backend.app.auth.models import User
from backend.app.auth.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Validates the supplied JWT token and retrieves the corresponding active user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Validate JWT
    try:
        payload = decode_access_token(token)
        if not payload:
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # 2. Fetch User
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        raise credentials_exception
        
    # 3. Active Check
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user


def require_role(allowed_roles: list[str]):
    """
    Returns a FastAPI dependency that verifies the current user has at least one of the allowed roles.
    Checks the roles directly from the database User object to prevent client JWT spoofing.
    """
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        user_roles = [role.name for role in current_user.roles]
        
        has_allowed_role = any(role in allowed_roles for role in user_roles)
        if not has_allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return current_user
        
    return role_dependency
