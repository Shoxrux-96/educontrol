import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base
import enum
from app.models.policy import PolicyTargetType


class MessageType(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), default=MessageType.info
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    target_type: Mapped[PolicyTargetType] = mapped_column(
        Enum(PolicyTargetType), nullable=False
    )
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
