import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text, BigInteger, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class RemoteSessionStatus(str, enum.Enum):
    active = "active"
    closed = "closed"
    timeout = "timeout"


class DeploymentStatus(str, enum.Enum):
    pending = "pending"
    deploying = "deploying"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class RemoteSession(Base):
    __tablename__ = "remote_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    computer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=RemoteSessionStatus.active.value
    )
    protocol: Mapped[str] = mapped_column(String(20), default="vnc")
    screen_width: Mapped[int] = mapped_column(Integer, nullable=True)
    screen_height: Mapped[int] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    computer = relationship("Computer")
    user = relationship("User")


class SoftwareInventoryItem(Base):
    __tablename__ = "software_inventory"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    computer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[str] = mapped_column(String(100), nullable=True)
    publisher: Mapped[str] = mapped_column(String(255), nullable=True)
    install_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    install_location: Mapped[str] = mapped_column(String(500), nullable=True)
    uninstall_string: Mapped[str] = mapped_column(Text, nullable=True)
    size_mb: Mapped[float] = mapped_column(Float, nullable=True)
    is_system_component: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    computer = relationship("Computer")

    def __repr__(self):
        return f"<Software {self.name} v{self.version}>"


class SoftwarePackage(Base):
    __tablename__ = "software_packages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    package_type: Mapped[str] = mapped_column(String(50), nullable=False)
    installer_path: Mapped[str] = mapped_column(String(500), nullable=True)
    installer_url: Mapped[str] = mapped_column(String(1000), nullable=True)
    installer_args: Mapped[str] = mapped_column(String(500), nullable=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=True)
    size_mb: Mapped[float] = mapped_column(Float, nullable=True)
    icon: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<SoftwarePackage {self.name}>"


class SoftwareDeployment(Base):
    __tablename__ = "software_deployments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    package_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("software_packages.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target_ids: Mapped[dict] = mapped_column(JSONB, default=list)
    status: Mapped[str] = mapped_column(
        String(20), default=DeploymentStatus.pending.value
    )
    total_computers: Mapped[int] = mapped_column(Integer, default=0)
    completed_computers: Mapped[int] = mapped_column(Integer, default=0)
    failed_computers: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    package = relationship("SoftwarePackage")
    creator = relationship("User")
