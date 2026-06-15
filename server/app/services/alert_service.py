import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.monitoring import (
    AlertRule,
    AlertRuleCreate,
    AlertEvent,
    AlertStats,
)
from app.utils.types import UUIDStr
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self):
        self._rules: Dict[str, AlertRule] = {}
        self._events: List[AlertEvent] = []
        self._events_max = 500

    def create_rule(self, data: AlertRuleCreate) -> AlertRule:
        rule = AlertRule(
            id=str(uuid.uuid4()),
            name=data.name,
            metric=data.metric,
            condition=data.condition,
            threshold=data.threshold,
            enabled=data.enabled,
            notification_channels=data.notification_channels,
            cooldown_minutes=data.cooldown_minutes,
            last_triggered=None,
        )
        self._rules[rule.id] = rule
        logger.info(f"Alert rule created: {rule.name} ({rule.id})")
        return rule

    def list_rules(self) -> List[AlertRule]:
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        return self._rules.get(rule_id)

    def update_rule(self, rule_id: str, data: AlertRuleCreate) -> Optional[AlertRule]:
        existing = self._rules.get(rule_id)
        if not existing:
            return None
        updated = AlertRule(
            id=rule_id,
            name=data.name,
            metric=data.metric,
            condition=data.condition,
            threshold=data.threshold,
            enabled=data.enabled,
            notification_channels=data.notification_channels,
            cooldown_minutes=data.cooldown_minutes,
            last_triggered=existing.last_triggered,
        )
        self._rules[rule_id] = updated
        logger.info(f"Alert rule updated: {updated.name} ({rule_id})")
        return updated

    def delete_rule(self, rule_id: str) -> bool:
        if rule_id in self._rules:
            del self._rules[rule_id]
            logger.info(f"Alert rule deleted: {rule_id}")
            return True
        return False

    def check_rules(self, current_metrics: dict) -> List[AlertEvent]:
        triggered = []
        now = datetime.now(timezone.utc)

        for rule in self._rules.values():
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
                alert = self.trigger_alert(rule, actual_value)
                triggered.append(alert)

        return triggered

    def trigger_alert(self, rule: AlertRule, actual_value: float) -> AlertEvent:
        now = datetime.now(timezone.utc)
        alert = AlertEvent(
            id=str(uuid.uuid4()),
            rule_id=rule.id,
            rule_name=rule.name,
            metric=rule.metric,
            actual_value=actual_value,
            threshold=rule.threshold,
            triggered_at=now,
            acknowledged=False,
            acknowledged_by=None,
        )

        self._events.insert(0, alert)
        if len(self._events) > self._events_max:
            self._events.pop()

        rule.last_triggered = now
        logger.warning(
            f"ALERT triggered: {rule.name} | metric={rule.metric} "
            f"value={actual_value} threshold={rule.threshold} condition={rule.condition}"
        )

        if "log" in rule.notification_channels:
            self._log_alert(alert)

        if "email" in rule.notification_channels:
            email_service.send_alert_notification(alert.model_dump())

        return alert

    def _log_alert(self, alert: AlertEvent):
        logger.info(f"Alert notification logged: {alert.rule_name} - {alert.metric}={alert.actual_value}")

    def acknowledge_alert(self, alert_id: str, user: Optional[str] = None) -> Optional[AlertEvent]:
        for alert in self._events:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = user
                logger.info(f"Alert {alert_id} acknowledged by {user}")
                return alert
        return None

    def list_alerts(self, limit: int = 50) -> List[AlertEvent]:
        return self._events[:limit]

    def get_alert_stats(self) -> AlertStats:
        total = len(self._events)
        active = sum(1 for e in self._events if not e.acknowledged)
        acknowledged = sum(1 for e in self._events if e.acknowledged)

        by_severity: Dict[str, int] = {"critical": 0, "warning": 0, "info": 0}
        for e in self._events:
            if not e.acknowledged:
                val = e.actual_value
                ratio = abs(val - e.threshold) / max(abs(e.threshold), 1) if e.threshold else 0
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
