from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.command import Command, CommandStatus
from app.models.computer import Computer
from app.schemas.command import CommandCreate, CommandResponse


class CommandService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_command(
        self, computer_id: str, data: CommandCreate, user_id: str
    ) -> CommandResponse:
        result = await self.db.execute(
            select(Computer).where(Computer.id == computer_id)
        )
        if not result.scalar_one_or_none():
            raise ValueError("Computer not found")

        command = Command(
            computer_id=computer_id,
            command_type=data.command_type,
            payload=data.payload,
            status=CommandStatus.pending,
            sent_by=user_id,
        )
        self.db.add(command)
        await self.db.commit()
        await self.db.refresh(command)
        return CommandResponse.model_validate(command)

    async def send_command_to_group(
        self, group_id: str, data: CommandCreate, user_id: str
    ) -> list[CommandResponse]:
        result = await self.db.execute(
            select(Computer).where(Computer.group_id == group_id)
        )
        computers = result.scalars().all()
        commands = []
        for comp in computers:
            cmd = await self.send_command(str(comp.id), data, user_id)
            commands.append(cmd)
        return commands

    async def broadcast_command(
        self, data: CommandCreate, user_id: str
    ) -> list[CommandResponse]:
        result = await self.db.execute(select(Computer).where(Computer.status != "offline"))
        computers = result.scalars().all()
        commands = []
        for comp in computers:
            cmd = await self.send_command(str(comp.id), data, user_id)
            commands.append(cmd)
        return commands

    async def update_command_result(
        self, command_id: str, success: bool, result_data: Optional[dict] = None
    ):
        result = await self.db.execute(
            select(Command).where(Command.id == command_id)
        )
        command = result.scalar_one_or_none()
        if command:
            command.status = CommandStatus.executed if success else CommandStatus.failed
            command.executed_at = datetime.now(timezone.utc)
            command.result = result_data
            await self.db.commit()

    async def get_computer_commands(
        self, computer_id: str, limit: int = 50
    ) -> list[CommandResponse]:
        result = await self.db.execute(
            select(Command)
            .where(Command.computer_id == computer_id)
            .order_by(Command.sent_at.desc())
            .limit(limit)
        )
        commands = result.scalars().all()
        return [CommandResponse.model_validate(c) for c in commands]
