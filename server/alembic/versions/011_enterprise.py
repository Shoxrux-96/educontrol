"""enterprise: syslog, snmp, backup management

Revision ID: 011
Revises: 010
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "syslog_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("facility", sa.String(50), nullable=True),
        sa.Column("severity", sa.String(10), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("app_name", sa.String(100), nullable=True),
        sa.Column("process_id", sa.String(20), nullable=True),
        sa.Column("message_id", sa.String(50), nullable=True),
        sa.Column("structured_data", postgresql.JSONB, nullable=True),
        sa.Column("device_type", sa.String(50), nullable=True),
        sa.Column("raw_log", sa.Text, nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_syslog_severity", "syslog_entries", ["severity"])
    op.create_index("ix_syslog_hostname", "syslog_entries", ["hostname"])
    op.create_index("ix_syslog_received", "syslog_entries", ["received_at"])

    op.create_table(
        "snmp_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("snmp_version", sa.String(4), server_default=sa.text("'v2c'")),
        sa.Column("community", sa.String(100), nullable=True),
        sa.Column("snmp_user", sa.String(100), nullable=True),
        sa.Column("snmp_auth_protocol", sa.String(20), nullable=True),
        sa.Column("snmp_auth_key", sa.String(100), nullable=True),
        sa.Column("snmp_priv_protocol", sa.String(20), nullable=True),
        sa.Column("snmp_priv_key", sa.String(100), nullable=True),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("vendor", sa.String(100), nullable=True),
        sa.Column("model", sa.String(100), nullable=True),
        sa.Column("os_version", sa.String(100), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("uptime_seconds", sa.BigInteger, nullable=True),
        sa.Column("poll_interval_seconds", sa.Integer, server_default=sa.text("300")),
        sa.Column("is_monitored", sa.Boolean, server_default=sa.text("true")),
        sa.Column("is_reachable", sa.Boolean, server_default=sa.text("false")),
        sa.Column("last_poll_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "snmp_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("snmp_devices.id"), nullable=False),
        sa.Column("oid", sa.String(255), nullable=False),
        sa.Column("metric_name", sa.String(100), nullable=False),
        sa.Column("value_float", sa.Float, nullable=True),
        sa.Column("value_int", sa.BigInteger, nullable=True),
        sa.Column("value_str", sa.String(500), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_snmp_metrics_device", "snmp_metrics", ["device_id"])
    op.create_index("ix_snmp_metrics_name", "snmp_metrics", ["metric_name"])

    op.create_table(
        "backup_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("device_type", sa.String(50), nullable=False),
        sa.Column("device_id", sa.String(255), nullable=False),
        sa.Column("device_hostname", sa.String(255), nullable=False),
        sa.Column("device_ip", sa.String(45), nullable=True),
        sa.Column("backup_type", sa.String(10), server_default=sa.text("'config'")),
        sa.Column("schedule_cron", sa.String(100), nullable=True),
        sa.Column("retention_count", sa.Integer, server_default=sa.text("30")),
        sa.Column("storage_path", sa.String(500), nullable=True),
        sa.Column("protocol", sa.String(20), server_default=sa.text("'scp'")),
        sa.Column("username", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(10), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "backup_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("backup_jobs.id"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("file_path", sa.String(1000), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column("status", sa.String(10), nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("duration_seconds", sa.Integer, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_backup_records_job", "backup_records", ["job_id"])


def downgrade() -> None:
    op.drop_table("backup_records")
    op.drop_table("backup_jobs")
    op.drop_table("snmp_metrics")
    op.drop_table("snmp_devices")
    op.drop_table("syslog_entries")
