"""network management: devices, ip, ping, bandwidth

Revision ID: 006
Revises: 005
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "network_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("mac_address", sa.String(17), nullable=False),
        sa.Column("device_type", sa.String(20), nullable=False),
        sa.Column("vendor", sa.String(200), nullable=True),
        sa.Column("model", sa.String(200), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("network_devices.id"), nullable=True),
        sa.Column("connection_type", sa.String(10), server_default=sa.text("'wired'")),
        sa.Column("port_count", sa.Integer, nullable=True),
        sa.Column("uptime_seconds", sa.BigInteger, nullable=True),
        sa.Column("firmware_version", sa.String(100), nullable=True),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column("is_monitored", sa.Boolean, server_default=sa.text("true")),
        sa.Column("discovered_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("last_seen", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_network_devices_ip", "network_devices", ["ip_address"])
    op.create_index("ix_network_devices_org", "network_devices", ["organization_id"])

    op.create_table(
        "ip_leases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("mac_address", sa.String(17), nullable=False),
        sa.Column("hostname", sa.String(255), nullable=True),
        sa.Column("vendor", sa.String(200), nullable=True),
        sa.Column("is_dhcp", sa.Boolean, server_default=sa.text("true")),
        sa.Column("is_static", sa.Boolean, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("conflict_detected", sa.Boolean, server_default=sa.text("false")),
        sa.Column("conflict_with", sa.String(45), nullable=True),
        sa.Column("leased_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_ip_leases_ip", "ip_leases", ["ip_address"])
    op.create_index("ix_ip_leases_org", "ip_leases", ["organization_id"])

    op.create_table(
        "ping_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("network_devices.id"), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("is_alive", sa.Boolean, server_default=sa.text("false")),
        sa.Column("latency_ms", sa.Float, nullable=True),
        sa.Column("packet_loss_pct", sa.Float, nullable=True),
        sa.Column("jitter_ms", sa.Float, nullable=True),
        sa.Column("response_time_ms", sa.Float, nullable=True),
        sa.Column("checked_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_ping_results_device", "ping_results", ["device_id"])
    op.create_index("ix_ping_results_org", "ping_results", ["organization_id"])

    op.create_table(
        "bandwidth_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("network_devices.id"), nullable=False),
        sa.Column("interface_name", sa.String(100), nullable=True),
        sa.Column("bytes_in", sa.BigInteger, server_default=sa.text("0")),
        sa.Column("bytes_out", sa.BigInteger, server_default=sa.text("0")),
        sa.Column("bytes_total", sa.BigInteger, server_default=sa.text("0")),
        sa.Column("bits_in_per_sec", sa.Float, server_default=sa.text("0")),
        sa.Column("bits_out_per_sec", sa.Float, server_default=sa.text("0")),
        sa.Column("utilization_pct", sa.Float, server_default=sa.text("0")),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_bandwidth_device", "bandwidth_records", ["device_id"])
    op.create_index("ix_bandwidth_org", "bandwidth_records", ["organization_id"])


def downgrade() -> None:
    op.drop_table("bandwidth_records")
    op.drop_table("ping_results")
    op.drop_table("ip_leases")
    op.drop_table("network_devices")
