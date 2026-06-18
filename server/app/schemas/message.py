from pydantic import BaseModel, Field

from app.utils.types import OptionalUUIDStr


class MessageCreate(BaseModel):
    title: str = Field(..., max_length=200)
    body: str
    message_type: str = "info"
    target_type: str
    target_id: OptionalUUIDStr = None
