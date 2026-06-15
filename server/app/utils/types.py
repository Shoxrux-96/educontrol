from uuid import UUID
from typing import Annotated
from pydantic import BeforeValidator


def coerce_uuid(v):
    if isinstance(v, UUID):
        return str(v)
    if v is None:
        return None
    return str(v)


UUIDStr = Annotated[str, BeforeValidator(coerce_uuid)]
OptionalUUIDStr = Annotated[str | None, BeforeValidator(coerce_uuid)]
