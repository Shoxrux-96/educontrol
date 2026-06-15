from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.audit_log import AuditLog, EventSeverity
from app.schemas.audit import AuditLogResponse
from app.utils.pagination import PaginatedResponse, paginate


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_event(
        self,
        event_type: str,
        description: str,
        severity: str = "info",
        computer_id: Optional[str] = None,
        user_id: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ):
        log = AuditLog(
            event_type=event_type,
            severity=EventSeverity(severity),
            computer_id=computer_id,
            user_id=user_id,
            description=description,
            details=extra_data,
        )
        self.db.add(log)
        await self.db.commit()

    async def list_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        computer_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> PaginatedResponse[AuditLogResponse]:
        query = select(AuditLog)
        if event_type:
            query = query.where(AuditLog.event_type == event_type)
        if severity:
            query = query.where(AuditLog.severity == EventSeverity(severity))
        if computer_id:
            query = query.where(AuditLog.computer_id == computer_id)
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        query = query.order_by(AuditLog.created_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        logs = result.scalars().all()

        items = [AuditLogResponse.model_validate(l) for l in logs]
        return paginate(items, total, page, page_size)
