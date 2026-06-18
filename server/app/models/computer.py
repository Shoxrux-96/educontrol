import uuid
from datetime import datetime, timezone
from sqlalchemy import String, SmallInteger, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class ComputerStatus(str, enum.Enum):
    online = "online"
    offline = "offline"
    busy = "busy"
    locked = "locked"
    maintenance = "maintenance"


class ComputerGroup(Base):
    __tablename__ = "computer_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(String(7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization", back_populates="computer_groups")
    computers = relationship("Computer", back_populates="group")


class Computer(Base):
    __tablename__ = "computers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    mac_address: Mapped[str] = mapped_column(String(17), nullable=True)
    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computer_groups.id"), nullable=True
    )
    os_version: Mapped[str] = mapped_column(String(100), nullable=True)
    agent_version: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[ComputerStatus] = mapped_column(
        Enum(ComputerStatus), default=ComputerStatus.offline
    )
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    cpu_model: Mapped[str] = mapped_column(String(200), nullable=True)
    ram_gb: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    disk_gb: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    current_user: Mapped[str] = mapped_column(String(100), nullable=True)
    cpu_usage: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    ram_usage: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    disk_usage: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    group = relationship("ComputerGroup", back_populates="computers")
    organization = relationship("Organization", back_populates="computers")
