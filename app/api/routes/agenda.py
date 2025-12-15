from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.agenda import AgendaEvent
from app.models.core import GlobalRole, OrgMembership
from app.schemas.agenda import AgendaEventCreate, AgendaEventOut

router = APIRouter(prefix="/agenda")


def can_view(user_role: GlobalRole) -> bool:
    return user_role in {GlobalRole.OWNER, GlobalRole.ADMIN, GlobalRole.MEMBER}


@router.post("/", response_model=AgendaEventOut)
async def create_event(
    payload: AgendaEventCreate,
    session: AsyncSession = Depends(get_db),
) -> AgendaEventOut:
    event = AgendaEvent(**payload.model_dump())
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


@router.get("/", response_model=list[AgendaEventOut])
async def list_events(
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[AgendaEventOut]:
    membership = await session.scalar(select(OrgMembership).where(OrgMembership.user_id == current_user.id))
    if not membership or not can_view(membership.role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    result = await session.scalars(select(AgendaEvent).where(AgendaEvent.user_id == current_user.id))
    return list(result)
