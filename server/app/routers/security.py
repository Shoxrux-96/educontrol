from fastapi import APIRouter, Depends, HTTPException, Query
import enum
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_, case, distinct
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models.user import User
from app.models.computer import Computer
from app.models.security import (
    UsbEvent, AntivirusStatus, ThreatDetection, ThreatType, ThreatSeverity,
    LoginAudit, LoginResult, SecurityPolicy,
)
from app.utils.security import get_current_user, require_role
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/security", tags=["Security"])


# ── Dashboard Summary ──

@router.get("/summary")
async def security_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_filter = {"organization_id": current_user.organization_id} if current_user.organization_id else {}

    async def count(model, **kw):
        q = select(func.count()).select_from(model)
        if org_filter:
            q = q.where(model.organization_id == current_user.organization_id)
        for k, v in kw.items():
            q = q.where(getattr(model, k) == v)
        r = await db.execute(q)
        return r.scalar() or 0

    return {
        "total_usb_events": await count(UsbEvent),
        "usb_blocked": await count(UsbEvent, blocked=True),
        "total_threats": await count(ThreatDetection),
        "critical_threats": await count(ThreatDetection, severity=ThreatSeverity.critical),
        "unresolved_threats": await count(ThreatDetection, is_cleaned=False, is_quarantined=False),
        "computers_without_av": await count(AntivirusStatus, is_installed=False),
        "av_outdated": await count(AntivirusStatus, definitions_up_to_date=False),
        "failed_logins": await count(LoginAudit, result=LoginResult.failed),
        "recent_logins": await count(LoginAudit, result=LoginResult.success),
    }


# ── USB Events ──

from sqlalchemy.orm import joinedload

def _usb_to_dict(event: UsbEvent) -> dict:
    return {
        "id": str(event.id),
        "device_name": event.device_name,
        "device_label": event.device_label,
        "action": event.action,
        "vendor": event.vendor_name,
        "serial": event.serial_number,
        "capacity": f"{event.capacity_mb} MB" if event.capacity_mb else None,
        "filesystem": event.filesystem,
        "computer_name": event.computer.name if event.computer else None,
        "computer_id": str(event.computer_id) if event.computer_id else None,
        "username": event.username,
        "blocked": event.blocked,
        "detected_at": event.detected_at.isoformat() if event.detected_at else None,
    }


