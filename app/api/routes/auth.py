from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.dependencies import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.exceptions import ConflictException, AuthenticationException
from app.db.models.user import User
from app.db.repositories.user_repo import UserRepository
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user account with unique email.
    """
    repo = UserRepository(db)
    existing = repo.get_by_email(request.email)
    if existing:
        raise ConflictException(f"User with email '{request.email}' already exists.")

    hashed_pw = get_password_hash(request.password)
    user = repo.create_user(
        email=request.email,
        hashed_password=hashed_pw,
        full_name=request.full_name,
    )
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible token login, retrieving an access token for subsequent API calls.
    """
    repo = UserRepository(db)
    user = repo.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise AuthenticationException("Incorrect email or password.")
    if not user.is_active:
        raise AuthenticationException("User account is inactive.")

    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        expires_delta=token_expires,
        extra_claims={"email": user.email},
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(token_expires.total_seconds()),
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve current authenticated user's profile.
    """
    return current_user
