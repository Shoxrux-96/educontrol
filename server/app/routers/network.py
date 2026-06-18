from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, or_

from app.database import get_db
from app.models.user import User
from app.models.network_device import NetworkDevice, IpLease, PingResult, BandwidthRecord, NetworkDeviceType
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/network", tags=["Network"])


def org_filter(query, org_id):
    return query.where(NetworkDevice.organization_id == org_id)


# ── Network Devices / Topology ──

@router.get("/devices")
async def list_devices(
    device_type: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(NetworkDevice)
    if current_user.organization_id:
        q = q.where(NetworkDevice.organization_id == current_user.organization_id)
    if device_type:
        q = q.where(NetworkDevice.device_type == device_type)
    q = q.order_by(NetworkDevice.device_type, NetworkDevice.hostname)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/devices")
async def create_device(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    device = NetworkDevice(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(NetworkDevice, k) and k not in ("id", "organization_id")},
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.patch("/devices/{device_id}")
async def update_device(
    device_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(NetworkDevice).where(NetworkDevice.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, "Device not found")
    for k, v in data.items():
        if hasattr(device, k) and k not in ("id", "organization_id"):
            setattr(device, k, v)
    await db.commit()
    await db.refresh(device)
    return device


@router.delete("/devices/{device_id}")
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(NetworkDevice).where(NetworkDevice.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, "Device not found")
    await db.delete(device)
    await db.commit()
    return {"ok": True}


@router.get("/topology")
async def get_topology(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return hierarchical topology: root devices first, then children nested."""
    q = select(NetworkDevice)
    if current_user.organization_id:
        q = q.where(NetworkDevice.organization_id == current_user.organization_id)
    result = await db.execute(q)
    devices = result.scalars().all()
    roots = [d for d in devices if d.parent_id is None]
    children = [d for d in devices if d.parent_id is not None]
    def build_tree(parent):
        return {
            "id": str(parent.id),
            "hostname": parent.hostname,
            "ip_address": parent.ip_address,
            "device_type": parent.device_type.value,
            "vendor": parent.vendor,
            "is_monitored": parent.is_monitored,
            "children": [build_tree(c) for c in children if c.parent_id == parent.id],
        }
    return [build_tree(r) for r in roots]


# ── IP Management ──

@router.get("/ip-addresses")
async def list_ip_addresses(
    search: str = None,
    conflict: bool = None,
    free: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if free:
        used = await db.execute(
            select(IpLease.ip_address).where(IpLease.organization_id == current_user.organization_id, IpLease.is_active == True)
        )
        used_ips = {row[0] for row in used}
        all_ips = [f"192.168.1.{i}" for i in range(1, 255)]
        free_ips = [ip for ip in all_ips if ip not in used_ips]
        return free_ips

    q = select(IpLease)
    if current_user.organization_id:
        q = q.where(IpLease.organization_id == current_user.organization_id)
    if search:
        q = q.where(or_(IpLease.ip_address.ilike(f"%{search}%"), IpLease.hostname.ilike(f"%{search}%"), IpLease.mac_address.ilike(f"%{search}%")))
    if conflict is not None:
        q = q.where(IpLease.conflict_detected == conflict)
    q = q.order_by(IpLease.ip_address)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/ip-addresses")
async def create_ip_lease(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    lease = IpLease(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(IpLease, k) and k not in ("id", "organization_id")},
    )
    db.add(lease)
    await db.commit()
    await db.refresh(lease)
    return lease


@router.patch("/ip-addresses/{lease_id}")
async def update_ip_lease(
    lease_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(IpLease).where(IpLease.id == lease_id))
    lease = result.scalar_one_or_none()
    if not lease:
        raise HTTPException(404, "IP lease not found")
    for k, v in data.items():
        if hasattr(lease, k) and k not in ("id", "organization_id"):
            setattr(lease, k, v)
    await db.commit()
    await db.refresh(lease)
    return lease


@router.get("/ip-addresses/conflicts")
async def list_conflicts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detect duplicate IPs across leases and devices."""
    q = select(IpLease).where(IpLease.conflict_detected == True)
    if current_user.organization_id:
        q = q.where(IpLease.organization_id == current_user.organization_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/ip-addresses/scan-conflicts")
async def scan_conflicts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Find duplicate IP assignments and mark conflicts."""
    from sqlalchemy import text
    raw = text("""
        SELECT ip_address, COUNT(*) as cnt
        FROM ip_leases
        WHERE organization_id = :org_id AND is_active = true
        GROUP BY ip_address
        HAVING COUNT(*) > 1
    """)
    result = await db.execute(raw, {"org_id": current_user.organization_id})
    conflicts_found = 0
    for row in result:
        ip = row[0]
        leases = await db.execute(
            select(IpLease).where(
                IpLease.organization_id == current_user.organization_id,
                IpLease.ip_address == ip,
                IpLease.is_active == True,
            )
        )
        all_leases = leases.scalars().all()
        if len(all_leases) > 1:
            conflicts_found += 1
            for lease in all_leases:
                lease.conflict_detected = True
                others = [str(l.ip_address) for l in all_leases if l.id != lease.id]
                lease.conflict_with = ", ".join(others)
    await db.commit()
    return {"conflicts_found": conflicts_found}


# ── Ping Monitoring ──

@router.get("/ping-results")
async def list_ping_results(
    device_id: str = None,
    limit: int = Query(50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(PingResult)
    if current_user.organization_id:
        q = q.where(PingResult.organization_id == current_user.organization_id)
    if device_id:
        q = q.where(PingResult.device_id == device_id)
    q = q.order_by(desc(PingResult.checked_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/ping-results")
async def create_ping_result(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ping = PingResult(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(PingResult, k) and k not in ("id", "organization_id")},
    )
    db.add(ping)
    await db.commit()
    await db.refresh(ping)
    return ping


@router.get("/ping-status")
async def ping_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Latest ping per monitored device."""
    subq = (
        select(
            PingResult.device_id,
            func.max(PingResult.checked_at).label("latest")
        )
        .where(PingResult.organization_id == current_user.organization_id)
        .group_by(PingResult.device_id)
        .subquery()
    )
    q = (
        select(PingResult, NetworkDevice.hostname)
        .join(subq, (PingResult.device_id == subq.c.device_id) & (PingResult.checked_at == subq.c.latest))
        .join(NetworkDevice, NetworkDevice.id == PingResult.device_id)
        .order_by(NetworkDevice.hostname)
    )
    result = await db.execute(q)
    return [
        {"device_id": str(r[0].device_id), "hostname": r[1], "is_alive": r[0].is_alive, "latency_ms": r[0].latency_ms, "packet_loss_pct": r[0].packet_loss_pct, "checked_at": r[0].checked_at.isoformat()}
        for r in result
    ]


# ── Bandwidth Monitoring ──

@router.get("/bandwidth")
async def list_bandwidth(
    device_id: str = None,
    limit: int = Query(200),
    since: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(BandwidthRecord)
    if current_user.organization_id:
        q = q.where(BandwidthRecord.organization_id == current_user.organization_id)
    if device_id:
        q = q.where(BandwidthRecord.device_id == device_id)
    if since:
        from datetime import datetime, timezone
        try:
            dt = datetime.fromisoformat(since)
            q = q.where(BandwidthRecord.recorded_at >= dt)
        except ValueError:
            pass
    q = q.order_by(BandwidthRecord.recorded_at.desc()).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/bandwidth")
async def create_bandwidth(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bw = BandwidthRecord(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(BandwidthRecord, k) and k not in ("id", "organization_id")},
    )
    db.add(bw)
    await db.commit()
    await db.refresh(bw)
    return bw


@router.get("/bandwidth/summary")
async def bandwidth_summary(
    device_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(
        func.avg(BandwidthRecord.bits_in_per_sec).label("avg_in"),
        func.avg(BandwidthRecord.bits_out_per_sec).label("avg_out"),
        func.max(BandwidthRecord.bits_in_per_sec).label("peak_in"),
        func.max(BandwidthRecord.bits_out_per_sec).label("peak_out"),
        func.avg(BandwidthRecord.utilization_pct).label("avg_util"),
    )
    if current_user.organization_id:
        q = q.where(BandwidthRecord.organization_id == current_user.organization_id)
    if device_id:
        q = q.where(BandwidthRecord.device_id == device_id)
    result = await db.execute(q)
    row = result.one()
    return {
        "avg_in_bps": round(row.avg_in or 0, 2),
        "avg_out_bps": round(row.avg_out or 0, 2),
        "peak_in_bps": round(row.peak_in or 0, 2),
        "peak_out_bps": round(row.peak_out or 0, 2),
        "avg_utilization_pct": round(row.avg_util or 0, 2),
    }
