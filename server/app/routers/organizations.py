from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.schemas.user import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationDetailResponse,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.utils.security import get_current_user, require_role
from app.models.user import User
from app.models.organization import Organization
from app.models.computer import Computer
from app.models.policy import Policy

router = APIRouter(prefix="/api/v1/organizations", tags=["Organizations"])


@router.get("", response_model=list[OrganizationDetailResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    result = await db.execute(select(Organization).order_by(Organization.name))
    orgs = result.scalars().all()
    response = []
    for org in orgs:
        user_count = await db.scalar(select(func.count(User.id)).where(User.organization_id == org.id))
        computer_count = await db.scalar(select(func.count(Computer.id)).where(Computer.organization_id == org.id))
        policy_count = await db.scalar(select(func.count(Policy.id)).where(Policy.organization_id == org.id))
        response.append(OrganizationDetailResponse(
            id=str(org.id),
            name=org.name,
            slug=org.slug,
            contact_email=org.contact_email,
            contact_phone=org.contact_phone,
            address=org.address,
            is_active=org.is_active,
            max_computers=org.max_computers,
            created_at=org.created_at,
            user_count=user_count or 0,
            computer_count=computer_count or 0,
            policy_count=policy_count or 0,
        ))
    return response


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    existing = await db.execute(select(Organization).where(Organization.slug == org_data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Organization slug already exists")

    org = Organization(**org_data.model_dump())
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return OrganizationResponse.model_validate(org)


@router.get("/{org_id}", response_model=OrganizationDetailResponse)
async def get_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    user_count = await db.scalar(select(func.count(User.id)).where(User.organization_id == org.id))
    computer_count = await db.scalar(select(func.count(Computer.id)).where(Computer.organization_id == org.id))
    policy_count = await db.scalar(select(func.count(Policy.id)).where(Policy.organization_id == org.id))
    return OrganizationDetailResponse(
        id=str(org.id),
        name=org.name,
        slug=org.slug,
        contact_email=org.contact_email,
        contact_phone=org.contact_phone,
        address=org.address,
        is_active=org.is_active,
        max_computers=org.max_computers,
        created_at=org.created_at,
        user_count=user_count or 0,
        computer_count=computer_count or 0,
        policy_count=policy_count or 0,
    )


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    updates = org_data.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(org, key, value)
    await db.commit()
    await db.refresh(org)
    return OrganizationResponse.model_validate(org)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    await db.delete(org)
    await db.commit()


@router.get("/{org_id}/users", response_model=list[UserResponse])
async def list_organization_users(
    org_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    result = await db.execute(
        select(User).where(User.organization_id == org_id).order_by(User.username)
    )
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("/{org_id}/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_organization_user(
    org_id: str,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Organization not found")

    user_data.organization_id = org_id
    service = AuthService(db)
    try:
        return await service.register(user_data, str(current_user.id), organization_id=org_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
