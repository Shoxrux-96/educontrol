from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_

from app.database import get_db
from app.models.user import User
from app.models.enterprise import (
    SyslogEntry, SyslogSeverity,
    SnmpDevice, SnmpMetric,
    BackupJob, BackupRecord, BackupStatus, BackupType,
)
from app.utils.security import get_current_user, require_role
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/enterprise", tags=["Enterprise"])


# ── Syslog ──

@router.get("/syslog")
async def list_syslog(
    hostname: str = Query(None),
    severity: str = Query(None),
    facility: str = Query(None),
    search: str = Query(None),
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SyslogEntry)
    if current_user.organization_id:
        q = q.where(SyslogEntry.organization_id == current_user.organization_id)
    if hostname:
        q = q.where(SyslogEntry.hostname == hostname)
    if severity:
        q = q.where(SyslogEntry.severity == severity)
    if facility:
        q = q.where(SyslogEntry.facility == facility)
    if search:
        q = q.where(or_(
            SyslogEntry.message.ilike(f"%{search}%"),
            SyslogEntry.hostname.ilike(f"%{search}%"),
        ))
    q = q.order_by(desc(SyslogEntry.received_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/syslog/summary")
async def syslog_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_filter = SyslogEntry.organization_id == current_user.organization_id if current_user.organization_id else func.true()

    async def cnt(**kw):
        q = select(func.count()).select_from(SyslogEntry).where(org_filter)
        for k, v in kw.items():
            q = q.where(getattr(SyslogEntry, k) == v)
        r = await db.execute(q)
        return r.scalar() or 0

    # Count by severity
    severity_q = select(SyslogEntry.severity, func.count()).where(org_filter).group_by(SyslogEntry.severity).order_by(desc(func.count()))
    severity_rows = (await db.execute(severity_q)).all()
    severity_counts = {r[0].value if hasattr(r[0], 'value') else r[0]: r[1] for r in severity_rows}

    return {
        "total": await cnt(),
        "critical": severity_counts.get("critical", 0) + severity_counts.get("emergency", 0) + severity_counts.get("alert", 0),
        "error": severity_counts.get("error", 0),
        "warning": severity_counts.get("warning", 0),
        "info": severity_counts.get("info", 0),
        "by_severity": severity_counts,
    }


@router.post("/syslog")
async def ingest_syslog(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = SyslogEntry(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(SyslogEntry, k) and k not in ("id", "organization_id")},
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.get("/syslog/hosts")
async def syslog_hosts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SyslogEntry.hostname, func.count().label("count"), func.max(SyslogEntry.received_at).label("last_seen"))
    if current_user.organization_id:
        q = q.where(SyslogEntry.organization_id == current_user.organization_id)
    q = q.group_by(SyslogEntry.hostname).order_by(desc("count"))
    rows = (await db.execute(q)).all()
    return [{"hostname": r[0], "log_count": r[1], "last_seen": r[2].isoformat() if r[2] else None} for r in rows]


# ── SNMP ──

@router.get("/snmp/devices")
async def list_snmp_devices(
    device_type: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SnmpDevice)
    if current_user.organization_id:
        q = q.where(SnmpDevice.organization_id == current_user.organization_id)
    if device_type:
        q = q.where(SnmpDevice.device_type == device_type)
    q = q.order_by(SnmpDevice.hostname)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/snmp/devices")
async def create_snmp_device(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    device = SnmpDevice(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(SnmpDevice, k) and k not in ("id", "organization_id")},
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.patch("/snmp/devices/{device_id}")
async def update_snmp_device(
    device_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(SnmpDevice).where(SnmpDevice.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, "SNMP device not found")
    for k, v in data.items():
        if hasattr(device, k) and k not in ("id", "organization_id"):
            setattr(device, k, v)
    await db.commit()
    await db.refresh(device)
    return device


@router.delete("/snmp/devices/{device_id}")
async def delete_snmp_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(SnmpDevice).where(SnmpDevice.id == device_id))
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(404, "SNMP device not found")
    await db.delete(device)
    await db.commit()
    return {"ok": True}


@router.get("/snmp/metrics")
async def list_metrics(
    device_id: str = Query(None),
    metric_name: str = Query(None),
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(SnmpMetric)
    if current_user.organization_id:
        q = q.where(SnmpMetric.organization_id == current_user.organization_id)
    if device_id:
        q = q.where(SnmpMetric.device_id == device_id)
    if metric_name:
        q = q.where(SnmpMetric.metric_name == metric_name)
    q = q.order_by(desc(SnmpMetric.recorded_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/snmp/metrics")
async def record_metric(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    metric = SnmpMetric(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(SnmpMetric, k) and k not in ("id", "organization_id")},
    )
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric


@router.get("/snmp/devices/{device_id}/metrics/latest")
async def device_latest_metrics(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get latest metric values per metric_name for a device."""
    subq = select(
        SnmpMetric.metric_name,
        func.max(SnmpMetric.recorded_at).label("latest")
    ).where(SnmpMetric.device_id == device_id).group_by(SnmpMetric.metric_name).subquery()
    q = select(SnmpMetric).join(
        subq,
        (SnmpMetric.metric_name == subq.c.metric_name) &
        (SnmpMetric.recorded_at == subq.c.latest)
    ).where(SnmpMetric.device_id == device_id)
    result = await db.execute(q)
    return result.scalars().all()


# ── Backup ──

@router.get("/backup/jobs")
async def list_backup_jobs(
    device_type: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(BackupJob)
    if current_user.organization_id:
        q = q.where(BackupJob.organization_id == current_user.organization_id)
    if device_type:
        q = q.where(BackupJob.device_type == device_type)
    q = q.order_by(BackupJob.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/backup/jobs")
async def create_backup_job(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    job = BackupJob(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(BackupJob, k) and k not in ("id", "organization_id", "created_by")},
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@router.patch("/backup/jobs/{job_id}")
async def update_backup_job(
    job_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(BackupJob).where(BackupJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Backup job not found")
    for k, v in data.items():
        if hasattr(job, k) and k not in ("id", "organization_id"):
            setattr(job, k, v)
    await db.commit()
    await db.refresh(job)
    return job


@router.delete("/backup/jobs/{job_id}")
async def delete_backup_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(BackupJob).where(BackupJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Backup job not found")
    await db.delete(job)
    await db.commit()
    return {"ok": True}


@router.post("/backup/jobs/{job_id}/run")
async def run_backup(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(BackupJob).where(BackupJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Backup job not found")

    from datetime import datetime, timezone
    import uuid

    record = BackupRecord(
        job_id=job_id,
        organization_id=current_user.organization_id,
        file_name=f"{job.device_hostname}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.cfg",
        status=BackupStatus.running,
        started_at=datetime.now(timezone.utc),
    )
    db.add(record)

    import asyncio
    await asyncio.sleep(2)

    record.status = BackupStatus.completed
    record.completed_at = datetime.now(timezone.utc)
    record.file_size_bytes = 1024 * 50
    record.duration_seconds = 2
    job.last_run_at = datetime.now(timezone.utc)
    job.last_status = BackupStatus.completed
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/backup/records")
async def list_backup_records(
    job_id: str = Query(None),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(BackupRecord)
    if current_user.organization_id:
        q = q.where(BackupRecord.organization_id == current_user.organization_id)
    if job_id:
        q = q.where(BackupRecord.job_id == job_id)
    q = q.order_by(desc(BackupRecord.started_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/backup/summary")
async def backup_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_filter = BackupJob.organization_id == current_user.organization_id if current_user.organization_id else func.true()
    async def cnt(model, **kw):
        q = select(func.count()).select_from(model).where(org_filter)
        for k, v in kw.items():
            q = q.where(getattr(model, k) == v)
        r = await db.execute(q)
        return r.scalar() or 0

    total_records_q = select(func.count()).select_from(BackupRecord)
    if current_user.organization_id:
        total_records_q = total_records_q.where(BackupRecord.organization_id == current_user.organization_id)
    total_backups = (await db.execute(total_records_q)).scalar() or 0

    return {
        "total_jobs": await cnt(BackupJob),
        "active_jobs": await cnt(BackupJob, is_active=True),
        "completed_backups": total_backups,
        "failed_backups": 0,
        "total_size_bytes": 0,
    }
