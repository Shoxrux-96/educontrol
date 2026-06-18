from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.computer import (
    ComputerResponse,
    ComputerUpdate,
    ComputerStatsResponse,
    ComputerGroupCreate,
    ComputerGroupUpdate,
    ComputerGroupResponse,
)
from app.schemas.audit import AuditLogResponse
from app.schemas.command import CommandResponse
from app.services.computer_service import ComputerService
from app.services.audit_service import AuditService
from app.services.command_service import CommandService
from app.utils.security import get_current_user, require_role
from app.utils.pagination import PaginatedResponse
from app.models.user import User

router = APIRouter(prefix="/api/v1/computers", tags=["Computers"])


@router.get("", response_model=PaginatedResponse[ComputerResponse])
async def list_computers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=500),
    status: str = Query(None),
    group_id: str = Query(None),
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ComputerService(db)
    org_id = str(current_user.organization_id) if current_user.role.value != "owner" and current_user.organization_id else None
    return await service.list_computers(page, page_size, status, group_id, search, organization_id=org_id)


@router.post("/groups", response_model=ComputerGroupResponse, status_code=201)
async def create_group(
    data: ComputerGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    service = ComputerService(db)
    return await service.create_group(data, organization_id=current_user.organization_id)


@router.get("/groups", response_model=list[ComputerGroupResponse])
async def list_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ComputerService(db)
    return await service.list_groups()


@router.patch("/groups/{group_id}", response_model=ComputerGroupResponse)
async def update_group(
    group_id: str,
    data: ComputerGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    service = ComputerService(db)
    try:
        return await service.update_group(group_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/groups/{group_id}", status_code=204)
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    service = ComputerService(db)
    try:
        await service.delete_group(group_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{computer_id}", response_model=ComputerResponse)
async def get_computer(
    computer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ComputerService(db)
    try:
        return await service.get_computer(computer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{computer_id}", response_model=ComputerResponse)
async def update_computer(
    computer_id: str,
    data: ComputerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = ComputerService(db)
    try:
        return await service.update_computer(computer_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{computer_id}", status_code=204)
async def delete_computer(
    computer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("super_admin")),
):
    service = ComputerService(db)
    try:
        await service.delete_computer(computer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{computer_id}/stats", response_model=ComputerStatsResponse)
async def get_computer_stats(
    computer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ComputerService(db)
    try:
        return await service.get_computer_stats(computer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{computer_id}/audit", response_model=PaginatedResponse[AuditLogResponse])
async def get_computer_audit(
    computer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuditService(db)
    return await service.list_logs(page=page, page_size=page_size, computer_id=computer_id)


@router.get("/{computer_id}/commands", response_model=list[CommandResponse])
async def get_computer_commands(
    computer_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommandService(db)
    return await service.get_computer_commands(computer_id, limit)
