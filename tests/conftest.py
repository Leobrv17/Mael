import os
import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.db.session import Base
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    maker = async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def client(db_session, monkeypatch):
    async def _get_db_override():
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    os.environ["FIREBASE_EMULATED_UID"] = "test-user"
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
