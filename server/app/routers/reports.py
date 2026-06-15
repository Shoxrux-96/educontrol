from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.tasks.reports import generate_report, REPORT_STATUS

import os


class ReportRequest(BaseModel):
    report_type: str
    start_date: str
    end_date: str
    scope: str = "all"
    scope_id: str = None
    format: str = "pdf"
    include: list = ["internet", "applications", "usb", "print"]


class ReportTaskResponse(BaseModel):
    task_id: str


router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.post("/generate", response_model=ReportTaskResponse)
async def generate_report_endpoint(
    data: ReportRequest,
    current_user: User = Depends(get_current_user),
):
    task = generate_report.delay(
        report_type=data.report_type,
        start_date=data.start_date,
        end_date=data.end_date,
        scope=data.scope,
        scope_id=data.scope_id,
        format=data.format,
        include=data.include,
    )
    return ReportTaskResponse(task_id=task.id)


@router.get("/{task_id}/status")
async def get_report_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    status = REPORT_STATUS.get(task_id, {"status": "not_found"})
    return status


@router.get("/{task_id}/download")
async def download_report(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    status = REPORT_STATUS.get(task_id)
    if not status or status.get("status") != "completed":
        raise HTTPException(status_code=404, detail="Report not ready or not found")

    filepath = status.get("filepath")
    if not filepath or not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report file not found")

    return FileResponse(
        filepath,
        filename=status.get("filename", "report.pdf"),
        media_type="application/octet-stream",
    )
