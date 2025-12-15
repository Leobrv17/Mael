from datetime import datetime

from pydantic import BaseModel

from app.models.project import ProjectRole


class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    organization_id: int


class ProjectOut(ProjectBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectMembershipOut(BaseModel):
    id: int
    user_id: int
    role: ProjectRole

    model_config = {"from_attributes": True}


class SprintBase(BaseModel):
    name: str
    goal: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class SprintCreate(SprintBase):
    project_id: int


class SprintOut(SprintBase):
    id: int
    project_id: int

    model_config = {"from_attributes": True}
