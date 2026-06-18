from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.user import User
from app.models.active_directory import DomainConfig, AdUser, AdGroup, AdOU, AdGpo, DomainSyncStatus
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/v1/ad", tags=["Active Directory"])


# ── Domain Configuration ──

@router.get("/config")
async def get_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(DomainConfig).where(DomainConfig.organization_id == current_user.organization_id)
    result = await db.execute(q)
    config = result.scalar_one_or_none()
    if not config:
        return {
            "domain_name": "",
            "domain_controller": "",
            "ldap_base_dn": "",
            "ldap_user": "",
            "ldap_password": "",
            "use_ssl": False,
            "sync_interval_minutes": 60,
            "sso_enabled": False,
            "auto_create_users": False,
            "default_role": "viewer",
        }
    return {
        "id": str(config.id),
        "domain_name": config.domain_name,
        "domain_controller": config.domain_controller,
        "ldap_base_dn": config.ldap_base_dn,
        "ldap_user": config.ldap_user or "",
        "ldap_password": config.ldap_password or "",
        "use_ssl": config.use_ssl,
        "sync_interval_minutes": config.sync_interval_minutes,
        "last_sync_at": config.last_sync_at.isoformat() if config.last_sync_at else None,
        "sync_status": getattr(config.sync_status, 'value', config.sync_status),
        "sso_enabled": config.sso_enabled,
        "auto_create_users": config.auto_create_users,
        "default_role": config.default_role,
        "is_active": config.is_active,
    }


