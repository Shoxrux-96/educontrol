import os
import hashlib
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.agent_build import AgentBuild
from app.schemas.agent_update import (
    AgentUpdateCheckResponse,
    AgentBuildResponse,
    AgentBuildCreate,
)
from app.utils.security import get_current_user, require_role
from app.utils.types import UUIDStr
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agent-updates", tags=["Agent Updates"])

BUILDS_DIR = os.path.join(settings.backup_path, "agent_builds")


def ensure_builds_dir():
    os.makedirs(BUILDS_DIR, exist_ok=True)


@router.get("/check", response_model=AgentUpdateCheckResponse)
async def check_for_update(
    current_version: str = Query(...),
    platform: str = Query("windows"),
    arch: str = Query("x86_64"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(AgentBuild).where(
            AgentBuild.platform == platform,
            AgentBuild.arch == arch,
            AgentBuild.is_active == True,
        ).order_by(AgentBuild.created_at.desc()).limit(1)
    )
    latest = result.scalar_one_or_none()
    if not latest:
        return AgentUpdateCheckResponse(
            update_available=False, latest_version=None, build=None
        )
    return AgentUpdateCheckResponse(
        update_available=latest.version != current_version,
        latest_version=latest.version,
        build=latest,
    )


@router.get("/builds", response_model=list[AgentBuildResponse])
async def list_builds(
    platform: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = select(AgentBuild).order_by(AgentBuild.created_at.desc())
    if platform:
        query = query.where(AgentBuild.platform == platform)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/download/{build_id}")
async def download_build(
    build_id: UUIDStr,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = await db.execute(select(AgentBuild).where(AgentBuild.id == build_id))
    build = result.scalar_one_or_none()
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if not os.path.exists(build.file_path):
        raise HTTPException(status_code=404, detail="Build file not found on disk")
    return FileResponse(
        build.file_path,
        filename=f"educontrol-agent-{build.version}-{build.platform}-{build.arch}",
        media_type="application/octet-stream",
    )


@router.post("/builds", response_model=AgentBuildResponse, status_code=status.HTTP_201_CREATED)
async def upload_build(
    version: str = Form(...),
    platform: str = Form("windows"),
    arch: str = Form("x86_64"),
    changelog: str | None = Form(None),
    is_active: bool = Form(True),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin", "super_admin")),
):
    ensure_builds_dir()
    filename = f"educontrol-agent-{version}-{platform}-{arch}"
    file_path = os.path.join(BUILDS_DIR, filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    checksum = hashlib.sha256(content).hexdigest()

    build = AgentBuild(
        version=version,
        platform=platform,
        arch=arch,
        file_path=file_path,
        file_size=len(content),
        checksum_sha256=checksum,
        changelog=changelog,
        is_active=is_active,
    )
    db.add(build)
    await db.commit()
    await db.refresh(build)
    logger.info(f"Agent build uploaded: {filename} ({build.id})")
    return build


@router.put("/builds/{build_id}/toggle", response_model=AgentBuildResponse)
async def toggle_build_active(
    build_id: UUIDStr,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin", "super_admin")),
):
    result = await db.execute(select(AgentBuild).where(AgentBuild.id == build_id))
    build = result.scalar_one_or_none()
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    build.is_active = not build.is_active
    await db.commit()
    await db.refresh(build)
    return build


@router.delete("/builds/{build_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_build(
    build_id: UUIDStr,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin", "super_admin")),
):
    result = await db.execute(select(AgentBuild).where(AgentBuild.id == build_id))
    build = result.scalar_one_or_none()
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    if os.path.exists(build.file_path):
        os.remove(build.file_path)
    await db.delete(build)
    await db.commit()
