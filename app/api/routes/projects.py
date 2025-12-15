from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.core import OrgMembership, Organization
from app.models.project import Project, ProjectMembership, ProjectRole, Sprint
from app.schemas.project import ProjectCreate, ProjectOut, ProjectMembershipOut, SprintCreate, SprintOut

router = APIRouter(prefix="/projects")


def ensure_org_access(session: AsyncSession, org_id: int, user_id: int) -> None:
    # To be extended with finer RBAC
    pass


@router.post("/", response_model=ProjectOut)
async def create_project(
    payload: ProjectCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProjectOut:
    org_membership = await session.scalar(
        select(OrgMembership).where(OrgMembership.organization_id == payload.organization_id, OrgMembership.user_id == current_user.id)
    )
    if not org_membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not in organization")
    project = Project(**payload.model_dump())
    session.add(project)
    await session.flush()
    session.add(ProjectMembership(project_id=project.id, user_id=current_user.id, role=ProjectRole.PROJECT_OWNER))
    await session.commit()
    await session.refresh(project)
    return project


@router.get("/", response_model=list[ProjectOut])
async def list_projects(session: AsyncSession = Depends(get_db)) -> list[ProjectOut]:
    return list(await session.scalars(select(Project)))


@router.post("/{project_id}/members", response_model=ProjectMembershipOut)
async def add_member(
    project_id: int,
    role: ProjectRole,
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> ProjectMembershipOut:
    owner = await session.scalar(
        select(ProjectMembership).where(ProjectMembership.project_id == project_id, ProjectMembership.user_id == current_user.id)
    )
    if not owner or owner.role not in {ProjectRole.PROJECT_OWNER, ProjectRole.MAINTAINER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    membership = ProjectMembership(project_id=project_id, user_id=user_id, role=role)
    session.add(membership)
    await session.commit()
    await session.refresh(membership)
    return membership


@router.post("/{project_id}/sprints", response_model=SprintOut)
async def create_sprint(
    project_id: int,
    payload: SprintCreate,
    session: AsyncSession = Depends(get_db),
) -> SprintOut:
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    sprint = Sprint(project_id=project_id, **payload.model_dump(exclude={"project_id"}))
    session.add(sprint)
    await session.commit()
    await session.refresh(sprint)
    return sprint
