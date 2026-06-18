import psutil
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from collections import deque

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas.monitoring import (
    ServerStats,
    ServiceStatus,
    SystemHealth,
    MetricHistoryPoint,
    DashboardStats,
)
from app.models.computer import Computer, ComputerStatus
from app.models.user import User
from app.models.policy import Policy
from app.models.command import Command
from app.websocket.manager import manager

logger = logging.getLogger(__name__)


class MonitorService:
    def __init__(self):
        self.metric_history: deque = deque(maxlen=1440)

    def get_server_stats(self) -> ServerStats:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        boot_time = psutil.boot_time()
        uptime = int(datetime.now().timestamp() - boot_time)

        return ServerStats(
            cpu_percent=cpu,
            ram_percent=ram.percent,
            ram_used_gb=round(ram.used / (1024**3), 2),
            ram_total_gb=round(ram.total / (1024**3), 2),
            disk_percent=disk.percent,
            disk_used_gb=round(disk.used / (1024**3), 2),
            disk_total_gb=round(disk.total / (1024**3), 2),
            uptime_seconds=uptime,
        )

    async def check_service_status(self, db: Optional[AsyncSession] = None) -> List[ServiceStatus]:
        services = []
        now = datetime.now(timezone.utc)

        services.append(await self._check_postgres(db))
        services.append(await self._check_redis())
        services.append(await self._check_celery())

        return services

    async def _check_postgres(self, db: Optional[AsyncSession]) -> ServiceStatus:
        now = datetime.now(timezone.utc)
        if db is None:
            return ServiceStatus(name="postgres", status="unknown", last_check=now, details={"error": "no session"})
        try:
            await db.execute(select(1))
            return ServiceStatus(name="postgres", status="healthy", last_check=now)
        except Exception as e:
            logger.error(f"Postgres check failed: {e}")
            return ServiceStatus(name="postgres", status="down", last_check=now, details={"error": str(e)})

    async def _check_redis(self) -> ServiceStatus:
        now = datetime.now(timezone.utc)
        try:
            import redis.asyncio as aioredis
            from app.config import settings
            r = aioredis.from_url(settings.redis_url)
            await r.ping()
            await r.aclose()
            return ServiceStatus(name="redis", status="healthy", last_check=now)
        except ImportError:
            return ServiceStatus(name="redis", status="unknown", last_check=now, details={"error": "redis not installed"})
        except Exception as e:
            logger.error(f"Redis check failed: {e}")
            return ServiceStatus(name="redis", status="down", last_check=now, details={"error": str(e)})

    async def _check_celery(self) -> ServiceStatus:
        now = datetime.now(timezone.utc)
        try:
            from app.tasks.celery_app import celery_app
            inspect = celery_app.control.inspect()
            active = inspect.active()
            if active is not None:
                return ServiceStatus(name="celery", status="healthy", last_check=now, details={"active_workers": len(active)})
            return ServiceStatus(name="celery", status="unhealthy", last_check=now, details={"error": "no workers"})
        except Exception as e:
            logger.error(f"Celery check failed: {e}")
            return ServiceStatus(name="celery", status="down", last_check=now, details={"error": str(e)})

    async def get_system_health(self, db: Optional[AsyncSession] = None) -> SystemHealth:
        server = self.get_server_stats()
        services = await self.check_service_status(db)

        all_healthy = all(s.status == "healthy" for s in services)
        any_down = any(s.status == "down" for s in services)
        if any_down:
            overall = "degraded"
        elif all_healthy:
            overall = "healthy"
        else:
            overall = "degraded"

        return SystemHealth(
            overall_status=overall,
            server=server,
            services=services,
            agents_connected=manager.active_connections,
            active_connections=manager.active_connections,
            uptime_seconds=server.uptime_seconds,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_metric_history(self, hours: int = 24) -> List[MetricHistoryPoint]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        return [
            p for p in self.metric_history
            if p.timestamp >= cutoff
        ]

    def record_metric(self, value: float):
        self.metric_history.append(
            MetricHistoryPoint(timestamp=datetime.now(timezone.utc), value=value)
        )

    async def get_dashboard_stats(self, db: AsyncSession) -> DashboardStats:
        total_result = await db.execute(select(func.count(Computer.id)))
        total_computers = total_result.scalar() or 0

        online_result = await db.execute(
            select(func.count(Computer.id)).where(Computer.status == ComputerStatus.online)
        )
        online_computers = online_result.scalar() or 0

        offline_result = await db.execute(
            select(func.count(Computer.id)).where(Computer.status == ComputerStatus.offline)
        )
        offline_computers = offline_result.scalar() or 0

        user_result = await db.execute(select(func.count(User.id)))
        total_users = user_result.scalar() or 0

        policy_result = await db.execute(
            select(func.count(Policy.id)).where(Policy.is_active == True)
        )
        active_policies = policy_result.scalar() or 0

        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        from app.models.audit_log import AuditLog
        alerts_result = await db.execute(
            select(func.count(AuditLog.id)).where(
                AuditLog.event_type == "alert",
                AuditLog.created_at >= today_start,
            )
        )
        alerts_today = alerts_result.scalar() or 0

        commands_result = await db.execute(
            select(func.count(Command.id)).where(Command.sent_at >= today_start)
        )
        commands_today = commands_result.scalar() or 0

        return DashboardStats(
            total_computers=total_computers,
            online_computers=online_computers,
            offline_computers=offline_computers,
            total_users=total_users,
            active_policies=active_policies,
            alerts_today=alerts_today,
            commands_today=commands_today,
        )


monitor_service = MonitorService()
