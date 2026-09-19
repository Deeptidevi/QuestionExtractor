from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationException
from app.db.session import get_db
from app.db.models.user import User
from app.db.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """Validates JWT bearer token and injects authenticated user."""
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationException("Could not validate credentials or token expired.")

    user_id: Optional[str] = payload.get("sub")
    if not user_id:
        raise AuthenticationException("Token missing subject identifier.")

    user_repo = UserRepository(db)
    user = user_repo.get(user_id)
    if not user:
        raise AuthenticationException("User account does not exist.")
    if not user.is_active:
        raise AuthenticationException("User account is inactive.")

    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have sufficient administrative privileges.",
        )
    return current_user
