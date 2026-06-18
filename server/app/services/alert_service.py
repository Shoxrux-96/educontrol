import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert_rule import AlertRule as AlertRuleModel
from app.models.alert_event import AlertEventModel
from app.schemas.monitoring import (
    AlertRule,
    AlertRuleCreate,
    AlertEvent,
    AlertStats,
)
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self):
        self._cache_rules: Dict[str, AlertRule] = {}
        self._cache_events: List[AlertEvent] = []
        self._events_max = 500

    async def create_rule(self, data: AlertRuleCreate, db: AsyncSession) -> AlertRule:
        model = AlertRuleModel(
            name=data.name,
            metric=data.metric,
            condition=data.condition,
            threshold=data.threshold,
            enabled=data.enabled,
            notification_channels=data.notification_channels,
            cooldown_minutes=data.cooldown_minutes,
        )
        db.add(model)
        await db.commit()
        await db.refresh(model)
        rule = AlertRule.model_validate(model)
        self._cache_rules[rule.id] = rule
        return rule

    async def list_rules(self, db: AsyncSession) -> List[AlertRule]:
        result = await db.execute(select(AlertRuleModel).order_by(AlertRuleModel.created_at))
        models = result.scalars().all()
        rules = [AlertRule.model_validate(m) for m in models]
        self._cache_rules = {r.id: r for r in rules}
        return rules

    async def get_rule(self, rule_id: str, db: AsyncSession) -> Optional[AlertRule]:
        if rule_id in self._cache_rules:
            return self._cache_rules[rule_id]
        result = await db.execute(select(AlertRuleModel).where(AlertRuleModel.id == rule_id))
        model = result.scalar_one_or_none()
        if model:
            rule = AlertRule.model_validate(model)
            self._cache_rules[rule.id] = rule
            return rule
        return None

    async def update_rule(self, rule_id: str, data: AlertRuleCreate, db: AsyncSession) -> Optional[AlertRule]:
        result = await db.execute(select(AlertRuleModel).where(AlertRuleModel.id == rule_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.name = data.name
        model.metric = data.metric
        model.condition = data.condition
        model.threshold = data.threshold
        model.enabled = data.enabled
        model.notification_channels = data.notification_channels
        model.cooldown_minutes = data.cooldown_minutes
        await db.commit()
        await db.refresh(model)
        rule = AlertRule.model_validate(model)
        self._cache_rules[rule.id] = rule
        return rule

    async def delete_rule(self, rule_id: str, db: AsyncSession) -> bool:
        result = await db.execute(select(AlertRuleModel).where(AlertRuleModel.id == rule_id))
        model = result.scalar_one_or_none()
        if not model:
            return False
        await db.delete(model)
        await db.commit()
        self._cache_rules.pop(rule_id, None)
        return True

    async def check_rules(self, current_metrics: dict, db: AsyncSession) -> List[AlertEvent]:
        triggered = []
        now = datetime.now(timezone.utc)
        rules = await self.list_rules(db)

        for rule in rules:
            if not rule.enabled:
                continue
            actual_value = current_metrics.get(rule.metric)
            if actual_value is None:
                continue
            if rule.last_triggered:
                cooldown_elapsed = (now - rule.last_triggered).total_seconds() / 60
                if cooldown_elapsed < rule.cooldown_minutes:
                    continue
            triggered_flag = False
            if rule.condition == "gt" and actual_value > rule.threshold:
                triggered_flag = True
            elif rule.condition == "lt" and actual_value < rule.threshold:
                triggered_flag = True
            elif rule.condition == "gte" and actual_value >= rule.threshold:
                triggered_flag = True
            elif rule.condition == "lte" and actual_value <= rule.threshold:
                triggered_flag = True
            elif rule.condition == "eq" and actual_value == rule.threshold:
                triggered_flag = True
            if triggered_flag:
                alert = await self.trigger_alert(rule, actual_value, db)
                triggered.append(alert)
        return triggered

    async def trigger_alert(self, rule: AlertRule, actual_value: float, db: AsyncSession) -> AlertEvent:
        now = datetime.now(timezone.utc)
        event_model = AlertEventModel(
            rule_id=rule.id,
            rule_name=rule.name,
            metric=rule.metric,
            actual_value=actual_value,
            threshold=rule.threshold,
            triggered_at=now,
        )
        db.add(event_model)
        await db.commit()
        await db.refresh(event_model)
        alert = AlertEvent.model_validate(event_model)

        rule.last_triggered = now
        result = await db.execute(select(AlertRuleModel).where(AlertRuleModel.id == rule.id))
        db_rule = result.scalar_one_or_none()
        if db_rule:
            db_rule.last_triggered = now
            await db.commit()

        self._cache_events.insert(0, alert)
        if len(self._cache_events) > self._events_max:
            self._cache_events.pop()

        logger.warning(
            f"ALERT triggered: {rule.name} | metric={rule.metric} "
            f"value={actual_value} threshold={rule.threshold} condition={rule.condition}"
        )
        if "log" in rule.notification_channels:
            logger.info(f"Alert notification logged: {alert.rule_name} - {alert.metric}={alert.actual_value}")
        if "email" in rule.notification_channels:
            email_service.send_alert_notification(alert.model_dump())
        return alert

    async def acknowledge_alert(self, alert_id: str, user: Optional[str] = None, db: AsyncSession = None) -> Optional[AlertEvent]:
        if db is None:
            for alert in self._cache_events:
                if alert.id == alert_id:
                    alert.acknowledged = True
                    alert.acknowledged_by = user
                    return alert
            return None
        result = await db.execute(select(AlertEventModel).where(AlertEventModel.id == alert_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.acknowledged = True
        model.acknowledged_by = user
        await db.commit()
        await db.refresh(model)
        alert = AlertEvent.model_validate(model)
        for i, e in enumerate(self._cache_events):
            if e.id == alert_id:
                self._cache_events[i] = alert
                break
        return alert

    async def list_alerts(self, db: AsyncSession, limit: int = 50) -> List[AlertEvent]:
        result = await db.execute(
            select(AlertEventModel).order_by(AlertEventModel.triggered_at.desc()).limit(limit)
        )
        models = result.scalars().all()
        events = [AlertEvent.model_validate(m) for m in models]
        self._cache_events = events
        return events

    async def get_alert_stats(self, db: AsyncSession) -> AlertStats:
        events = await self.list_alerts(db, 200)
        total = len(events)
        active = sum(1 for e in events if not e.acknowledged)
        acknowledged = sum(1 for e in events if e.acknowledged)
        by_severity: Dict[str, int] = {"critical": 0, "warning": 0, "info": 0}
        for e in events:
            if not e.acknowledged:
                ratio = abs(e.actual_value - e.threshold) / max(abs(e.threshold), 1) if e.threshold else 0
                if ratio > 0.5:
                    by_severity["critical"] += 1
                elif ratio > 0.2:
                    by_severity["warning"] += 1
                else:
                    by_severity["info"] += 1
        return AlertStats(
            total_alerts=total,
            active_alerts=active,
            acknowledged=acknowledged,
            by_severity=by_severity,
        )


alert_service = AlertService()
