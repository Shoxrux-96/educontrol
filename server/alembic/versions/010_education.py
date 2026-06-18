"""education module: exams, tests, student monitoring

Revision ID: 010
Revises: 009
Create Date: 2025-06-16
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "exam_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("subject", sa.String(200), nullable=True),
        sa.Column("status", sa.String(10), server_default=sa.text("'scheduled'")),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("block_internet", sa.Boolean, server_default=sa.text("true")),
        sa.Column("block_usb", sa.Boolean, server_default=sa.text("true")),
        sa.Column("block_alt_tab", sa.Boolean, server_default=sa.text("true")),
        sa.Column("block_task_manager", sa.Boolean, server_default=sa.text("true")),
        sa.Column("block_cmd", sa.Boolean, server_default=sa.text("false")),
        sa.Column("allow_applications", postgresql.JSONB, nullable=True),
        sa.Column("monitor_screens", sa.Boolean, server_default=sa.text("true")),
        sa.Column("auto_submit_on_leave", sa.Boolean, server_default=sa.text("true")),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "exam_participants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exam_sessions.id"), nullable=False),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=False),
        sa.Column("student_name", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), server_default=sa.text("'pending'")),
        sa.Column("screen_monitored", sa.Boolean, server_default=sa.text("true")),
        sa.Column("computer_blocked", sa.Boolean, server_default=sa.text("false")),
        sa.Column("violations", sa.Integer, server_default=sa.text("0")),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_exam_participants_exam", "exam_participants", ["exam_id"])

    op.create_table(
        "test_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exam_sessions.id"), nullable=True),
        sa.Column("question_type", sa.String(10), server_default=sa.text("'single'")),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("options", postgresql.JSONB, nullable=True),
        sa.Column("correct_answer", sa.Text, nullable=True),
        sa.Column("points", sa.Integer, server_default=sa.text("1")),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "test_answers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("test_questions.id"), nullable=False),
        sa.Column("participant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exam_participants.id"), nullable=False),
        sa.Column("answer", sa.Text, nullable=True),
        sa.Column("is_correct", sa.Boolean, nullable=True),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "student_activity_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("exam_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("exam_sessions.id"), nullable=True),
        sa.Column("computer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("computers.id"), nullable=False),
        sa.Column("student_name", sa.String(255), nullable=True),
        sa.Column("activity_type", sa.String(50), nullable=False),
        sa.Column("details", postgresql.JSONB, nullable=True),
        sa.Column("severity", sa.String(20), server_default=sa.text("'info'")),
        sa.Column("logged_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("student_activity_logs")
    op.drop_table("test_answers")
    op.drop_table("test_questions")
    op.drop_table("exam_participants")
    op.drop_table("exam_sessions")
