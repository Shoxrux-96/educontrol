from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.utils.types import OptionalUUIDStr


class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    computer_id: OptionalUUIDStr = None
    user_id: OptionalUUIDStr = None
    description: str
    details: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}
