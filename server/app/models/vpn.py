import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base


class VpnProfile(Base):
    __tablename__ = "vpn_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    vpn_type: Mapped[str] = mapped_column(String(20), default="wireguard")
    server_address: Mapped[str] = mapped_column(String(500), nullable=False)
    server_port: Mapped[int] = mapped_column(Integer, nullable=False)
    allowed_ips: Mapped[str] = mapped_column(Text, nullable=True)
    dns_servers: Mapped[str] = mapped_column(String(500), nullable=True)
    public_key: Mapped[str] = mapped_column(Text, nullable=True)
    private_key: Mapped[str] = mapped_column(Text, nullable=True)
    preshared_key: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")
    creator = relationship("User")


class VpnClient(Base):
    __tablename__ = "vpn_clients"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vpn_profiles.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    client_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    public_key: Mapped[str] = mapped_column(Text, nullable=True)
    private_key: Mapped[str] = mapped_column(Text, nullable=True)
    allowed_ips: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    disconnected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    profile = relationship("VpnProfile")
    user = relationship("User")
