from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ticket import Ticket, TicketTimeSegment


async def start_timer(ticket: Ticket, session: AsyncSession) -> None:
    if any(segment.ended_at is None for segment in ticket.time_segments):
        return
    segment = TicketTimeSegment(ticket=ticket, started_at=datetime.utcnow())
    session.add(segment)
    await session.flush()


async def stop_timer(ticket: Ticket, session: AsyncSession) -> None:
    for segment in ticket.time_segments:
        if segment.ended_at is None:
            segment.ended_at = datetime.utcnow()
    await session.flush()
