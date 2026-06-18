"""it management platform: internet, firewall, helpdesk, vpn

Revision ID: 005
Revises: 004
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "internet_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("target_type", sa.String(20), nullable=False),
        sa.Column("target_value", sa.String(500), nullable=True),
        sa.Column("category", sa.String(30), nullable=True),
        sa.Column("schedule", postgresql.JSONB, nullable=True),
        sa.Column("bandwidth_limit_kbps", sa.Integer, nullable=True),
        sa.Column("bandwidth_direction", sa.String(10), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer, server_default=sa.text("100")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "firewall_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("action", sa.String(10), nullable=False),
        sa.Column("direction", sa.String(10), server_default=sa.text("'both'")),
        sa.Column("protocol", sa.String(10), server_default=sa.text("'ANY'")),
        sa.Column("match_type", sa.String(15), nullable=False),
        sa.Column("match_value", sa.String(500), nullable=False),
        sa.Column("source_ip", sa.String(45), nullable=True),
        sa.Column("destination_ip", sa.String(45), nullable=True),
        sa.Column("source_port", sa.Integer, nullable=True),
        sa.Column("destination_port", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer, server_default=sa.text("100")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "traffic_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("bytes_sent", sa.BigInteger, server_default=sa.text("0")),
        sa.Column("bytes_received", sa.BigInteger, server_default=sa.text("0")),
        sa.Column("bytes_total", sa.BigInteger, server_default=sa.text("0")),
        sa.Column("destination_ip", sa.String(45), nullable=True),
        sa.Column("destination_host", sa.String(500), nullable=True),
        sa.Column("destination_port", sa.Integer, nullable=True),
        sa.Column("protocol", sa.String(10), nullable=True),
        sa.Column("application", sa.String(100), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("blocked", sa.Boolean, server_default=sa.text("false")),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_traffic_logs_logged_at", "traffic_logs", ["logged_at"])
    op.create_index("ix_traffic_logs_computer", "traffic_logs", ["computer_id"])
    op.create_index("ix_traffic_logs_organization", "traffic_logs", ["organization_id"])

    op.create_table(
        "helpdesk_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("category", sa.String(20), server_default=sa.text("'other'")),
        sa.Column("priority", sa.String(10), server_default=sa.text("'medium'")),
        sa.Column("status", sa.String(15), server_default=sa.text("'open'")),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ticket_comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("helpdesk_tickets.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("is_internal", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "vpn_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("vpn_type", sa.String(20), server_default=sa.text("'wireguard'")),
        sa.Column("server_address", sa.String(500), nullable=False),
        sa.Column("server_port", sa.Integer, nullable=False),
        sa.Column("allowed_ips", sa.Text, nullable=True),
        sa.Column("dns_servers", sa.String(500), nullable=True),
        sa.Column("public_key", sa.Text, nullable=True),
        sa.Column("private_key", sa.Text, nullable=True),
        sa.Column("preshared_key", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "vpn_clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("profile_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("vpn_profiles.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("client_ip", sa.String(45), nullable=True),
        sa.Column("public_key", sa.Text, nullable=True),
        sa.Column("private_key", sa.Text, nullable=True),
        sa.Column("allowed_ips", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disconnected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("vpn_clients")
    op.drop_table("vpn_profiles")
    op.drop_table("ticket_comments")
    op.drop_table("helpdesk_tickets")
    op.drop_table("traffic_logs")
    op.drop_table("firewall_rules")
    op.drop_table("internet_rules")
