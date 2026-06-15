from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    TokenRefreshResponse,
)
from app.services.auth_service import AuthService
from app.utils.security import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    service = AuthService(db)
    try:
        return await service.register(user_data, str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        return await service.login(login_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh(refresh_data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    try:
        return await service.refresh_token(refresh_data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    return None


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
