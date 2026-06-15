from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.utils.types import UUIDStr, OptionalUUIDStr


class ComputerGroupCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    color: Optional[str] = None


class ComputerGroupResponse(BaseModel):
    id: UUIDStr
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    computer_count: Optional[int] = None

    model_config = {"from_attributes": True}


class ComputerUpdate(BaseModel):
    name: Optional[str] = None
    group_id: OptionalUUIDStr = None


class ComputerResponse(BaseModel):
    id: UUIDStr
    name: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    group_id: OptionalUUIDStr = None
    os_version: Optional[str] = None
    agent_version: Optional[str] = None
    status: str
    last_seen: Optional[datetime] = None
    cpu_model: Optional[str] = None
    ram_gb: Optional[int] = None
    disk_gb: Optional[int] = None
    current_user: Optional[str] = None
    cpu_usage: Optional[int] = None
    ram_usage: Optional[int] = None
    disk_usage: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ComputerStatsResponse(BaseModel):
    computer_id: str
    cpu_history: List[dict]
    ram_history: List[dict]
    disk_history: List[dict]
