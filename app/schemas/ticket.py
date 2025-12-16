from datetime import datetime
from typing import Sequence

from pydantic import BaseModel

from app.models.ticket import Priority


class TicketBase(BaseModel):
    title: str
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    estimation_minutes: int | None = None
    column_id: int
    sprint_id: int | None = None


class TicketCreate(TicketBase):
    project_id: int


class TicketOut(TicketBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CommentBase(BaseModel):
    body: str


class CommentOut(CommentBase):
    id: int
    ticket_id: int
    author_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketMove(BaseModel):
    column_id: int


class TicketTimeSegmentOut(BaseModel):
    id: int
    ticket_id: int
    started_at: datetime
    ended_at: datetime | None

    model_config = {"from_attributes": True}
