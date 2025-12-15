from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.notification import Notification
from app.schemas.common import Message

router = APIRouter(prefix="/notifications")


@router.get("/", response_model=list[Notification])
async def list_notifications(
    session: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    result = await session.scalars(select(Notification).where(Notification.user_id == current_user.id))
    return list(result)


@router.post("/{notification_id}/read", response_model=Message)
async def mark_read(
    notification_id: int,
    session: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Message:
    notification = await session.get(Notification, notification_id)
    if not notification or notification.user_id != current_user.id:
        return Message(message="not found")
    notification.read = True
    await session.commit()
    return Message(message="ok")
