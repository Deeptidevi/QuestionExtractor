from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User's unique email address")
    password: str = Field(..., min_length=6, description="User password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="Full name of the user")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration duration in seconds")


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
