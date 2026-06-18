import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Integer, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class NetworkDeviceType(str, enum.Enum):
    router = "router"
    switch = "switch"
    access_point = "access_point"
    printer = "printer"
    camera = "camera"
    computer = "computer"
    server = "server"
    firewall_device = "firewall_device"
    modem = "modem"
    other = "other"


class ConnectionType(str, enum.Enum):
    wired = "wired"
    wireless = "wireless"


class NetworkDevice(Base):
    __tablename__ = "network_devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    mac_address: Mapped[str] = mapped_column(String(17), nullable=False)
    device_type: Mapped[NetworkDeviceType] = mapped_column(
        Enum(NetworkDeviceType), nullable=False
    )
    vendor: Mapped[str] = mapped_column(String(200), nullable=True)
    model: Mapped[str] = mapped_column(String(200), nullable=True)
    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("network_devices.id"), nullable=True
    )
    connection_type: Mapped[ConnectionType] = mapped_column(
        Enum(ConnectionType), default=ConnectionType.wired
    )
    port_count: Mapped[int] = mapped_column(Integer, nullable=True)
    uptime_seconds: Mapped[int] = mapped_column(BigInteger, nullable=True)
    firmware_version: Mapped[str] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(String(1000), nullable=True)
    is_monitored: Mapped[bool] = mapped_column(Boolean, default=True)
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")
    children = relationship("NetworkDevice", backref="parent", remote_side=[id])


class IpLease(Base):
    __tablename__ = "ip_leases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    mac_address: Mapped[str] = mapped_column(String(17), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=True)
    vendor: Mapped[str] = mapped_column(String(200), nullable=True)
    is_dhcp: Mapped[bool] = mapped_column(Boolean, default=True)
    is_static: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    conflict_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    conflict_with: Mapped[str] = mapped_column(String(45), nullable=True)
    leased_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")


class PingResult(Base):
    __tablename__ = "ping_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("network_devices.id"), nullable=False
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    is_alive: Mapped[bool] = mapped_column(Boolean, default=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=True)
    packet_loss_pct: Mapped[float] = mapped_column(Float, nullable=True)
    jitter_ms: Mapped[float] = mapped_column(Float, nullable=True)
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=True)
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")
    device = relationship("NetworkDevice")


class BandwidthRecord(Base):
    __tablename__ = "bandwidth_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("network_devices.id"), nullable=False
    )
    interface_name: Mapped[str] = mapped_column(String(100), nullable=True)
    bytes_in: Mapped[int] = mapped_column(BigInteger, default=0)
    bytes_out: Mapped[int] = mapped_column(BigInteger, default=0)
    bytes_total: Mapped[int] = mapped_column(BigInteger, default=0)
    bits_in_per_sec: Mapped[float] = mapped_column(Float, default=0)
    bits_out_per_sec: Mapped[float] = mapped_column(Float, default=0)
    utilization_pct: Mapped[float] = mapped_column(Float, default=0)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")
    device = relationship("NetworkDevice")
