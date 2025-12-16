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
def test_engine(event_loop):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async def _init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    event_loop.run_until_complete(_init_models())
    yield engine
    event_loop.run_until_complete(engine.dispose())


@pytest.fixture(scope="session")
def session_factory(test_engine):
    return async_sessionmaker(bind=test_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def db_session(event_loop, session_factory):
    async def _get_session():
        async with session_factory() as session:
            yield session

    session_gen = _get_session()
    session = event_loop.run_until_complete(session_gen.__anext__())
    try:
        yield session
    finally:
        event_loop.run_until_complete(session.rollback())
        event_loop.run_until_complete(session_gen.aclose())


@pytest.fixture
def client(session_factory, monkeypatch):
    async def _get_db_override():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_override
    os.environ["FIREBASE_EMULATED_UID"] = "test-user"
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
