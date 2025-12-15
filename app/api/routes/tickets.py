from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.kanban import KanbanColumn
from app.models.notification import Event
from app.models.project import ProjectMembership, ProjectRole
from app.models.ticket import Ticket, TicketComment
from app.schemas.ticket import CommentBase, CommentOut, TicketCreate, TicketMove, TicketOut, TicketTimeSegmentOut
from app.services.time_tracking import start_timer, stop_timer

router = APIRouter(prefix="/tickets")


async def ensure_project_access(
    session: AsyncSession, project_id: int, user_id: int, min_role: ProjectRole | None = None
) -> None:
    membership = await session.scalar(
        select(ProjectMembership).where(ProjectMembership.project_id == project_id, ProjectMembership.user_id == user_id)
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No project access")
    if min_role and membership.role not in {min_role, ProjectRole.PROJECT_OWNER, ProjectRole.MAINTAINER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")


@router.post("/", response_model=TicketOut)
async def create_ticket(
    payload: TicketCreate,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TicketOut:
    await ensure_project_access(session, payload.project_id, current_user.id)
    column = await session.get(KanbanColumn, payload.column_id)
    if not column:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid column")
    ticket = Ticket(**payload.model_dump())
    session.add(ticket)
    await session.flush()
    session.add(Event(ticket_id=ticket.id, action="created", actor_id=current_user.id))
    await session.commit()
    await session.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/move", response_model=TicketOut)
async def move_ticket(
    ticket_id: int,
    payload: TicketMove,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> TicketOut:
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    await ensure_project_access(session, ticket.project_id, current_user.id)
    new_column = await session.get(KanbanColumn, payload.column_id)
    if not new_column:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid column")
    ticket.column_id = payload.column_id
    await session.flush()
    if new_column.name == "IN_PROGRESS":
        await start_timer(ticket, session)
    elif new_column.name == "DONE":
        await stop_timer(ticket, session)
    session.add(Event(ticket_id=ticket.id, action="moved", actor_id=current_user.id, details=str(payload.column_id)))
    await session.commit()
    await session.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/comments", response_model=CommentOut)
async def add_comment(
    ticket_id: int,
    payload: CommentBase,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> CommentOut:
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    await ensure_project_access(session, ticket.project_id, current_user.id)
    comment = TicketComment(ticket_id=ticket_id, author_id=current_user.id, body=payload.body)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment


@router.get("/{ticket_id}/time", response_model=list[TicketTimeSegmentOut])
async def list_time_segments(ticket_id: int, session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    ticket = await session.get(Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    await ensure_project_access(session, ticket.project_id, current_user.id)
    return ticket.time_segments
