from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.core import GlobalRole, OrgMembership, Organization
from app.schemas.common import Message
from app.schemas.organization import OrganizationCreate, OrganizationOut

router = APIRouter(prefix="/organizations")


def ensure_owner(role: GlobalRole) -> None:
    if role not in {GlobalRole.OWNER, GlobalRole.ADMIN}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")


@router.post("/", response_model=OrganizationOut)
async def create_organization(
    payload: OrganizationCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> OrganizationOut:
    organization = Organization(name=payload.name)
    session.add(organization)
    await session.flush()
    session.add(OrgMembership(organization_id=organization.id, user_id=current_user.id, role=GlobalRole.OWNER))
    await session.commit()
    await session.refresh(organization)
    return organization


@router.get("/", response_model=list[OrganizationOut])
async def list_organizations(session: AsyncSession = Depends(get_db)) -> list[OrganizationOut]:
    result = await session.scalars(select(Organization))
    return list(result)


@router.delete("/{org_id}", response_model=Message)
async def delete_org(
    org_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Message:
    membership = await session.scalar(
        select(OrgMembership).where(OrgMembership.organization_id == org_id, OrgMembership.user_id == current_user.id)
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")
    ensure_owner(membership.role)
    organization = await session.get(Organization, org_id)
    if not organization:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    await session.delete(organization)
    await session.commit()
    return Message(message="deleted")
