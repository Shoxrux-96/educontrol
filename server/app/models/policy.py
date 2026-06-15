import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class PolicyType(str, enum.Enum):
    internet = "internet"
    application = "application"
    usb = "usb"
    print_screen = "print_screen"


class PolicyTargetType(str, enum.Enum):
    computer = "computer"
    group = "group"
    all = "all"


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    policy_type: Mapped[PolicyType] = mapped_column(Enum(PolicyType), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    creator = relationship("User")
    assignments = relationship("PolicyAssignment", back_populates="policy")


class PolicyAssignment(Base):
    __tablename__ = "policy_assignments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("policies.id"), nullable=False
    )
    target_type: Mapped[PolicyTargetType] = mapped_column(
        Enum(PolicyTargetType), nullable=False
    )
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    assigned_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    policy = relationship("Policy", back_populates="assignments")
    assigner = relationship("User")
