from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.database import get_db
from app.models.user import User
from app.models.internet_rule import InternetRule, InternetRuleAction, InternetRuleTarget, InternetCategory
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/internet", tags=["Internet"])


@router.get("/rules")
async def list_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(InternetRule)
    if current_user.organization_id:
        query = query.where(InternetRule.organization_id == current_user.organization_id)
    query = query.order_by(InternetRule.priority, InternetRule.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/rules")
async def create_rule(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = InternetRule(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(InternetRule, k) and k not in ("id", "organization_id", "created_by")},
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.patch("/rules/{rule_id}")
async def update_rule(
    rule_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(InternetRule).where(InternetRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Rule not found")
    for k, v in data.items():
        if hasattr(rule, k) and k not in ("id", "organization_id"):
            setattr(rule, k, v)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(InternetRule).where(InternetRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Rule not found")
    await db.delete(rule)
    await db.commit()
    return {"ok": True}


@router.get("/traffic/summary")
async def traffic_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.traffic_log import TrafficLog
    from datetime import datetime, timezone, timedelta
    query = select(
        func.sum(TrafficLog.bytes_total).label("total"),
        func.sum(TrafficLog.bytes_sent).label("sent"),
        func.sum(TrafficLog.bytes_received).label("received"),
        func.count().label("connections"),
    )
    if current_user.organization_id:
        query = query.where(TrafficLog.organization_id == current_user.organization_id)
    result = await db.execute(query)
    row = result.one()

    active_q = select(func.count())
    if current_user.organization_id:
        active_q = active_q.where(TrafficLog.organization_id == current_user.organization_id)
    active_q = active_q.where(TrafficLog.logged_at >= datetime.now(timezone.utc) - timedelta(minutes=5))
    active_row = (await db.execute(active_q)).scalar() or 0

    return {
        "total_bytes": row.total or 0,
        "bytes_sent": row.sent or 0,
        "bytes_received": row.received or 0,
        "total_connections": row.connections or 0,
        "active_connections": active_row,
        "total_uploaded": row.sent or 0,
        "total_downloaded": row.received or 0,
    }


@router.get("/traffic/top-users")
async def top_users(
    limit: int = Query(10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.traffic_log import TrafficLog
    from app.models.computer import Computer
    from app.models.user import User as UserModel
    query = select(
        TrafficLog.user_id,
        TrafficLog.computer_id,
        func.sum(TrafficLog.bytes_sent).label("sent"),
        func.sum(TrafficLog.bytes_received).label("received"),
        func.sum(TrafficLog.bytes_total).label("total"),
    )
    if current_user.organization_id:
        query = query.where(TrafficLog.organization_id == current_user.organization_id)
    query = query.group_by(TrafficLog.user_id, TrafficLog.computer_id).order_by(desc("total")).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    items = []
    for r in rows:
        username = "N/A"
        computer_name = "N/A"
        if r.user_id:
            u = await db.get(UserModel, r.user_id)
            if u:
                username = u.username or u.full_name or str(u.id)
        if r.computer_id:
            c = await db.get(Computer, r.computer_id)
            if c:
                computer_name = c.name or c.hostname or str(c.id)
        items.append({
            "username": username,
            "computer_name": computer_name,
            "uploaded": r.sent or 0,
            "downloaded": r.received or 0,
            "total": r.total or 0,
        })
    return items


@router.get("/traffic/realtime")
async def realtime_traffic(
    minutes: int = Query(5),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models.traffic_log import TrafficLog
    from app.models.computer import Computer
    from datetime import datetime, timezone, timedelta
    since = datetime.now(timezone.utc) - timedelta(minutes=minutes)
    query = select(TrafficLog, Computer.name.label("computer_name"), Computer.ip_address.label("source_ip")).outerjoin(
        Computer, TrafficLog.computer_id == Computer.id
    )
    if current_user.organization_id:
        query = query.where(TrafficLog.organization_id == current_user.organization_id)
    query = query.where(TrafficLog.logged_at >= since).order_by(desc(TrafficLog.logged_at)).limit(limit)
    result = await db.execute(query)
    rows = result.all()
    return [
        {
            "id": str(r.TrafficLog.id),
            "computer_name": r.computer_name or "N/A",
            "source_ip": r.source_ip or "N/A",
            "destination": r.TrafficLog.destination_host or r.TrafficLog.destination_ip or "N/A",
            "bytes_sent": r.TrafficLog.bytes_sent,
            "bytes_received": r.TrafficLog.bytes_received,
            "protocol": r.TrafficLog.protocol or "N/A",
            "timestamp": r.TrafficLog.logged_at.isoformat() if r.TrafficLog.logged_at else None,
        }
        for r in rows
    ]
