from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as PgEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ProjectRole(str, Enum):
    PROJECT_OWNER = "PROJECT_OWNER"
    MAINTAINER = "MAINTAINER"
    CONTRIBUTOR = "CONTRIBUTOR"
    REPORTER = "REPORTER"
    VIEWER = "VIEWER"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    organization: Mapped["Organization"] = relationship("Organization", back_populates="projects")
    memberships: Mapped[list[ProjectMembership]] = relationship(
        "ProjectMembership", back_populates="project", cascade="all, delete-orphan"
    )
    sprints: Mapped[list["Sprint"]] = relationship("Sprint", back_populates="project")
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="project")
    columns: Mapped[list["KanbanColumn"]] = relationship(
        "KanbanColumn", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectMembership(Base):
    __tablename__ = "project_memberships"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[ProjectRole] = mapped_column(PgEnum(ProjectRole), default=ProjectRole.VIEWER)

    project: Mapped[Project] = relationship("Project", back_populates="memberships")
    user: Mapped["User"] = relationship("User")


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255))
    goal: Mapped[str | None] = mapped_column(String(500))
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[Project] = relationship("Project", back_populates="sprints")
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="sprint")
