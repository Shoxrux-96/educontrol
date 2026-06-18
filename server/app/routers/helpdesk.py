"""enhanced help desk: assign, status workflow, filters, stats, activity"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_

from app.database import get_db
from app.models.user import User
from app.models.helpdesk import HelpDeskTicket, TicketComment, TicketStatus
from app.utils.security import get_current_user, require_role
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/helpdesk", tags=["Help Desk"])


@router.get("/tickets")
async def list_tickets(
    status: str = Query(None),
    category: str = Query(None),
    priority: str = Query(None),
    search: str = Query(None),
    assigned_to: str = Query(None),
    created_by: str = Query(None),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(HelpDeskTicket)
    if current_user.organization_id:
        query = query.where(HelpDeskTicket.organization_id == current_user.organization_id)
    if status:
        query = query.where(HelpDeskTicket.status == status)
    if category:
        query = query.where(HelpDeskTicket.category == category)
    if priority:
        query = query.where(HelpDeskTicket.priority == priority)
    if search:
        query = query.where(or_(
            HelpDeskTicket.title.ilike(f"%{search}%"),
            HelpDeskTicket.description.ilike(f"%{search}%"),
        ))
    if assigned_to:
        query = query.where(HelpDeskTicket.assigned_to == assigned_to)
    if created_by:
        query = query.where(HelpDeskTicket.created_by == created_by)
    query = query.order_by(desc(HelpDeskTicket.created_at)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/tickets/stats")
async def ticket_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_filter = HelpDeskTicket.organization_id == current_user.organization_id if current_user.organization_id else func.true()
    async def cnt(**kw):
        q = select(func.count()).select_from(HelpDeskTicket).where(org_filter)
        for k, v in kw.items():
            q = q.where(getattr(HelpDeskTicket, k) == v)
        r = await db.execute(q)
        return r.scalar() or 0
    return {
        "total": await cnt(),
        "open": await cnt(status=TicketStatus.open),
        "in_progress": await cnt(status=TicketStatus.in_progress),
        "resolved": await cnt(status=TicketStatus.resolved),
        "closed": await cnt(status=TicketStatus.closed),
        "critical": await cnt(priority="critical"),
        "high": await cnt(priority="high"),
        "unassigned": await cnt(assigned_to=None, status=TicketStatus.open),
    }


@router.post("/tickets")
async def create_ticket(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = HelpDeskTicket(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(HelpDeskTicket, k) and k not in ("id", "organization_id", "created_by")},
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.get("/tickets/{ticket_id}")
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HelpDeskTicket).where(HelpDeskTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(HelpDeskTicket).where(HelpDeskTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(404, "Ticket not found")

    old_status = ticket.status
    new_status = data.get("status")
    if new_status and new_status != old_status.value:
        if new_status == "resolved" or new_status == "closed":
            data["resolved_at"] = datetime.now(timezone.utc)

    for k, v in data.items():
        if hasattr(ticket, k) and k not in ("id", "organization_id", "created_by"):
            setattr(ticket, k, v)
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(HelpDeskTicket).where(HelpDeskTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    assignee_id = data.get("assigned_to")
    ticket.assigned_to = assignee_id
    if assignee_id and ticket.status == TicketStatus.open:
        ticket.status = TicketStatus.in_progress
    await db.commit()
    await db.refresh(ticket)
    return ticket


@router.get("/tickets/{ticket_id}/comments")
async def list_comments(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(TicketComment)
        .where(TicketComment.ticket_id == ticket_id)
        .order_by(TicketComment.created_at)
    )
    return result.scalars().all()


@router.post("/tickets/{ticket_id}/comments")
async def add_comment(
    ticket_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(HelpDeskTicket).where(HelpDeskTicket.id == ticket_id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    comment = TicketComment(
        ticket_id=ticket_id,
        user_id=current_user.id,
        body=data.get("body", ""),
        is_internal=data.get("is_internal", False),
    )
    db.add(comment)
    ticket.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.get("/users")
async def list_helpdesk_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return IT staff users available for assignment."""
    q = select(User).where(User.organization_id == current_user.organization_id, User.is_active == True)
    q = q.order_by(User.full_name)
    result = await db.execute(q)
    users = result.scalars().all()
    return [{"id": str(u.id), "full_name": u.full_name or u.username, "role": u.role.value} for u in users]
