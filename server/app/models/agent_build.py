import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, BigInteger, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.base import Base


class AgentBuild(Base):
    __tablename__ = "agent_builds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(20), nullable=False)
    arch: Mapped[str] = mapped_column(String(10), nullable=False, default="x86_64")
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    changelog: Mapped[str] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