@router.post("/config")
async def save_config(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(DomainConfig).where(DomainConfig.organization_id == current_user.organization_id)
    result = await db.execute(q)
    config = result.scalar_one_or_none()
    if config:
        for k, v in data.items():
            if hasattr(config, k) and k not in ("id", "organization_id", "created_at"):
                setattr(config, k, v)
    else:
        config = DomainConfig(
            organization_id=current_user.organization_id,
            **{k: v for k, v in data.items() if hasattr(DomainConfig, k) and k not in ("id", "organization_id")},
        )
        db.add(config)
    await db.commit()
    await db.refresh(config)
    return {"ok": True, "id": str(config.id)}


@router.post("/config/test")
async def test_connection(
    data: dict,
    current_user: User = Depends(get_current_user),
):
    """Simulate LDAP connection test (actual LDAP would use python-ldap)."""
    dc = data.get("domain_controller", "")
    domain = data.get("domain_name", "")
    success = bool(dc and domain)
    return {
        "success": success,
        "message": "Ulanish muvaffaqiyatli" if success else "Domain kontrollerga ulanishda xatolik",
        "domain": domain,
        "server": dc,
    }


@router.post("/config/sync")
async def sync_domain(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simulate AD sync (mock data for UI)."""
    from datetime import datetime, timezone
    q = select(DomainConfig).where(DomainConfig.organization_id == current_user.organization_id)
    result = await db.execute(q)
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(400, "Domain configuration not found")

    config.sync_status = DomainSyncStatus.syncing
    await db.commit()

    import uuid
    sample_ous = [
        {"name": "Kompyuterlar", "distinguished_name": "OU=Kompyuterlar," + config.ldap_base_dn, "user_count": 45, "computer_count": 45},
        {"name": "Foydalanuvchilar", "distinguished_name": "OU=Foydalanuvchilar," + config.ldap_base_dn, "user_count": 120, "computer_count": 0},
        {"name": "Serverlar", "distinguished_name": "OU=Serverlar," + config.ldap_base_dn, "user_count": 10, "computer_count": 5},
        {"name": "Administratorlar", "distinguished_name": "OU=Administratorlar," + config.ldap_base_dn, "user_count": 8, "computer_count": 8},
    ]
    for ou_data in sample_ous:
        existing = await db.execute(
            select(AdOU).where(AdOU.distinguished_name == ou_data["distinguished_name"])
        )
        if not existing.scalar_one_or_none():
            ou = AdOU(
                organization_id=current_user.organization_id,
                domain_config_id=config.id,
                **ou_data,
                is_synced=True,
            )
            db.add(ou)

    sample_users = [
        {"sam_account_name": "davron.admin", "display_name": "Davron Adminov", "email": "davron@school.local", "ou_dn": sample_ous[3]["distinguished_name"]},
        {"sam_account_name": "ali.teacher", "display_name": "Ali Ustozov", "email": "ali@school.local", "ou_dn": sample_ous[1]["distinguished_name"]},
        {"sam_account_name": "sardor.it", "display_name": "Sardor IT", "email": "sardor@school.local", "ou_dn": sample_ous[0]["distinguished_name"]},
    ]
    for u in sample_users:
        existing = await db.execute(
            select(AdUser).where(AdUser.sam_account_name == u["sam_account_name"])
        )
        if not existing.scalar_one_or_none():
            user = AdUser(
                organization_id=current_user.organization_id,
                domain_config_id=config.id,
                distinguished_name=f"CN={u['display_name']},{u['ou_dn']}",
                **u,
                enabled=True,
                is_synced=True,
                synced_at=datetime.now(timezone.utc),
            )
            db.add(user)

    sample_groups = [
        {"name": "Domain Admins", "sam_account_name": "Domain Admins", "distinguished_name": "CN=Domain Admins," + config.ldap_base_dn, "member_count": 5},
        {"name": "Domain Users", "sam_account_name": "Domain Users", "distinguished_name": "CN=Domain Users," + config.ldap_base_dn, "member_count": 120},
        {"name": "IT Department", "sam_account_name": "IT_Dept", "distinguished_name": "CN=IT_Dept," + config.ldap_base_dn, "member_count": 8},
    ]
    for g in sample_groups:
        existing = await db.execute(
            select(AdGroup).where(AdGroup.distinguished_name == g["distinguished_name"])
        )
        if not existing.scalar_one_or_none():
            grp = AdGroup(
                organization_id=current_user.organization_id,
                domain_config_id=config.id,
                **g,
                is_synced=True,
                synced_at=datetime.now(timezone.utc),
            )
            db.add(grp)

    config.sync_status = DomainSyncStatus.synced
    config.last_sync_at = datetime.now(timezone.utc)
    await db.commit()

    return {"ok": True, "message": "Sinxronizatsiya muvaffaqiyatli yakunlandi", "users": len(sample_users), "groups": len(sample_groups), "ous": len(sample_ous)}


# ── SSO ──

@router.post("/sso/login")
async def sso_login(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """SSO login with AD credentials (simulated)."""
    from app.services.auth_service import AuthService
    from app.utils.security import create_access_token, create_refresh_token
    from app.schemas.user import TokenResponse, UserResponse
    from app.config import settings
    from datetime import datetime, timezone

    username = data.get("username", "")
    password = data.get("password", "")

    ad_user = await db.execute(
        select(AdUser).where(AdUser.sam_account_name == username)
    )
    ad_user = ad_user.scalar_one_or_none()
    if not ad_user:
        raise HTTPException(401, "Domain foydalanuvchisi topilmadi")

    if ad_user.linked_user_id:
        local_user = await db.get(User, ad_user.linked_user_id)
    else:
        from app.models.user import UserRole
        local_user = User(
            organization_id=ad_user.organization_id,
            username=ad_user.sam_account_name,
            email=ad_user.email or f"{ad_user.sam_account_name}@domain.local",
            password_hash="",  # SSO users don't need local password
            role=UserRole.viewer,
            full_name=ad_user.display_name,
        )
        db.add(local_user)
        await db.commit()
        await db.refresh(local_user)
        ad_user.linked_user_id = local_user.id
        await db.commit()

    local_user.last_login = datetime.now(timezone.utc)
    await db.commit()

    user_resp = UserResponse.model_validate(local_user)
    token_data = {"sub": str(local_user.id), "role": local_user.role.value}
    if local_user.organization_id:
        token_data["org_id"] = str(local_user.organization_id)
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"sub": str(local_user.id), "type": "refresh"})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=user_resp,
    )


# ── Imported Data ──

@router.get("/users")
async def list_ad_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(AdUser).where(AdUser.organization_id == current_user.organization_id).order_by(AdUser.sam_account_name)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/groups")
async def list_ad_groups(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(AdGroup).where(AdGroup.organization_id == current_user.organization_id).order_by(AdGroup.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/ous")
async def list_ad_ous(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(AdOU).where(AdOU.organization_id == current_user.organization_id).order_by(AdOU.name)
    result = await db.execute(q)
    return result.scalars().all()


# ── GPO ──

@router.get("/gpos")
async def list_gpos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(AdGpo).where(AdGpo.organization_id == current_user.organization_id).order_by(AdGpo.name)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/gpos")
async def create_gpo(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    gpo = AdGpo(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(AdGpo, k) and k not in ("id", "organization_id", "created_by")},
    )
    db.add(gpo)
    await db.commit()
    await db.refresh(gpo)
    return gpo


@router.patch("/gpos/{gpo_id}")
async def update_gpo(
    gpo_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(AdGpo).where(AdGpo.id == gpo_id))
    gpo = result.scalar_one_or_none()
    if not gpo:
        raise HTTPException(404, "GPO not found")
    for k, v in data.items():
        if hasattr(gpo, k) and k not in ("id", "organization_id"):
            setattr(gpo, k, v)
    await db.commit()
    await db.refresh(gpo)
    return gpo


@router.delete("/gpos/{gpo_id}")
async def delete_gpo(
    gpo_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(AdGpo).where(AdGpo.id == gpo_id))
    gpo = result.scalar_one_or_none()
    if not gpo:
        raise HTTPException(404, "GPO not found")
    await db.delete(gpo)
    await db.commit()
    return {"ok": True}
