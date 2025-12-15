from __future__ import annotations

import os
from typing import Annotated

import firebase_admin
from fastapi import Depends, Header, HTTPException, status
from firebase_admin import auth
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_session
from app.models.core import OrgMembership, Organization, User

logger = get_logger(__name__)


async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    decoded: dict[str, str]
    emulated_uid = os.getenv("FIREBASE_EMULATED_UID")
    if emulated_uid and token == "test-token":
        decoded = {"uid": emulated_uid, "email": f"{emulated_uid}@local", "name": "Test"}
    else:
        try:
            if not firebase_admin._apps:  # type: ignore[attr-defined]
                firebase_admin.initialize_app()
            decoded = auth.verify_id_token(token, clock_skew_seconds=30)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to verify token: %s", exc)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    firebase_uid = decoded.get("uid")
    email = decoded.get("email")
    name = decoded.get("name", email)
    if not firebase_uid or not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = await session.scalar(select(User).where(User.firebase_uid == firebase_uid))
    if user:
        user.email = email
        user.name = name
    else:
        user = User(firebase_uid=firebase_uid, email=email, name=name)
        session.add(user)
        org = await session.scalar(select(Organization))
        if org:
            session.add(OrgMembership(organization_id=org.id, user=user))
    await session.commit()
    await session.refresh(user)
    return user
