from datetime import datetime
from pydantic import BaseModel

from app.utils.types import UUIDStr


class AgentUpdateCheckRequest(BaseModel):
    current_version: str
    platform: str = "windows"
    arch: str = "x86_64"


class AgentBuildResponse(BaseModel):
    id: UUIDStr
    version: str
    platform: str
    arch: str
    file_path: str
    file_size: int
    checksum_sha256: str
    changelog: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentUpdateCheckResponse(BaseModel):
    update_available: bool
    latest_version: str | None
    build: AgentBuildResponse | None


class AgentBuildCreate(BaseModel):
    version: str
    platform: str = "windows"
    arch: str = "x86_64"
    changelog: str | None = None
    is_active: bool = True
