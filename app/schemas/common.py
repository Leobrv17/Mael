from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(ORMBase):
    message: str


class AuditEvent(ORMBase):
    action: str
    created_at: datetime
    details: Any | None = None
