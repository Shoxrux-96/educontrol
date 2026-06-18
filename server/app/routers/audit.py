from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.audit import AuditLogResponse
from app.services.audit_service import AuditService
from app.utils.security import get_current_user
from app.utils.pagination import PaginatedResponse
from app.models.user import User

router = APIRouter(prefix="/api/v1/audit", tags=["Audit Logs"])


@router.get("", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    event_type: str = Query(None),
    severity: str = Query(None),
    computer_id: str = Query(None),
    user_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuditService(db)
    return await service.list_logs(
        page=page,
        page_size=page_size,
        event_type=event_type,
        severity=severity,
        computer_id=computer_id,
        user_id=user_id,
    )
