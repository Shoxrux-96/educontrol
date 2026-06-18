import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, Text, BigInteger, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base import Base
import enum


class InternetRuleAction(str, enum.Enum):
    allow = "allow"
    block = "block"
    limit = "limit"
    warn = "warn"


class InternetRuleTarget(str, enum.Enum):
    url = "url"
    category = "category"
    user = "user"
    group = "group"
    computer = "computer"
    global_all = "global"


class InternetCategory(str, enum.Enum):
    social_media = "social_media"
    video_streaming = "video_streaming"
    gaming = "gaming"
    adult = "adult"
    torrent = "torrent"
    vpn = "vpn"
    chat = "chat"
    news = "news"
    shopping = "shopping"
    education = "education"
    productivity = "productivity"
    other = "other"


class BandwidthDirection(str, enum.Enum):
    download = "download"
    upload = "upload"
    both = "both"


class InternetRule(Base):
    __tablename__ = "internet_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    action: Mapped[InternetRuleAction] = mapped_column(
        Enum(InternetRuleAction), nullable=False
    )
    target_type: Mapped[InternetRuleTarget] = mapped_column(
        Enum(InternetRuleTarget), nullable=False
    )
    target_value: Mapped[str] = mapped_column(String(500), nullable=True)
    category: Mapped[InternetCategory] = mapped_column(
        Enum(InternetCategory), nullable=True
    )
    schedule: Mapped[dict] = mapped_column(JSONB, nullable=True)
    bandwidth_limit_kbps: Mapped[int] = mapped_column(Integer, nullable=True)
    bandwidth_direction: Mapped[BandwidthDirection] = mapped_column(
        Enum(BandwidthDirection), default=BandwidthDirection.both
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    organization = relationship("Organization")
    creator = relationship("User")
