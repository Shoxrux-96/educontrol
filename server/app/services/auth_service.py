from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    LoginRequest,
    TokenResponse,
    UserResponse,
    TokenRefreshResponse,
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.config import settings


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreate, created_by: str = None) -> UserResponse:
        existing = await self.db.execute(
            select(User).where(
                (User.username == user_data.username) | (User.email == user_data.email)
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Username or email already exists")

        user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role=UserRole(user_data.role),
            full_name=user_data.full_name,
            created_by=created_by,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return UserResponse.model_validate(user)

    async def login(self, login_data: LoginRequest) -> TokenResponse:
        result = await self.db.execute(
            select(User).where(User.username == login_data.username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid username or password")

        if not user.is_active:
            raise ValueError("User account is disabled")

        user.last_login = datetime.now(timezone.utc)
        await self.db.commit()

        user_resp = UserResponse.model_validate(user)
        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token({"sub": str(user.id), "type": "refresh"})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=user_resp,
        )

    async def refresh_token(self, refresh_token: str) -> TokenRefreshResponse:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        return TokenRefreshResponse(
            access_token=access_token,
            expires_in=settings.access_token_expire_minutes * 60,
        )

    async def get_user_by_id(self, user_id: str) -> UserResponse:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")
        return UserResponse.model_validate(user)
