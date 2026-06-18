"""multi-tenant: organizations + org_id columns

Revision ID: 004
Revises: 003
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(50), nullable=True),
        sa.Column("address", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("max_computers", sa.Integer, server_default=sa.text("100"), nullable=False),
        sa.Column("settings", postgresql.JSONB, server_default=sa.text("'{}'::jsonb"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.add_column("users", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=True))
    op.create_index("ix_users_organization_id", "users", ["organization_id"])

    op.add_column("computer_groups", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("computer_groups", "organization_id", server_default=None)

    op.add_column("computers", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("computers", "organization_id", server_default=None)

    op.add_column("policies", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("policies", "organization_id", server_default=None)

    op.add_column("commands", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("commands", "organization_id", server_default=None)

    op.add_column("messages", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("messages", "organization_id", server_default=None)

    op.add_column("audit_logs", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("audit_logs", "organization_id", server_default=None)

    op.add_column("screenshots", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("screenshots", "organization_id", server_default=None)

    op.add_column("alert_rules", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("alert_rules", "organization_id", server_default=None)

    op.add_column("agent_builds", sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, server_default=sa.text("gen_random_uuid()")))
    op.alter_column("agent_builds", "organization_id", server_default=None)

    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check")
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'owner'")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'viewer'")


def downgrade() -> None:
    op.drop_column("agent_builds", "organization_id")
    op.drop_column("alert_rules", "organization_id")
    op.drop_column("screenshots", "organization_id")
    op.drop_column("audit_logs", "organization_id")
    op.drop_column("messages", "organization_id")
    op.drop_column("commands", "organization_id")
    op.drop_column("policies", "organization_id")
    op.drop_column("computers", "organization_id")
    op.drop_column("computer_groups", "organization_id")
    op.drop_column("users", "organization_id")
    op.drop_table("organizations")
