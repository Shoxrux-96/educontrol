from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.monitoring import (
    SystemHealth,
    DashboardStats,
    MetricHistoryPoint,
    AlertEvent,
    AlertStats,
    AlertRule,
    AlertRuleCreate,
)
from app.services.monitor_service import monitor_service
from app.services.alert_service import alert_service
from app.utils.security import get_current_user, require_role
from app.models.user import User

router = APIRouter(prefix="/api/v1/monitoring", tags=["Monitoring"])


@router.get("/health", response_model=SystemHealth)
async def get_system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await monitor_service.get_system_health(db)


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await monitor_service.get_dashboard_stats(db)


@router.get("/metrics/history", response_model=list[MetricHistoryPoint])
async def get_metric_history(
    hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
):
    return await monitor_service.get_metric_history(hours)


@router.get("/alerts", response_model=list[AlertEvent])
async def list_alerts(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
):
    return alert_service.list_alerts(limit)


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertEvent)
async def acknowledge_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),
):
    alert = alert_service.acknowledge_alert(alert_id, str(current_user.id))
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.get("/alerts/stats", response_model=AlertStats)
async def get_alert_stats(
    current_user: User = Depends(get_current_user),
):
    return alert_service.get_alert_stats()


@router.get("/alerts/rules", response_model=list[AlertRule])
async def list_alert_rules(
    current_user: User = Depends(get_current_user),
):
    return alert_service.list_rules()


@router.post("/alerts/rules", response_model=AlertRule, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    data: AlertRuleCreate,
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    return alert_service.create_rule(data)


@router.put("/alerts/rules/{rule_id}", response_model=AlertRule)
async def update_alert_rule(
    rule_id: str,
    data: AlertRuleCreate,
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    rule = alert_service.update_rule(rule_id, data)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found")
    return rule


@router.delete("/alerts/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: str,
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    if not alert_service.delete_rule(rule_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert rule not found")
