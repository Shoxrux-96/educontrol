from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.utils.types import UUIDStr


class OrganizationCreate(BaseModel):
    name: str = Field(..., max_length=200)
    slug: str = Field(..., max_length=100, pattern=r"^[a-z0-9-]+$")
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    max_computers: int = 100


class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None
    max_computers: Optional[int] = None
    settings: Optional[dict] = None


class OrganizationResponse(BaseModel):
    id: UUIDStr
    name: str
    slug: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    is_active: bool
    max_computers: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OrganizationDetailResponse(OrganizationResponse):
    user_count: int = 0
    computer_count: int = 0
    policy_count: int = 0


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: str = "viewer"
    organization_id: Optional[UUIDStr] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    organization_id: Optional[UUIDStr] = None


class UserResponse(BaseModel):
    id: UUIDStr
    organization_id: Optional[UUIDStr] = None
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
