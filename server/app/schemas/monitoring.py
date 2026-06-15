from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.utils.types import UUIDStr


class ServerStats(BaseModel):
    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float
    uptime_seconds: int


class ServiceStatus(BaseModel):
    name: str
    status: str
    last_check: datetime
    details: Optional[dict] = None


class SystemHealth(BaseModel):
    overall_status: str
    server: ServerStats
    services: List[ServiceStatus]
    agents_connected: int
    active_connections: int
    uptime_seconds: int
    timestamp: datetime


class AlertRule(BaseModel):
    id: UUIDStr
    name: str
    metric: str
    condition: str
    threshold: float
    enabled: bool
    notification_channels: List[str]
    cooldown_minutes: int
    last_triggered: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AlertRuleCreate(BaseModel):
    name: str
    metric: str
    condition: str
    threshold: float
    enabled: bool = True
    notification_channels: List[str] = ["log"]
    cooldown_minutes: int = 15


class AlertEvent(BaseModel):
    id: UUIDStr
    rule_id: UUIDStr
    rule_name: str
    metric: str
    actual_value: float
    threshold: float
    triggered_at: datetime
    acknowledged: bool
    acknowledged_by: Optional[str] = None

    model_config = {"from_attributes": True}


class AlertStats(BaseModel):
    total_alerts: int
    active_alerts: int
    acknowledged: int
    by_severity: dict


class MetricHistoryPoint(BaseModel):
    timestamp: datetime
    value: float


class DashboardStats(BaseModel):
    total_computers: int
    online_computers: int
    offline_computers: int
    total_users: int
    active_policies: int
    alerts_today: int
    commands_today: int
