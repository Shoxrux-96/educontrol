from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_

from app.database import get_db
from app.models.user import User
from app.models.computer import Computer
from app.models.computer_management import (
    RemoteSession, RemoteSessionStatus,
    SoftwareInventoryItem, SoftwarePackage, SoftwareDeployment, DeploymentStatus,
)
from app.models.command import Command
from app.utils.security import get_current_user, require_role
from app.websocket.manager import manager
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/computers", tags=["Computer Management"])


def _serialize_deployment(d: SoftwareDeployment) -> dict:
    pkg_name = d.package.name if d.package else "Noma'lum"
    return {
        "id": str(d.id),
        "organization_id": str(d.organization_id) if d.organization_id else None,
        "package_id": str(d.package_id) if d.package_id else None,
        "package_name": pkg_name,
        "name": d.name,
        "target_type": d.target_type,
        "target_ids": d.target_ids if isinstance(d.target_ids, list) else [],
        "status": d.status.value if hasattr(d.status, "value") else d.status,
        "total_computers": d.total_computers,
        "completed_computers": d.completed_computers,
        "failed_computers": d.failed_computers,
        "created_by": str(d.created_by) if d.created_by else None,
        "started_at": d.started_at.isoformat() if d.started_at else None,
        "completed_at": d.completed_at.isoformat() if d.completed_at else None,
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


# ── Remote Desktop ──

@router.post("/{computer_id}/remote/start")
async def start_remote_session(
    computer_id: str,
    data: dict = {},
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    comp = await db.get(Computer, computer_id)
    if not comp:
        raise HTTPException(404, "Computer not found")

    session = RemoteSession(
        organization_id=current_user.organization_id or comp.organization_id,
        computer_id=computer_id,
        user_id=current_user.id,
        protocol=data.get("protocol", "vnc"),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    await manager.send_to_computer(computer_id, {
        "type": "remote_session",
        "action": "start",
        "session_id": str(session.id),
        "protocol": session.protocol,
    })

    return {
        "id": str(session.id),
        "computer_id": computer_id,
        "status": session.status.value,
        "protocol": session.protocol,
    }


@router.post("/remote/{session_id}/stop")
async def stop_remote_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(RemoteSession).where(RemoteSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, "Session not found")
    session.status = RemoteSessionStatus.closed
    session.ended_at = datetime.now(timezone.utc)
    await db.commit()

    await manager.send_to_computer(str(session.computer_id), {
        "type": "remote_session",
        "action": "stop",
        "session_id": session_id,
    })

    return {"ok": True}


@router.get("/remote/active")
async def list_active_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(RemoteSession).where(RemoteSession.status == RemoteSessionStatus.active.value)
    if current_user.organization_id:
        q = q.where(RemoteSession.organization_id == current_user.organization_id)
    q = q.order_by(desc(RemoteSession.started_at))
    result = await db.execute(q)
    return [{
        "id": str(s.id),
        "computer_id": str(s.computer_id),
        "user_id": str(s.user_id),
        "status": s.status,
        "protocol": s.protocol,
        "started_at": s.started_at.isoformat() if s.started_at else None,
        "ended_at": s.ended_at.isoformat() if s.ended_at else None,
        "last_activity": s.last_activity.isoformat() if s.last_activity else None,
    } for s in result.scalars().all()]


@router.post("/{computer_id}/remote/input")
async def send_remote_input(
    computer_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    input_type = data.get("type", "keyboard")
    await manager.send_to_computer(computer_id, {
        "type": "remote_input",
        "input_type": input_type,
        "data": data.get("data", {}),
    })
    return {"ok": True}


@router.post("/{computer_id}/remote/screenshot")
async def request_screenshot(
    computer_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    await manager.send_to_computer(computer_id, {
        "type": "remote_session",
        "action": "screenshot",
    })
    return {"ok": True, "message": "Screenshot so'rovi yuborildi"}


# ── Power Management ──

@router.post("/{computer_id}/power")
async def power_action(
    computer_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    action = data.get("action", "")
    if action not in ("shutdown", "restart", "sleep", "wake"):
        raise HTTPException(400, "Invalid power action. Use: shutdown, restart, sleep, wake")

    comp = await db.get(Computer, computer_id)
    if not comp:
        raise HTTPException(404, "Computer not found")

    if action == "wake":
        if not comp.mac_address:
            raise HTTPException(400, "MAC address required for Wake-on-LAN")
        return await _send_wol(comp.mac_address, comp.ip_address, db, current_user)

    ws_msg = {
        "type": "command",
        "action": "power",
        "payload": {"action": action},
        "computer_id": computer_id,
    }
    await manager.send_to_computer(computer_id, ws_msg)

    command = Command(
        organization_id=current_user.organization_id or comp.organization_id,
        computer_id=computer_id,
        command_type="power",
        payload={"action": action},
        sent_by=current_user.id,
    )
    db.add(command)
    await db.commit()

    return {"ok": True, "action": action, "computer_id": computer_id}


async def _send_wol(mac: str, ip: str, db, current_user):
    """Send Wake-on-LAN magic packet (simulated)."""
    return {
        "ok": True,
        "action": "wake",
        "mac_address": mac,
        "message": f"Wake-on-LAN paketi {mac} ({ip}) ga yuborildi",
    }


@router.post("/power/bulk")
async def bulk_power_action(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    action = data.get("action", "")
    computer_ids = data.get("computer_ids", [])
    if not computer_ids:
        raise HTTPException(400, "computer_ids required")
    results = []
    for cid in computer_ids:
        try:
            comp = await db.get(Computer, cid)
            if not comp:
                results.append({"computer_id": cid, "status": "error", "message": "Not found"})
                continue
            if action == "wake" and comp.mac_address:
                await _send_wol(comp.mac_address, comp.ip_address, db, current_user)
            elif action != "wake":
                await manager.send_to_computer(cid, {"type": "command", "action": "power", "payload": {"action": action}})
                cmd = Command(
                    organization_id=current_user.organization_id or comp.organization_id,
                    computer_id=cid, command_type="power", payload={"action": action}, sent_by=current_user.id,
                )
                db.add(cmd)
            results.append({"computer_id": cid, "status": "sent"})
        except Exception as e:
            results.append({"computer_id": cid, "status": "error", "message": str(e)})
    await db.commit()
    return {"action": action, "total": len(computer_ids), "results": results}


# ── Software Inventory ──

@router.get("/{computer_id}/software")
async def list_software(
    computer_id: str,
    search: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SoftwareInventoryItem).where(SoftwareInventoryItem.computer_id == computer_id)
    if search:
        q = q.where(SoftwareInventoryItem.name.ilike(f"%{search}%"))
    q = q.order_by(SoftwareInventoryItem.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/{computer_id}/software/sync")
async def sync_software_inventory(
    computer_id: str,
    data: dict,
    current_user: User = Depends(require_role("admin", "owner")),
):
    """Request agent to scan and report installed software."""
    await manager.send_to_computer(computer_id, {
        "type": "command",
        "action": "software_scan",
        "payload": {},
    })
    return {"ok": True, "message": "Dasturiy ta'minot skanerlash so'rovi yuborildi"}


@router.get("/software/search")
async def search_software(
    q: str = Query(""),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(SoftwareInventoryItem.name, func.count().label("count"))
    if current_user.organization_id:
        query = query.where(SoftwareInventoryItem.organization_id == current_user.organization_id)
    if q:
        query = query.where(SoftwareInventoryItem.name.ilike(f"%{q}%"))
    query = query.group_by(SoftwareInventoryItem.name).order_by(desc("count")).limit(50)
    result = await db.execute(query)
    return [{"name": r[0], "computers": r[1]} for r in result]


# ── Software Packages ──

@router.get("/software/packages")
async def list_packages(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SoftwarePackage)
    if current_user.organization_id:
        q = q.where(SoftwarePackage.organization_id == current_user.organization_id)
    q = q.order_by(SoftwarePackage.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/software/packages")
async def create_package(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    pkg = SoftwarePackage(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(SoftwarePackage, k) and k not in ("id", "organization_id", "created_by")},
    )
    db.add(pkg)
    await db.commit()
    await db.refresh(pkg)
    return pkg


@router.patch("/software/packages/{package_id}")
async def update_package(
    package_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(SoftwarePackage).where(SoftwarePackage.id == package_id))
    pkg = result.scalar_one_or_none()
    if not pkg:
        raise HTTPException(404, "Package not found")
    for k, v in data.items():
        if hasattr(pkg, k) and k not in ("id", "organization_id"):
            setattr(pkg, k, v)
    await db.commit()
    await db.refresh(pkg)
    return pkg


# ── Software Deployment ──

@router.get("/deployments")
async def list_deployments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SoftwareDeployment)
    if current_user.organization_id:
        q = q.where(SoftwareDeployment.organization_id == current_user.organization_id)
    q = q.order_by(desc(SoftwareDeployment.created_at))
    result = await db.execute(q)
    return [_serialize_deployment(d) for d in result.scalars().all()]


@router.post("/deployments")
async def create_deployment(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    pkg_id = data.get("package_id")
    if pkg_id:
        pkg = await db.get(SoftwarePackage, pkg_id)
        if not pkg:
            raise HTTPException(404, "Package not found")

    target_type = data.get("target_type", "computer")
    target_ids = data.get("target_ids", [])

    total = len(target_ids) if target_ids else 0

    deploy = SoftwareDeployment(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        package_id=pkg_id,
        name=data.get("name", "Deployment"),
        target_type=target_type,
        target_ids=target_ids or [],
        total_computers=total,
        status=DeploymentStatus.deploying,
        started_at=datetime.now(timezone.utc),
    )
    db.add(deploy)
    await db.commit()
    await db.refresh(deploy)

    action = data.get("action", "install")
    for cid in target_ids:
        await manager.send_to_computer(cid, {
            "type": "command",
            "action": "software_install" if action == "install" else "software_uninstall",
            "payload": {
                "package_id": str(pkg_id) if pkg_id else None,
                "package_name": data.get("name", ""),
                "installer_url": pkg.installer_url if pkg else None,
                "installer_args": pkg.installer_args if pkg else None,
            },
        })

    return _serialize_deployment(deploy)


@router.get("/deployments/{deployment_id}")
async def get_deployment(
    deployment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(SoftwareDeployment).where(SoftwareDeployment.id == deployment_id))
    deploy = result.scalar_one_or_none()
    if not deploy:
        raise HTTPException(404, "Deployment not found")
    return _serialize_deployment(deploy)
