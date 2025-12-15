from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as PgEnum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


ticket_assignees_table = Table(
    "ticket_assignees",
    Base.metadata,
    mapped_column("ticket_id", ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True),
    mapped_column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    sprint_id: Mapped[int | None] = mapped_column(ForeignKey("sprints.id"))
    column_id: Mapped[int] = mapped_column(ForeignKey("kanban_columns.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    priority: Mapped[Priority] = mapped_column(PgEnum(Priority), default=Priority.MEDIUM)
    estimation_minutes: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    project: Mapped["Project"] = relationship("Project", back_populates="tickets")
    column: Mapped["KanbanColumn"] = relationship("KanbanColumn")
    sprint: Mapped["Sprint"] = relationship("Sprint")
    assignees: Mapped[list["User"]] = relationship("User", secondary=ticket_assignees_table)
    comments: Mapped[list["TicketComment"]] = relationship(
        "TicketComment", back_populates="ticket", cascade="all, delete-orphan"
    )
    time_segments: Mapped[list["TicketTimeSegment"]] = relationship(
        "TicketTimeSegment", back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="comments")
    author: Mapped["User"] = relationship("User")


class TicketTimeSegment(Base):
    __tablename__ = "ticket_time_segments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id", ondelete="CASCADE"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    ticket: Mapped[Ticket] = relationship("Ticket", back_populates="time_segments")
