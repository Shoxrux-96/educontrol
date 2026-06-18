import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.base import Base


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    metric = Column(String(50), nullable=False)
    condition = Column(String(10), nullable=False)
    threshold = Column(Float, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    notification_channels = Column(JSONB, default=["log"], nullable=False)
    cooldown_minutes = Column(Integer, default=15, nullable=False)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    created_by = Column(UUID(as_uuid=True), nullable=True)

    organization = relationship("Organization", back_populates="alert_rules")
