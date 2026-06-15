from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.message import MessageCreate
from app.models.message import Message
from app.utils.security import get_current_user, require_role
from app.models.user import User
from app.websocket.manager import manager

router = APIRouter(prefix="/api/v1/messages", tags=["Messages"])


@router.post("", status_code=201)
async def send_message(
    data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    msg = Message(
        title=data.title,
        body=data.body,
        message_type=data.message_type,
        sender_id=current_user.id,
        target_type=data.target_type,
        target_id=data.target_id,
    )
    db.add(msg)
    await db.commit()

    ws_msg = {
        "type": "message",
        "message_id": str(msg.id),
        "title": data.title,
        "body": data.body,
        "severity": data.message_type,
    }

    if data.target_type == "all":
        await manager.broadcast(ws_msg)
    elif data.target_type == "computer" and data.target_id:
        await manager.send_to_computer(data.target_id, ws_msg)

    return {"id": str(msg.id), "status": "sent"}
