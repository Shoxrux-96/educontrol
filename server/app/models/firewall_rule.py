import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class FirewallAction(str, enum.Enum):
    allow = "allow"
    block = "block"
    log = "log"


class FirewallDirection(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"
    both = "both"


class FirewallProtocol(str, enum.Enum):
    tcp = "TCP"
    udp = "UDP"
    icmp = "ICMP"
    any = "ANY"


class FirewallMatchType(str, enum.Enum):
    port = "port"
    ip = "ip"
    mac = "mac"
    port_range = "port_range"
    subnet = "subnet"


class FirewallRule(Base):
    __tablename__ = "firewall_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    action: Mapped[FirewallAction] = mapped_column(
        Enum(FirewallAction), nullable=False
    )
    direction: Mapped[FirewallDirection] = mapped_column(
        Enum(FirewallDirection), default=FirewallDirection.both
    )
    protocol: Mapped[FirewallProtocol] = mapped_column(
        Enum(FirewallProtocol), default=FirewallProtocol.any
    )
    match_type: Mapped[FirewallMatchType] = mapped_column(
        Enum(FirewallMatchType), nullable=False
    )
    match_value: Mapped[str] = mapped_column(String(500), nullable=False)
    source_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    destination_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    source_port: Mapped[int] = mapped_column(Integer, nullable=True)
    destination_port: Mapped[int] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
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
