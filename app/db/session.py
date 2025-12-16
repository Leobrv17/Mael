from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


_engine: AsyncEngine | None = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine, SessionLocal

    if _engine is None:
        _engine = create_async_engine(settings.database_url, echo=False)
        SessionLocal = async_sessionmaker(bind=_engine, expire_on_commit=False, class_=AsyncSession)
    return _engine


async def get_session() -> AsyncSession:
    if SessionLocal is None:
        get_engine()

    assert SessionLocal is not None

    async with SessionLocal() as session:
        yield session
