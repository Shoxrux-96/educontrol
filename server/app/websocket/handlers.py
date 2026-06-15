import json
import logging
from datetime import datetime, timezone
from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.websocket.manager import manager
from app.services.computer_service import ComputerService
from app.services.command_service import CommandService
from app.services.audit_service import AuditService
from app.models.computer import Computer, ComputerStatus
from app.database import async_session

logger = logging.getLogger(__name__)


async def handle_agent_message(websocket: WebSocket, message: dict, db: AsyncSession):
    msg_type = message.get("type")
    agent_id = message.get("agent_id")

    if msg_type == "register":
        await handle_register(websocket, message, db)
    elif msg_type == "heartbeat":
        await handle_heartbeat(agent_id, message, db)
    elif msg_type == "event":
        await handle_event(agent_id, message, db)
    elif msg_type == "command_result":
        await handle_command_result(agent_id, message, db)
    else:
        logger.warning(f"Unknown message type: {msg_type}")


async def handle_register(websocket: WebSocket, message: dict, db: AsyncSession):
    computer_service = ComputerService(db)
    computer = await computer_service.get_or_create_computer_by_agent(message)

    agent_id = message.get("agent_id", str(computer.id))
    await manager.connect(websocket, agent_id, str(computer.id))

    audit = AuditService(db)
    await audit.log_event(
        event_type="agent_online",
        description=f"Agent connected: {message.get('hostname', 'Unknown')}",
        computer_id=str(computer.id),
        extra_data={"agent_version": message.get("agent_version")},
    )


async def handle_heartbeat(agent_id: str, message: dict, db: AsyncSession):
    if agent_id not in manager.connections:
        logger.warning(f"Heartbeat from unknown agent: {agent_id}")
        return

    info = manager.connections[agent_id]
    manager.update_heartbeat(agent_id)

    async with async_session() as session:
        result = await session.execute(
            select(Computer).where(Computer.id == info.computer_id)
        )
        computer = result.scalar_one_or_none()
        if computer:
            computer.cpu_usage = message.get("cpu")
            computer.ram_usage = message.get("ram")
            computer.disk_usage = message.get("disk")
            computer.current_user = message.get("current_user")
            computer.status = ComputerStatus(message.get("status", "online"))
            computer.last_seen = datetime.now(timezone.utc)
            await session.commit()


async def handle_event(agent_id: str, message: dict, db: AsyncSession):
    info = manager.connections.get(agent_id)
    if not info:
        return

    event = message.get("event")
    details = message.get("details", {})

    severity_map = {
        "app_blocked": "warning",
        "web_blocked": "info",
        "usb_connected": "info",
        "usb_blocked": "warning",
    }

    audit = AuditService(db)
    await audit.log_event(
        event_type=event,
        description=f"Event: {event} - {json.dumps(details)}",
        computer_id=info.computer_id,
        severity=severity_map.get(event, "info"),
        extra_data=details,
    )


async def handle_command_result(agent_id: str, message: dict, db: AsyncSession):
    command_id = message.get("command_id")
    success = message.get("success", False)
    data = message.get("data", {})

    if command_id:
        command_service = CommandService(db)
        await command_service.update_command_result(command_id, success, data)
