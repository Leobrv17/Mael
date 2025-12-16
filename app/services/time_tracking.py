from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.ticket import Ticket, TicketTimeSegment


async def start_timer(ticket: Ticket, session: AsyncSession) -> None:
    result = await session.scalars(
        select(TicketTimeSegment).where(TicketTimeSegment.ticket_id == ticket.id)
    )
    existing = list(result)
    if any(segment.ended_at is None for segment in existing):
        return

    segment = TicketTimeSegment(ticket_id=ticket.id, started_at=datetime.utcnow())
    session.add(segment)
    await session.flush()


async def stop_timer(ticket: Ticket, session: AsyncSession) -> None:
    result = await session.scalars(
        select(TicketTimeSegment).where(TicketTimeSegment.ticket_id == ticket.id)
    )
    segments = list(result)
    for segment in segments:
        if segment.ended_at is None:
            segment.ended_at = datetime.utcnow()
    await session.flush()
