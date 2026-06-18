import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class DomainSyncStatus(str, enum.Enum):
    pending = "pending"
    syncing = "syncing"
    synced = "synced"
    error = "error"


class GpoTargetType(str, enum.Enum):
    computer = "computer"
    user = "user"
    group = "group"
    all = "all"


class DomainConfig(Base):
    __tablename__ = "domain_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, unique=True
    )
    domain_name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain_controller: Mapped[str] = mapped_column(String(255), nullable=False)
    ldap_base_dn: Mapped[str] = mapped_column(String(500), nullable=False)
    ldap_user: Mapped[str] = mapped_column(String(255), nullable=True)
    ldap_password: Mapped[str] = mapped_column(String(255), nullable=True)
    use_ssl: Mapped[bool] = mapped_column(Boolean, default=True)
    sync_interval_minutes: Mapped[int] = mapped_column(default=60)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[DomainSyncStatus] = mapped_column(
        Enum(DomainSyncStatus), default=DomainSyncStatus.pending
    )
    sso_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    auto_create_users: Mapped[bool] = mapped_column(Boolean, default=True)
    default_role: Mapped[str] = mapped_column(String(20), default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")

    def __repr__(self):
        return f"<DomainConfig {self.domain_name}>"


class AdUser(Base):
    __tablename__ = "ad_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    domain_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_configs.id"), nullable=False
    )
    sam_account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_principal_name: Mapped[str] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=True)
    given_name: Mapped[str] = mapped_column(String(100), nullable=True)
    surname: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    distinguished_name: Mapped[str] = mapped_column(String(500), nullable=False)
    ou_dn: Mapped[str] = mapped_column(String(500), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    locked_out: Mapped[bool] = mapped_column(Boolean, default=False)
    last_logon: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    linked_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    domain_config = relationship("DomainConfig")
    linked_user = relationship("User", foreign_keys=[linked_user_id])

    def __repr__(self):
        return f"<AdUser {self.sam_account_name}>"


class AdGroup(Base):
    __tablename__ = "ad_groups"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    domain_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_configs.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    sam_account_name: Mapped[str] = mapped_column(String(255), nullable=True)
    distinguished_name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    group_type: Mapped[str] = mapped_column(String(50), nullable=True)
    member_count: Mapped[int] = mapped_column(default=0)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    domain_config = relationship("DomainConfig")

    def __repr__(self):
        return f"<AdGroup {self.name}>"


class AdOU(Base):
    __tablename__ = "ad_ous"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    domain_config_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("domain_configs.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    distinguished_name: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_dn: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    user_count: Mapped[int] = mapped_column(default=0)
    computer_count: Mapped[int] = mapped_column(default=0)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    domain_config = relationship("DomainConfig")

    def __repr__(self):
        return f"<AdOU {self.name}>"


class AdGpo(Base):
    __tablename__ = "ad_gpos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    target_type: Mapped[str] = mapped_column(
        String(20), default=GpoTargetType.all.value
    )
    target_id: Mapped[str] = mapped_column(String(255), nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    usb_block: Mapped[bool] = mapped_column(Boolean, default=False)
    control_panel_block: Mapped[bool] = mapped_column(Boolean, default=False)
    cmd_block: Mapped[bool] = mapped_column(Boolean, default=False)
    registry_block: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    apply_to_computers: Mapped[bool] = mapped_column(Boolean, default=False)
    apply_to_users: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")
    creator = relationship("User")

    def __repr__(self):
        return f"<AdGpo {self.name}>"
