from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.firewall_rule import FirewallRule, FirewallAction, FirewallDirection, FirewallProtocol, FirewallMatchType
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/firewall", tags=["Firewall"])


@router.get("/rules")
async def list_rules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(FirewallRule)
    if current_user.organization_id:
        query = query.where(FirewallRule.organization_id == current_user.organization_id)
    query = query.order_by(FirewallRule.priority, FirewallRule.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/rules")
async def create_rule(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rule = FirewallRule(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(FirewallRule, k) and k not in ("id", "organization_id", "created_by")},
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
    result = await db.execute(select(FirewallRule).where(FirewallRule.id == rule_id))
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
    result = await db.execute(select(FirewallRule).where(FirewallRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(404, "Rule not found")
    await db.delete(rule)
    await db.commit()
    return {"ok": True}
