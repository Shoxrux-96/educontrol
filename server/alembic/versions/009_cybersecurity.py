"""cybersecurity module: usb, antivirus, threats, login audit, policies

Revision ID: 009
Revises: 008
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "usb_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=False),
        sa.Column("action", sa.String(10), nullable=False),
        sa.Column("device_name", sa.String(255), nullable=True),
        sa.Column("device_label", sa.String(255), nullable=True),
        sa.Column("vendor_id", sa.String(10), nullable=True),
        sa.Column("product_id", sa.String(10), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("vendor_name", sa.String(255), nullable=True),
        sa.Column("capacity_mb", sa.Integer, nullable=True),
        sa.Column("filesystem", sa.String(20), nullable=True),
        sa.Column("blocked", sa.Boolean, server_default=sa.text("false")),
        sa.Column("blocked_by_policy", sa.String(100), nullable=True),
        sa.Column("username", sa.String(100), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_usb_events_computer", "usb_events", ["computer_id"])
    op.create_index("ix_usb_events_detected", "usb_events", ["detected_at"])

    op.create_table(
        "antivirus_statuses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=False, unique=True),
        sa.Column("product_name", sa.String(20), server_default=sa.text("'windows_defender'")),
        sa.Column("product_version", sa.String(50), nullable=True),
        sa.Column("definitions_version", sa.String(50), nullable=True),
        sa.Column("definitions_updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("definitions_up_to_date", sa.Boolean, server_default=sa.text("false")),
        sa.Column("realtime_protection", sa.Boolean, server_default=sa.text("false")),
        sa.Column("firewall_enabled", sa.Boolean, server_default=sa.text("false")),
        sa.Column("last_scan_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_scan_result", sa.String(50), nullable=True),
        sa.Column("threats_found", sa.Integer, server_default=sa.text("0")),
        sa.Column("threats_cleaned", sa.Integer, server_default=sa.text("0")),
        sa.Column("is_installed", sa.Boolean, server_default=sa.text("true")),
        sa.Column("is_running", sa.Boolean, server_default=sa.text("false")),
        sa.Column("requires_restart", sa.Boolean, server_default=sa.text("false")),
        sa.Column("status_updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_antivirus_computer", "antivirus_statuses", ["computer_id"])

    op.create_table(
        "threat_detections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=False),
        sa.Column("threat_type", sa.String(15), nullable=False),
        sa.Column("severity", sa.String(10), server_default=sa.text("'medium'")),
        sa.Column("threat_name", sa.String(500), nullable=True),
        sa.Column("file_path", sa.String(1000), nullable=True),
        sa.Column("md5_hash", sa.String(32), nullable=True),
        sa.Column("sha256_hash", sa.String(64), nullable=True),
        sa.Column("action_taken", sa.String(50), nullable=True),
        sa.Column("is_quarantined", sa.Boolean, server_default=sa.text("false")),
        sa.Column("is_cleaned", sa.Boolean, server_default=sa.text("false")),
        sa.Column("detected_by", sa.String(100), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_threat_detections_computer", "threat_detections", ["computer_id"])
    op.create_index("ix_threat_detections_severity", "threat_detections", ["severity"])

    op.create_table(
        "login_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=True),
        sa.Column("username", sa.String(100), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("result", sa.String(10), nullable=False),
        sa.Column("failure_reason", sa.String(255), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("session_duration_seconds", sa.Integer, nullable=True),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_login_audits_user", "login_audits", ["username"])
    op.create_index("ix_login_audits_logged", "login_audits", ["logged_at"])

    op.create_table(
        "security_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, unique=True),
        sa.Column("usb_block_enabled", sa.Boolean, server_default=sa.text("false")),
        sa.Column("usb_whitelist", postgresql.JSON, nullable=True),
        sa.Column("usb_block_external", sa.Boolean, server_default=sa.text("true")),
        sa.Column("av_required", sa.Boolean, server_default=sa.text("true")),
        sa.Column("av_realtime_required", sa.Boolean, server_default=sa.text("true")),
        sa.Column("av_definitions_max_age_hours", sa.Integer, server_default=sa.text("48")),
        sa.Column("auto_threat_quarantine", sa.Boolean, server_default=sa.text("true")),
        sa.Column("notify_on_threat", sa.Boolean, server_default=sa.text("true")),
        sa.Column("notify_on_usb", sa.Boolean, server_default=sa.text("false")),
        sa.Column("failed_login_threshold", sa.Integer, server_default=sa.text("5")),
        sa.Column("login_notify_on_failure", sa.Boolean, server_default=sa.text("true")),
        sa.Column("password_complexity_required", sa.Boolean, server_default=sa.text("true")),
        sa.Column("session_timeout_minutes", sa.Integer, server_default=sa.text("60")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("security_policies")
    op.drop_table("login_audits")
    op.drop_table("threat_detections")
    op.drop_table("antivirus_statuses")
    op.drop_table("usb_events")
