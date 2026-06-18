from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.policy import (
    PolicyCreate,
    PolicyUpdate,
    PolicyResponse,
    PolicyAssignRequest,
    PolicyAssignmentResponse,
)
from app.services.policy_service import PolicyService
from app.utils.security import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/api/v1/policies", tags=["Policies"])


@router.get("", response_model=list[PolicyResponse])
async def list_policies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PolicyService(db)
    return await service.list_policies()


@router.post("", response_model=PolicyResponse, status_code=201)
async def create_policy(
    data: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = PolicyService(db)
    return await service.create_policy(data, str(current_user.id))


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PolicyService(db)
    try:
        return await service.get_policy(policy_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    data: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = PolicyService(db)
    try:
        return await service.update_policy(policy_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{policy_id}", status_code=204)
async def delete_policy(
    policy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    service = PolicyService(db)
    try:
        await service.delete_policy(policy_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{policy_id}/assign", response_model=PolicyAssignmentResponse)
async def assign_policy(
    policy_id: str,
    data: PolicyAssignRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = PolicyService(db)
    try:
        return await service.assign_policy(policy_id, data, str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{policy_id}/assign/{assignment_id}", status_code=204)
async def unassign_policy(
    policy_id: str,
    assignment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = PolicyService(db)
    try:
        await service.unassign_policy(assignment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/computer/{computer_id}", response_model=list[PolicyResponse])
async def get_computer_policies(
    computer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = PolicyService(db)
    return await service.get_policies_for_computer(computer_id)
