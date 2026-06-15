from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.computer import Computer, ComputerGroup, ComputerStatus
from app.schemas.computer import (
    ComputerUpdate,
    ComputerResponse,
    ComputerGroupCreate,
    ComputerGroupResponse,
    ComputerStatsResponse,
)
from app.utils.pagination import PaginatedResponse, paginate


class ComputerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_computers(
        self, page: int = 1, page_size: int = 20, status: Optional[str] = None, group_id: Optional[str] = None, search: Optional[str] = None
    ) -> PaginatedResponse[ComputerResponse]:
        query = select(Computer)
        if status:
            query = query.where(Computer.status == ComputerStatus(status))
        if group_id:
            query = query.where(Computer.group_id == group_id)
        if search:
            query = query.where(
                Computer.name.ilike(f"%{search}%") | Computer.hostname.ilike(f"%{search}%")
            )
        query = query.order_by(Computer.name)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        computers = result.scalars().all()

        items = [ComputerResponse.model_validate(c) for c in computers]
        return paginate(items, total, page, page_size)

    async def get_computer(self, computer_id: str) -> ComputerResponse:
        result = await self.db.execute(
            select(Computer).where(Computer.id == computer_id)
        )
        computer = result.scalar_one_or_none()
        if not computer:
            raise ValueError("Computer not found")
        return ComputerResponse.model_validate(computer)

    async def update_computer(self, computer_id: str, data: ComputerUpdate) -> ComputerResponse:
        result = await self.db.execute(
            select(Computer).where(Computer.id == computer_id)
        )
        computer = result.scalar_one_or_none()
        if not computer:
            raise ValueError("Computer not found")

        if data.name is not None:
            computer.name = data.name
        if data.group_id is not None:
            computer.group_id = data.group_id

        await self.db.commit()
        await self.db.refresh(computer)
        return ComputerResponse.model_validate(computer)

    async def delete_computer(self, computer_id: str):
        result = await self.db.execute(
            select(Computer).where(Computer.id == computer_id)
        )
        computer = result.scalar_one_or_none()
        if not computer:
            raise ValueError("Computer not found")
        await self.db.delete(computer)
        await self.db.commit()

    async def get_computer_stats(self, computer_id: str) -> ComputerStatsResponse:
        result = await self.db.execute(
            select(Computer).where(Computer.id == computer_id)
        )
        computer = result.scalar_one_or_none()
        if not computer:
            raise ValueError("Computer not found")
        return ComputerStatsResponse(
            computer_id=str(computer.id),
            cpu_history=[{"usage": computer.cpu_usage}],
            ram_history=[{"usage": computer.ram_usage}],
            disk_history=[{"usage": computer.disk_usage}],
        )

    async def get_or_create_computer_by_agent(self, agent_data: dict) -> Computer:
        result = await self.db.execute(
            select(Computer).where(
                (Computer.hostname == agent_data.get("hostname"))
                & (Computer.mac_address == agent_data.get("mac"))
            )
        )
        computer = result.scalar_one_or_none()
        if not computer:
            computer = Computer(
                name=agent_data.get("hostname", "Unknown"),
                hostname=agent_data.get("hostname"),
                ip_address=agent_data.get("ip"),
                mac_address=agent_data.get("mac"),
                os_version=agent_data.get("os"),
                agent_version=agent_data.get("agent_version"),
                status=ComputerStatus.online,
            )
            self.db.add(computer)
        else:
            computer.ip_address = agent_data.get("ip")
            computer.status = ComputerStatus.online
            computer.agent_version = agent_data.get("agent_version")
        await self.db.commit()
        await self.db.refresh(computer)
        return computer

    async def create_group(self, data: ComputerGroupCreate) -> ComputerGroupResponse:
        group = ComputerGroup(
            name=data.name,
            description=data.description,
            color=data.color,
        )
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return ComputerGroupResponse.model_validate(group)

    async def list_groups(self) -> List[ComputerGroupResponse]:
        result = await self.db.execute(select(ComputerGroup).order_by(ComputerGroup.name))
        groups = result.scalars().all()
        items = []
        for g in groups:
            count_result = await self.db.execute(
                select(func.count()).where(Computer.group_id == g.id)
            )
            count = count_result.scalar()
            resp = ComputerGroupResponse.model_validate(g)
            resp.computer_count = count
            items.append(resp)
        return items
