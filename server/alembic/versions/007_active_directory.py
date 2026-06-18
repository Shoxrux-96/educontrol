"""active directory integration: domain, users, groups, OUs, GPO

Revision ID: 007
Revises: 006
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "domain_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False, unique=True),
        sa.Column("domain_name", sa.String(255), nullable=False),
        sa.Column("domain_controller", sa.String(255), nullable=False),
        sa.Column("ldap_base_dn", sa.String(500), nullable=False),
        sa.Column("ldap_user", sa.String(255), nullable=True),
        sa.Column("ldap_password", sa.String(255), nullable=True),
        sa.Column("use_ssl", sa.Boolean, server_default=sa.text("true")),
        sa.Column("sync_interval_minutes", sa.Integer, server_default=sa.text("60")),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sync_status", sa.String(10), server_default=sa.text("'pending'")),
        sa.Column("sso_enabled", sa.Boolean, server_default=sa.text("false")),
        sa.Column("auto_create_users", sa.Boolean, server_default=sa.text("true")),
        sa.Column("default_role", sa.String(20), server_default=sa.text("'viewer'")),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ad_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("domain_config_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("domain_configs.id"), nullable=False),
        sa.Column("sam_account_name", sa.String(255), nullable=False),
        sa.Column("user_principal_name", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("given_name", sa.String(100), nullable=True),
        sa.Column("surname", sa.String(100), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("distinguished_name", sa.String(500), nullable=False),
        sa.Column("ou_dn", sa.String(500), nullable=True),
        sa.Column("enabled", sa.Boolean, server_default=sa.text("true")),
        sa.Column("locked_out", sa.Boolean, server_default=sa.text("false")),
        sa.Column("last_logon", sa.DateTime(timezone=True), nullable=True),
        sa.Column("linked_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("is_synced", sa.Boolean, server_default=sa.text("false")),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ad_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("domain_config_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("domain_configs.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sam_account_name", sa.String(255), nullable=True),
        sa.Column("distinguished_name", sa.String(500), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("group_type", sa.String(50), nullable=True),
        sa.Column("member_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("is_synced", sa.Boolean, server_default=sa.text("false")),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ad_ous",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("domain_config_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("domain_configs.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("distinguished_name", sa.String(500), nullable=False),
        sa.Column("parent_dn", sa.String(500), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("user_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("computer_count", sa.Integer, server_default=sa.text("0")),
        sa.Column("is_synced", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "ad_gpos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("target_type", sa.String(10), server_default=sa.text("'all'")),
        sa.Column("target_id", sa.String(255), nullable=True),
        sa.Column("settings", sa.JSON, nullable=True),
        sa.Column("usb_block", sa.Boolean, server_default=sa.text("false")),
        sa.Column("control_panel_block", sa.Boolean, server_default=sa.text("false")),
        sa.Column("cmd_block", sa.Boolean, server_default=sa.text("false")),
        sa.Column("registry_block", sa.Boolean, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean, server_default=sa.text("false")),
        sa.Column("apply_to_computers", sa.Boolean, server_default=sa.text("false")),
        sa.Column("apply_to_users", sa.Boolean, server_default=sa.text("false")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("ad_gpos")
    op.drop_table("ad_ous")
    op.drop_table("ad_groups")
    op.drop_table("ad_users")
    op.drop_table("domain_configs")
