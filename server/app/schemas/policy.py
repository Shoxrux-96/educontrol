from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.utils.types import UUIDStr, OptionalUUIDStr


class PolicyCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    policy_type: str
    config: dict


class PolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    is_active: Optional[bool] = None


class PolicyResponse(BaseModel):
    id: UUIDStr
    name: str
    description: Optional[str] = None
    policy_type: str
    config: dict
    is_active: bool
    created_by: OptionalUUIDStr = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PolicyAssignRequest(BaseModel):
    target_type: str
    target_id: OptionalUUIDStr = None


class PolicyAssignmentResponse(BaseModel):
    id: UUIDStr
    policy_id: UUIDStr
    target_type: str
    target_id: OptionalUUIDStr = None
    assigned_at: datetime

    model_config = {"from_attributes": True}
