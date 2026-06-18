from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.vpn import VpnProfile, VpnClient
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/vpn", tags=["VPN"])


@router.get("/profiles")
async def list_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(VpnProfile)
    if current_user.organization_id:
        query = query.where(VpnProfile.organization_id == current_user.organization_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/profiles")
async def create_profile(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = VpnProfile(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(VpnProfile, k) and k not in ("id", "organization_id", "created_by")},
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.post("/profiles/{profile_id}/clients")
async def create_client(
    profile_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(VpnProfile).where(VpnProfile.id == profile_id))
    if not result.scalar_one_or_none():
        raise HTTPException(404, "Profile not found")
    client = VpnClient(
        profile_id=profile_id,
        user_id=current_user.id,
        **{k: v for k, v in data.items() if hasattr(VpnClient, k) and k not in ("id", "profile_id")},
    )
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/clients")
async def list_clients(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(VpnClient)
    if current_user.organization_id:
        query = query.where(VpnClient.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()
