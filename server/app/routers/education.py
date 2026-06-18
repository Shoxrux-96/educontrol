from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_

from app.database import get_db
from app.models.user import User
from app.models.computer import Computer
from app.models.education import (
    ExamSession, ExamStatus, ExamParticipant,
    TestQuestion, QuestionType, TestAnswer,
    StudentActivityLog,
)
from app.utils.security import get_current_user, require_role
from app.websocket.manager import manager
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/education", tags=["Education"])


# ── Exam Sessions ──

@router.get("/exams")
async def list_exams(
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(ExamSession)
    if current_user.organization_id:
        q = q.where(ExamSession.organization_id == current_user.organization_id)
    if status:
        q = q.where(ExamSession.status == status)
    q = q.order_by(desc(ExamSession.created_at))
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/exams")
async def create_exam(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    exam = ExamSession(
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        **{k: v for k, v in data.items() if hasattr(ExamSession, k) and k not in ("id", "organization_id", "created_by")},
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)
    return exam


@router.patch("/exams/{exam_id}")
async def update_exam(
    exam_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(ExamSession).where(ExamSession.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(404, "Exam not found")
    for k, v in data.items():
        if hasattr(exam, k) and k not in ("id", "organization_id"):
            setattr(exam, k, v)
    await db.commit()
    await db.refresh(exam)
    return exam


@router.post("/exams/{exam_id}/start")
async def start_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(ExamSession).where(ExamSession.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(404, "Exam not found")
    exam.status = ExamStatus.active
    exam.start_time = datetime.now(timezone.utc)

    participants = await db.execute(
        select(ExamParticipant).where(ExamParticipant.exam_id == exam_id)
    )
    for p in participants.scalars().all():
        await manager.send_to_computer(str(p.computer_id), {
            "type": "exam_mode",
            "action": "start",
            "exam_id": exam_id,
            "exam_name": exam.name,
            "rules": {
                "block_internet": exam.block_internet,
                "block_usb": exam.block_usb,
                "block_alt_tab": exam.block_alt_tab,
                "block_task_manager": exam.block_task_manager,
                "block_cmd": exam.block_cmd,
                "monitor_screens": exam.monitor_screens,
                "auto_submit_on_leave": exam.auto_submit_on_leave,
                "duration_minutes": exam.duration_minutes,
            },
        })
    await db.commit()
    return exam


@router.post("/exams/{exam_id}/stop")
async def stop_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(select(ExamSession).where(ExamSession.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(404, "Exam not found")
    exam.status = ExamStatus.completed
    exam.end_time = datetime.now(timezone.utc)

    participants = await db.execute(
        select(ExamParticipant).where(ExamParticipant.exam_id == exam_id)
    )
    for p in participants.scalars().all():
        await manager.send_to_computer(str(p.computer_id), {
            "type": "exam_mode",
            "action": "stop",
            "exam_id": exam_id,
        })
    await db.commit()
    return exam


@router.post("/exams/{exam_id}/block-computer/{computer_id}")
async def block_exam_computer(
    exam_id: str,
    computer_id: str,
    data: dict = {},
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    result = await db.execute(
        select(ExamParticipant).where(
            ExamParticipant.exam_id == exam_id,
            ExamParticipant.computer_id == computer_id,
        )
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(404, "Participant not found in this exam")

    blocked = data.get("blocked", True)
    participant.computer_blocked = blocked

    await manager.send_to_computer(computer_id, {
        "type": "exam_mode",
        "action": "block" if blocked else "unblock",
        "exam_id": exam_id,
    })
    await db.commit()
    return {"ok": True, "blocked": blocked}


# ── Participants ──

@router.get("/exams/{exam_id}/participants")
async def list_participants(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ExamParticipant)
        .where(ExamParticipant.exam_id == exam_id)
        .order_by(ExamParticipant.student_name)
    )
    return result.scalars().all()


@router.post("/exams/{exam_id}/participants")
async def add_participants(
    exam_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    computer_ids = data.get("computer_ids", [])
    participants = []
    for cid in computer_ids:
        existing = await db.execute(
            select(ExamParticipant).where(
                ExamParticipant.exam_id == exam_id,
                ExamParticipant.computer_id == cid,
            )
        )
        if existing.scalar_one_or_none():
            continue
        comp = await db.get(Computer, cid)
        participant = ExamParticipant(
            exam_id=exam_id,
            computer_id=cid,
            student_name=data.get("student_name") or (comp.name if comp else None),
        )
        db.add(participant)
        participants.append(participant)
    await db.commit()
    return participants


# ── Test Questions ──

@router.get("/questions")
async def list_questions(
    exam_id: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(TestQuestion)
    if current_user.organization_id:
        q = q.where(TestQuestion.organization_id == current_user.organization_id)
    if exam_id:
        q = q.where(TestQuestion.exam_id == exam_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/questions")
async def create_question(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    question = TestQuestion(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(TestQuestion, k) and k not in ("id", "organization_id")},
    )
    db.add(question)
    await db.commit()
    await db.refresh(question)
    return question


@router.post("/questions/bulk")
async def bulk_create_questions(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    questions_data = data.get("questions", [])
    created = []
    for q_data in questions_data:
        q = TestQuestion(
            organization_id=current_user.organization_id,
            exam_id=data.get("exam_id"),
            **{k: v for k, v in q_data.items() if hasattr(TestQuestion, k) and k not in ("id", "organization_id")},
        )
        db.add(q)
        created.append(q)
    await db.commit()
    return created


# ── Activity Log ──

@router.get("/activity")
async def list_activity(
    exam_id: str = Query(None),
    computer_id: str = Query(None),
    limit: int = Query(100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(StudentActivityLog)
    if current_user.organization_id:
        q = q.where(StudentActivityLog.organization_id == current_user.organization_id)
    if exam_id:
        q = q.where(StudentActivityLog.exam_id == exam_id)
    if computer_id:
        q = q.where(StudentActivityLog.computer_id == computer_id)
    q = q.order_by(desc(StudentActivityLog.logged_at)).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/activity")
async def log_activity(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = StudentActivityLog(
        organization_id=current_user.organization_id,
        **{k: v for k, v in data.items() if hasattr(StudentActivityLog, k) and k not in ("id", "organization_id")},
    )
    db.add(log)
    await db.commit()
    return {"ok": True}


# ── Send test to computers ──

@router.post("/send-test")
async def send_test_to_computers(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    computer_ids = data.get("computer_ids", [])
    questions = data.get("questions", [])
    exam_id = data.get("exam_id")

    for cid in computer_ids:
        await manager.send_to_computer(cid, {
            "type": "exam_mode",
            "action": "send_test",
            "exam_id": exam_id,
            "questions": questions,
            "duration_minutes": data.get("duration_minutes", 30),
        })
    return {"ok": True, "computers_sent": len(computer_ids), "questions_count": len(questions)}


# ── Send message to computers ──

@router.post("/send-message")
async def send_message_to_computers(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "owner")),
):
    computer_ids = data.get("computer_ids", [])
    message = data.get("message", "")
    message_type = data.get("type", "info")

    for cid in computer_ids:
        await manager.send_to_computer(cid, {
            "type": "notification",
            "action": "show_message",
            "message": message,
            "message_type": message_type,
        })
    return {"ok": True, "computers_sent": len(computer_ids)}
