from datetime import datetime

from pydantic import BaseModel

from app.models.agenda import AgendaEventType


class AgendaEventCreate(BaseModel):
    user_id: int
    project_id: int | None = None
    type: AgendaEventType
    title: str
    description: str | None = None
    start_at: datetime
    end_at: datetime


class AgendaEventOut(AgendaEventCreate):
    id: int

    model_config = {"from_attributes": True}
