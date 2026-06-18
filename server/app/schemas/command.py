from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.utils.types import UUIDStr, OptionalUUIDStr


class CommandCreate(BaseModel):
    command_type: str = Field(
        ...,
        pattern="^(lock_screen|unlock_screen|take_screenshot|send_message|restart|shutdown|kill_process|open_app|run_command)$",
    )
    payload: Optional[dict] = None


class CommandResponse(BaseModel):
    id: UUIDStr
    computer_id: UUIDStr
    command_type: str
    payload: Optional[dict] = None
    status: str
    sent_by: OptionalUUIDStr = None
    sent_at: datetime
    executed_at: Optional[datetime] = None
    result: Optional[dict] = None

    model_config = {"from_attributes": True}
