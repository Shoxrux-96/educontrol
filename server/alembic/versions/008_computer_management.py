"""computer management: remote desktop, software inventory, deployment

Revision ID: 008
Revises: 007
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "remote_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(10), server_default=sa.text("'active'")),
        sa.Column("protocol", sa.String(20), server_default=sa.text("'vnc'")),
        sa.Column("screen_width", sa.Integer, nullable=True),
        sa.Column("screen_height", sa.Integer, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_activity", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "software_inventory",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=False),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("version", sa.String(100), nullable=True),
        sa.Column("publisher", sa.String(255), nullable=True),
        sa.Column("install_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("install_location", sa.String(500), nullable=True),
        sa.Column("uninstall_string", sa.Text, nullable=True),
        sa.Column("size_mb", sa.Float, nullable=True),
        sa.Column("is_system_component", sa.Boolean, server_default=sa.text("false")),
        sa.Column("detected_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_software_inventory_computer", "software_inventory", ["computer_id"])
    op.create_index("ix_software_inventory_name", "software_inventory", ["name"])

    op.create_table(
        "software_packages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("package_type", sa.String(50), nullable=False),
        sa.Column("installer_path", sa.String(500), nullable=True),
        sa.Column("installer_url", sa.String(1000), nullable=True),
        sa.Column("installer_args", sa.String(500), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column("size_mb", sa.Float, nullable=True),
        sa.Column("icon", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "software_deployments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("package_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("software_packages.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("target_type", sa.String(20), nullable=False),
        sa.Column("target_ids", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(10), server_default=sa.text("'pending'")),
        sa.Column("total_computers", sa.Integer, server_default=sa.text("0")),
        sa.Column("completed_computers", sa.Integer, server_default=sa.text("0")),
        sa.Column("failed_computers", sa.Integer, server_default=sa.text("0")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_software_deployments_status", "software_deployments", ["status"])


def downgrade() -> None:
    op.drop_table("software_deployments")
    op.drop_table("software_packages")
    op.drop_table("software_inventory")
    op.drop_table("remote_sessions")
