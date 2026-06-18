import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    max_computers: Mapped[int] = mapped_column(Integer, default=100)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    users = relationship("User", back_populates="organization", lazy="selectin")
    computers = relationship("Computer", back_populates="organization", lazy="selectin")
    computer_groups = relationship("ComputerGroup", back_populates="organization", lazy="selectin")
    policies = relationship("Policy", back_populates="organization", lazy="selectin")
    commands = relationship("Command", back_populates="organization", lazy="selectin")
    messages = relationship("Message", back_populates="organization", lazy="selectin")
    audit_logs = relationship("AuditLog", back_populates="organization", lazy="selectin")
    alert_rules = relationship("AlertRule", back_populates="organization", lazy="selectin")
    agent_builds = relationship("AgentBuild", back_populates="organization", lazy="selectin")
