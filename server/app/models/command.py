import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base
import enum


class CommandStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    delivered = "delivered"
    executed = "executed"
    failed = "failed"


class Command(Base):
    __tablename__ = "commands"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    computer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=False
    )
    command_type: Mapped[str] = mapped_column(String(50), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=True)
    status: Mapped[CommandStatus] = mapped_column(
        Enum(CommandStatus), default=CommandStatus.pending
    )
    sent_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    result: Mapped[dict] = mapped_column(JSONB, nullable=True)
