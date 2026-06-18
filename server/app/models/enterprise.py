import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text, Integer, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class SyslogSeverity(str, enum.Enum):
    emergency = "emergency"
    alert = "alert"
    critical = "critical"
    error = "error"
    warning = "warning"
    notice = "notice"
    info = "info"
    debug = "debug"


class SnmpVersion(str, enum.Enum):
    v1 = "v1"
    v2c = "v2c"
    v3 = "v3"


class BackupStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class BackupType(str, enum.Enum):
    config = "config"
    full = "full"
    firmware = "firmware"


# ── Syslog ──

class SyslogEntry(Base):
    __tablename__ = "syslog_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    facility: Mapped[str] = mapped_column(String(50), nullable=True)
    severity: Mapped[SyslogSeverity] = mapped_column(
        Enum(SyslogSeverity), default=SyslogSeverity.info
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    app_name: Mapped[str] = mapped_column(String(100), nullable=True)
    process_id: Mapped[str] = mapped_column(String(20), nullable=True)
    message_id: Mapped[str] = mapped_column(String(50), nullable=True)
    structured_data: Mapped[dict] = mapped_column(JSONB, nullable=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=True)
    raw_log: Mapped[str] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")

    def __repr__(self):
        return f"<Syslog {self.severity} {self.hostname}>"


# ── SNMP ──

class SnmpDevice(Base):
    __tablename__ = "snmp_devices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    snmp_version: Mapped[SnmpVersion] = mapped_column(
        Enum(SnmpVersion), default=SnmpVersion.v2c
    )
    community: Mapped[str] = mapped_column(String(100), nullable=True)
    snmp_user: Mapped[str] = mapped_column(String(100), nullable=True)
    snmp_auth_protocol: Mapped[str] = mapped_column(String(20), nullable=True)
    snmp_auth_key: Mapped[str] = mapped_column(String(100), nullable=True)
    snmp_priv_protocol: Mapped[str] = mapped_column(String(20), nullable=True)
    snmp_priv_key: Mapped[str] = mapped_column(String(100), nullable=True)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    vendor: Mapped[str] = mapped_column(String(100), nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    os_version: Mapped[str] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=True)
    uptime_seconds: Mapped[int] = mapped_column(BigInteger, nullable=True)
    poll_interval_seconds: Mapped[int] = mapped_column(Integer, default=300)
    is_monitored: Mapped[bool] = mapped_column(Boolean, default=True)
    is_reachable: Mapped[bool] = mapped_column(Boolean, default=False)
    last_poll_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")

    def __repr__(self):
        return f"<SnmpDevice {self.hostname} ({self.device_type})>"


class SnmpMetric(Base):
    __tablename__ = "snmp_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("snmp_devices.id"), nullable=False
    )
    oid: Mapped[str] = mapped_column(String(255), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    value_float: Mapped[float] = mapped_column(Float, nullable=True)
    value_int: Mapped[int] = mapped_column(BigInteger, nullable=True)
    value_str: Mapped[str] = mapped_column(String(500), nullable=True)
    unit: Mapped[str] = mapped_column(String(50), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    device = relationship("SnmpDevice")
    organization = relationship("Organization")


# ── Backup ──

class BackupJob(Base):
    __tablename__ = "backup_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)
    device_id: Mapped[str] = mapped_column(String(255), nullable=False)
    device_hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    device_ip: Mapped[str] = mapped_column(String(45), nullable=True)
    backup_type: Mapped[BackupType] = mapped_column(
        Enum(BackupType), default=BackupType.config
    )
    schedule_cron: Mapped[str] = mapped_column(String(100), nullable=True)
    retention_count: Mapped[int] = mapped_column(Integer, default=30)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=True)
    protocol: Mapped[str] = mapped_column(String(20), default="scp")
    username: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[BackupStatus] = mapped_column(
        Enum(BackupStatus), nullable=True
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")

    def __repr__(self):
        return f"<BackupJob {self.name} ({self.device_hostname})>"


class BackupRecord(Base):
    __tablename__ = "backup_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("backup_jobs.id"), nullable=False
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=True)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=True)
    status: Mapped[BackupStatus] = mapped_column(
        Enum(BackupStatus), nullable=False
    )
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    job = relationship("BackupJob")
    organization = relationship("Organization")

    def __repr__(self):
        return f"<BackupRecord {self.file_name} ({self.status})>"
