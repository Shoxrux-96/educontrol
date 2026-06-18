"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-06-15 12:00:00.000000
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('super_admin', 'admin', 'viewer')")
    op.execute("CREATE TYPE computerstatus AS ENUM ('online', 'offline', 'busy', 'locked', 'maintenance')")
    op.execute("CREATE TYPE eventseverity AS ENUM ('info', 'warning', 'critical')")
    op.execute("CREATE TYPE policytype AS ENUM ('internet', 'application', 'usb', 'print_screen')")
    op.execute("CREATE TYPE policytargettype AS ENUM ('computer', 'group', 'all')")
    op.execute("CREATE TYPE messagetype AS ENUM ('info', 'warning', 'critical')")
    op.execute("CREATE TYPE commandstatus AS ENUM ('pending', 'sent', 'delivered', 'executed', 'failed')")

    # --- computer_groups ---
    op.create_table(
        "computer_groups",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- users (self-referencing FK) ---
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", ENUM("super_admin", "admin", "viewer", name="userrole", create_type=False), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        sa.UniqueConstraint("email"),
    )

    # --- computers ---
    op.create_table(
        "computers",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("hostname", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("mac_address", sa.String(length=17), nullable=True),
        sa.Column("group_id", UUID(as_uuid=True), nullable=True),
        sa.Column("os_version", sa.String(length=100), nullable=True),
        sa.Column("agent_version", sa.String(length=20), nullable=True),
        sa.Column("status", ENUM("online", "offline", "busy", "locked", "maintenance", name="computerstatus", create_type=False), nullable=False),
        sa.Column("last_seen", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cpu_model", sa.String(length=200), nullable=True),
        sa.Column("ram_gb", sa.SmallInteger(), nullable=True),
        sa.Column("disk_gb", sa.SmallInteger(), nullable=True),
        sa.Column("current_user", sa.String(length=100), nullable=True),
        sa.Column("cpu_usage", sa.SmallInteger(), nullable=True),
        sa.Column("ram_usage", sa.SmallInteger(), nullable=True),
        sa.Column("disk_usage", sa.SmallInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["computer_groups.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- audit_logs (partitioned) ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("severity", ENUM("info", "warning", "critical", name="eventseverity", create_type=False), nullable=False),
        sa.Column("computer_id", UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("metadata", JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", "created_at"),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        postgresql_partition_by="RANGE (created_at)",
    )

    # --- policies ---
    op.create_table(
        "policies",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("policy_type", ENUM("internet", "application", "usb", "print_screen", name="policytype", create_type=False), nullable=False),
        sa.Column("config", JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- policy_assignments ---
    op.create_table(
        "policy_assignments",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("policy_id", UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", ENUM("computer", "group", "all", name="policytargettype", create_type=False), nullable=False),
        sa.Column("target_id", UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_by", UUID(as_uuid=True), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["policy_id"], ["policies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- messages ---
    op.create_table(
        "messages",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("message_type", ENUM("info", "warning", "critical", name="messagetype", create_type=False), nullable=False),
        sa.Column("sender_id", UUID(as_uuid=True), nullable=True),
        sa.Column("target_type", ENUM("computer", "group", "all", name="policytargettype", create_type=False), nullable=False),
        sa.Column("target_id", UUID(as_uuid=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- commands ---
    op.create_table(
        "commands",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("computer_id", UUID(as_uuid=True), nullable=False),
        sa.Column("command_type", sa.String(length=50), nullable=False),
        sa.Column("payload", JSONB(), nullable=True),
        sa.Column("status", ENUM("pending", "sent", "delivered", "executed", "failed", name="commandstatus", create_type=False), nullable=False),
        sa.Column("sent_by", UUID(as_uuid=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("result", JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sent_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )

    # --- screenshots ---
    op.create_table(
        "screenshots",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("computer_id", UUID(as_uuid=True), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["computer_id"], ["computers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("screenshots")
    op.drop_table("commands")
    op.drop_table("messages")
    op.drop_table("policy_assignments")
    op.drop_table("policies")
    op.drop_table("audit_logs")
    op.drop_table("computers")
    op.drop_table("users")
    op.drop_table("computer_groups")
    # Ignore drop type errors (might not exist)
    op.execute("DROP TYPE IF EXISTS commandstatus")
    op.execute("DROP TYPE IF EXISTS messagetype")
    op.execute("DROP TYPE IF EXISTS policytargettype")
    op.execute("DROP TYPE IF EXISTS policytype")
    op.execute("DROP TYPE IF EXISTS eventseverity")
    op.execute("DROP TYPE IF EXISTS computerstatus")
    op.execute("DROP TYPE IF EXISTS userrole")
