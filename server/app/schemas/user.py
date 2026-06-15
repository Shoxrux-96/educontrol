from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.utils.types import UUIDStr


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = "viewer"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    id: UUIDStr
    username: str
    email: str
    role: str
    full_name: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    user: UserResponse


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    expires_in: int
