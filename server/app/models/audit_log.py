from datetime import datetime, timezone
from sqlalchemy import String, BigInteger, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base
import enum


class EventSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[EventSeverity] = mapped_column(
        Enum(EventSeverity), default=EventSeverity.info
    )
    computer_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=True
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = {
        "postgresql_partition_by": "RANGE (created_at)"
    }
