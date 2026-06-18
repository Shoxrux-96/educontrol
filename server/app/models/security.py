import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class UsbAction(str, enum.Enum):
    mounted = "mounted"
    unmounted = "unmounted"
    blocked = "blocked"


class ThreatType(str, enum.Enum):
    virus = "virus"
    trojan = "trojan"
    miner = "miner"
    ransomware = "ransomware"
    spyware = "spyware"
    worm = "worm"
    adware = "adware"
    unknown = "unknown"


class ThreatSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class LoginResult(str, enum.Enum):
    success = "success"
    failed = "failed"
    locked = "locked"
    timeout = "timeout"


class AntivirusProduct(str, enum.Enum):
    windows_defender = "Windows Defender"
    kaspersky = "Kaspersky"
    eset = "ESET NOD32"
    dr_web = "Dr.Web"
    mcafee = "McAfee"


class AntivirusStatusType(str, enum.Enum):
    healthy = "healthy"
    infected = "infected"
    at_risk = "at_risk"
    unknown = "unknown"


class PolicyCategory(str, enum.Enum):
    password = "password"
    antivirus = "antivirus"
    firewall = "firewall"
    usb = "usb"
    login = "login"
    general = "general"


class UsbEvent(Base):
    __tablename__ = "usb_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    computer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String(10), nullable=False)
    device_name: Mapped[str] = mapped_column(String(255), nullable=True)
    device_label: Mapped[str] = mapped_column(String(255), nullable=True)
    vendor_id: Mapped[str] = mapped_column(String(10), nullable=True)
    product_id: Mapped[str] = mapped_column(String(10), nullable=True)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=True)
    vendor_name: Mapped[str] = mapped_column(String(255), nullable=True)
    capacity_mb: Mapped[int] = mapped_column(Integer, nullable=True)
    filesystem: Mapped[str] = mapped_column(String(20), nullable=True)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked_by_policy: Mapped[str] = mapped_column(String(100), nullable=True)
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    computer = relationship("Computer")
    organization = relationship("Organization")

    def __repr__(self):
        return f"<UsbEvent {self.action} {self.device_name}>"


class AntivirusStatus(Base):
    __tablename__ = "antivirus_statuses"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    computer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=False, unique=True
    )
    product_name: Mapped[str] = mapped_column(String(100), nullable=True)
    product_version: Mapped[str] = mapped_column(String(50), nullable=True)
    definitions_version: Mapped[str] = mapped_column(String(50), nullable=True)
    definitions_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    definitions_up_to_date: Mapped[bool] = mapped_column(Boolean, default=True)
    realtime_protection: Mapped[bool] = mapped_column(Boolean, default=True)
    firewall_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    last_scan_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_scan_result: Mapped[str] = mapped_column(String(50), nullable=True)
    threats_found: Mapped[int] = mapped_column(Integer, default=0)
    threats_cleaned: Mapped[int] = mapped_column(Integer, default=0)
    is_installed: Mapped[bool] = mapped_column(Boolean, default=True)
    is_running: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_restart: Mapped[bool] = mapped_column(Boolean, default=False)
    status_updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    computer = relationship("Computer")
    organization = relationship("Organization")

    def __repr__(self):
        return f"<AntivirusStatus {self.product_name}>"


class ThreatDetection(Base):
    __tablename__ = "threat_detections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    computer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=False
    )
    threat_type: Mapped[str] = mapped_column(String(15), nullable=False)
    severity: Mapped[str] = mapped_column(String(10), default="medium")
    threat_name: Mapped[str] = mapped_column(String(500), nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=True)
    md5_hash: Mapped[str] = mapped_column(String(32), nullable=True)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=True)
    action_taken: Mapped[str] = mapped_column(String(50), nullable=True)
    is_quarantined: Mapped[bool] = mapped_column(Boolean, default=False)
    is_cleaned: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_by: Mapped[str] = mapped_column(String(100), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    computer = relationship("Computer")
    organization = relationship("Organization")
    resolver = relationship("User")

    def __repr__(self):
        return f"<ThreatDetection {self.threat_name} [{self.severity}]>"


class LoginAudit(Base):
    __tablename__ = "login_audits"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    computer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("computers.id"), nullable=True
    )
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True)
    hostname: Mapped[str] = mapped_column(String(255), nullable=True)
    result: Mapped[str] = mapped_column(String(10), nullable=False)
    failure_reason: Mapped[str] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[str] = mapped_column(String(500), nullable=True)
    session_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
    computer = relationship("Computer")
    organization = relationship("Organization")

    def __repr__(self):
        return f"<LoginAudit {self.username} {self.result}>"


class SecurityPolicy(Base):
    __tablename__ = "security_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, unique=True
    )
    usb_block_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    usb_whitelist: Mapped[dict] = mapped_column(JSON, default=dict)
    usb_block_external: Mapped[bool] = mapped_column(Boolean, default=True)
    av_required: Mapped[bool] = mapped_column(Boolean, default=True)
    av_realtime_required: Mapped[bool] = mapped_column(Boolean, default=True)
    av_definitions_max_age_hours: Mapped[int] = mapped_column(Integer, default=48)
    auto_threat_quarantine: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_threat: Mapped[bool] = mapped_column(Boolean, default=True)
    notify_on_usb: Mapped[bool] = mapped_column(Boolean, default=False)
    failed_login_threshold: Mapped[int] = mapped_column(Integer, default=5)
    login_notify_on_failure: Mapped[bool] = mapped_column(Boolean, default=True)
    password_complexity_required: Mapped[bool] = mapped_column(Boolean, default=True)
    session_timeout_minutes: Mapped[int] = mapped_column(Integer, default=60)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")

    def __repr__(self):
        return f"<SecurityPolicy {self.id}>"
