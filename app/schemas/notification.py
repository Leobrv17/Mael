from datetime import datetime

from app.schemas.common import ORMBase


class NotificationOut(ORMBase):
    id: int
    user_id: int
    title: str
    body: str
    created_at: datetime
    read: bool