@router.get("/usb")
async def list_usb_events(
    computer_id: str = Query(None),
    search: str = Query(None),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(UsbEvent).options(joinedload(UsbEvent.computer))
    if current_user.organization_id:
        q = q.where(UsbEvent.organization_id == current_user.organization_id)
    if computer_id:
        q = q.where(UsbEvent.computer_id == computer_id)
    if search:
        q = q.where(or_(
            UsbEvent.device_name.ilike(f"%{search}%"),
            UsbEvent.device_label.ilike(f"%{search}%"),
            UsbEvent.username.ilike(f"%{search}%"),
        ))
    q = q.order_by(desc(UsbEvent.detected_at)).limit(limit)
    result = await db.execute(q)
    return {"items": [_usb_to_dict(e) for e in result.unique().scalars().all()]}


@router.post("/usb")
async def record_usb_event(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    event = UsbEvent(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(UsbEvent, k) and k not in ("id", "organization_id")},
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return _usb_to_dict(event)


@router.get("/usb/stats")
async def usb_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func as sa_func

    org_filter = UsbEvent.organization_id == current_user.organization_id if current_user.organization_id else sa.true()

    total_q = select(sa_func.count()).select_from(UsbEvent).where(org_filter)
    blocked_q = select(sa_func.count()).select_from(UsbEvent).where(org_filter, UsbEvent.blocked == True)
    unique_q = select(sa_func.count(distinct(UsbEvent.serial_number))).select_from(UsbEvent).where(org_filter, UsbEvent.serial_number.isnot(None))
    latest_q = select(sa_func.max(UsbEvent.detected_at)).select_from(UsbEvent).where(org_filter)

    total = (await db.execute(total_q)).scalar() or 0
    blocked = (await db.execute(blocked_q)).scalar() or 0
    unique = (await db.execute(unique_q)).scalar() or 0
    latest = (await db.execute(latest_q)).scalar()

    return {
        "total_events": total,
        "blocked_count": blocked,
        "unique_devices": unique,
        "latest_event_time": latest.isoformat() if latest else None,
    }


@router.get("/usb/history/daily")
async def usb_daily_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(
        func.date_trunc("day", UsbEvent.detected_at).label("day"),
        func.count().label("count"),
    )
    if current_user.organization_id:
        q = q.where(UsbEvent.organization_id == current_user.organization_id)
    q = q.group_by(sa.text("day")).order_by(sa.text("day ASC")).limit(30)
    result = await db.execute(q)
    return [{"date": str(r.day), "count": r.count} for r in result]


@router.post("/usb/{event_id}/block")
async def toggle_usb_block(
    event_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(UsbEvent).where(UsbEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(404, "USB event not found")
    event.blocked = data.get("blocked", not event.blocked)
    await db.commit()
    await db.refresh(event)
    return _usb_to_dict(event)


# ── Antivirus ──

@router.get("/antivirus")
async def list_antivirus_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(AntivirusStatus)
    if current_user.organization_id:
        q = q.where(AntivirusStatus.organization_id == current_user.organization_id)
    q = q.order_by(AntivirusStatus.status_updated_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/antivirus/summary")
async def antivirus_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_filter = AntivirusStatus.organization_id == current_user.organization_id if current_user.organization_id else sa.true()

    async def cnt(**kw):
        q = select(func.count()).select_from(AntivirusStatus).where(org_filter)
        for k, v in kw.items():
            q = q.where(getattr(AntivirusStatus, k) == v)
        r = await db.execute(q)
        return r.scalar() or 0

    return {
        "total": await cnt(),
        "protected": await cnt(is_running=True, definitions_up_to_date=True),
        "no_av": await cnt(is_installed=False),
        "outdated": await cnt(definitions_up_to_date=False, is_installed=True),
        "realtime_off": await cnt(realtime_protection=False, is_installed=True),
        "requires_restart": await cnt(requires_restart=True),
    }


@router.post("/antivirus")
async def update_antivirus_status(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    computer_id = data.get("computer_id")
    if not computer_id:
        raise HTTPException(400, "computer_id required")
    existing = await db.execute(
        select(AntivirusStatus).where(AntivirusStatus.computer_id == computer_id)
    )
    status = existing.scalar_one_or_none()
    if status:
        for k, v in data.items():
            if hasattr(status, k) and k not in ("id", "organization_id"):
                setattr(status, k, v)
    else:
        status = AntivirusStatus(
            organization_id=current_user.organization_id,
            **{k: v for k, v in data.items() if hasattr(AntivirusStatus, k) and k not in ("id", "organization_id")},
        )
        db.add(status)
    await db.commit()
    await db.refresh(status)
    return status


# ── Threats ──

@router.get("/threats")
async def list_threats(
    severity: str = Query(None),
    threat_type: str = Query(None),
    resolved: bool = Query(None),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ThreatDetection)
    if current_user.organization_id:
        q = q.where(ThreatDetection.organization_id == current_user.organization_id)
    if severity:
        q = q.where(ThreatDetection.severity == severity)
    if threat_type:
        q = q.where(ThreatDetection.threat_type == threat_type)
    if resolved is not None:
        q = q.where(ThreatDetection.is_cleaned == resolved)
    q = q.order_by(desc(ThreatDetection.detected_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/threats/stats")
async def threat_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_filter = ThreatDetection.organization_id == current_user.organization_id if current_user.organization_id else sa.true()
    q = select(
        ThreatDetection.threat_type,
        func.count().label("count"),
    ).where(org_filter).group_by(ThreatDetection.threat_type).order_by(desc("count"))
    result = await db.execute(q)
    return [{"type": r[0].value if hasattr(r[0], 'value') else r[0], "count": r[1]} for r in result]


@router.patch("/threats/{threat_id}/resolve")
async def resolve_threat(
    threat_id: str,
    data: dict = {},
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(ThreatDetection).where(ThreatDetection.id == threat_id))
    threat = result.scalar_one_or_none()
    if not threat:
        raise HTTPException(404, "Threat not found")
    threat.is_cleaned = data.get("is_cleaned", True)
    threat.is_quarantined = data.get("is_quarantined", False)
    threat.resolved_at = datetime.now(timezone.utc)
    threat.resolved_by = current_user.id
    threat.action_taken = data.get("action_taken", "manual_resolve")
    await db.commit()
    await db.refresh(threat)
    return threat


@router.post("/threats")
async def report_threat(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    threat = ThreatDetection(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(ThreatDetection, k) and k not in ("id", "organization_id", "resolved_by")},
    )
    db.add(threat)
    await db.commit()
    await db.refresh(threat)
    return threat


# ── Login Audit ──

@router.get("/logins")
async def list_login_audits(
    username: str = Query(None),
    result_filter: str = Query(None, alias="result"),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(LoginAudit)
    if current_user.organization_id:
        q = q.where(LoginAudit.organization_id == current_user.organization_id)
    if username:
        q = q.where(LoginAudit.username.ilike(f"%{username}%"))
    if result_filter:
        q = q.where(LoginAudit.result == result_filter)
    q = q.order_by(desc(LoginAudit.logged_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/logins/summary")
async def login_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import case
    org_filter = LoginAudit.organization_id == current_user.organization_id if current_user.organization_id else sa.true()
    q = select(
        func.count().label("total"),
        func.sum(case((LoginAudit.result == "success", 1), else_=0)).label("success"),
        func.sum(case((LoginAudit.result == "failed", 1), else_=0)).label("failed"),
        func.sum(case((LoginAudit.result == "locked", 1), else_=0)).label("locked"),
    ).where(org_filter)
    r = (await db.execute(q)).one()
    return {"total": r.total or 0, "success": r.success or 0, "failed": r.failed or 0, "locked": r.locked or 0}


@router.post("/logins")
async def record_login(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    audit = LoginAudit(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        **{k: v for k, v in data.items() if hasattr(LoginAudit, k) and k not in ("id", "organization_id", "user_id")},
    )
    db.add(audit)
    await db.commit()
    await db.refresh(audit)
    return audit


# ── Security Policies ──

@router.get("/policies")
async def get_policies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SecurityPolicy).where(SecurityPolicy.organization_id == current_user.organization_id)
    result = await db.execute(q)
    policies = result.scalar_one_or_none()
    if not policies:
        return {}
    return policies


@router.post("/policies")
async def save_policies(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("owner")),
):
    q = select(SecurityPolicy).where(SecurityPolicy.organization_id == current_user.organization_id)
    result = await db.execute(q)
    policies = result.scalar_one_or_none()
    if policies:
        for k, v in data.items():
            if hasattr(policies, k) and k not in ("id", "organization_id", "created_at"):
                setattr(policies, k, v)
    else:
        policies = SecurityPolicy(
            organization_id=current_user.organization_id,
            **{k: v for k, v in data.items() if hasattr(SecurityPolicy, k) and k not in ("id", "organization_id")},
        )
        db.add(policies)
    await db.commit()
    await db.refresh(policies)
    return policies
