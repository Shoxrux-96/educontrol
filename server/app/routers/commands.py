from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.command import CommandCreate, CommandResponse
from app.services.command_service import CommandService
from app.utils.security import get_current_user, require_role
from app.models.user import User
from app.websocket.manager import manager

router = APIRouter(prefix="/api/v1", tags=["Commands"])


@router.post("/computers/{computer_id}/commands", response_model=CommandResponse, status_code=201)
async def send_command(
    computer_id: str,
    data: CommandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = CommandService(db)
    try:
        command = await service.send_command(computer_id, data, str(current_user.id))
        ws_message = {
            "type": "command",
            "command_id": str(command.id),
            "action": data.command_type,
            "payload": data.payload or {},
        }
        await manager.send_to_computer(computer_id, ws_message)
        return command
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/groups/{group_id}/commands", response_model=list[CommandResponse], status_code=201)
async def send_group_command(
    group_id: str,
    data: CommandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = CommandService(db)
    try:
        commands = await service.send_command_to_group(group_id, data, str(current_user.id))
        for cmd in commands:
            ws_message = {
                "type": "command",
                "command_id": str(cmd.id),
                "action": data.command_type,
                "payload": data.payload or {},
            }
            await manager.send_to_computer(cmd.computer_id, ws_message)
        return commands
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/computers/broadcast", response_model=list[CommandResponse], status_code=201)
async def broadcast_command(
    data: CommandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "super_admin")),
):
    service = CommandService(db)
    commands = await service.broadcast_command(data, str(current_user.id))
    for cmd in commands:
        ws_message = {
            "type": "command",
            "command_id": str(cmd.id),
            "action": data.command_type,
            "payload": data.payload or {},
        }
        await manager.send_to_computer(cmd.computer_id, ws_message)
    return commands
