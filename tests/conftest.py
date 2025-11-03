from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from types import SimpleNamespace

from app.db import models  # noqa: F401
from app.db.base import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.auth.dependencies import (
    get_current_user,
    require_admin,
    require_player_access,
)


@pytest.fixture()
def sync_engine():
    raw_url = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
    sync_url = raw_url.replace("sqlite+aiosqlite", "sqlite")
    engine = create_engine(
        sync_url,
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def session_factory(sync_engine) -> Iterator[sessionmaker[Session]]:
    factory = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False, future=True)
    yield factory


@pytest.fixture()
def db_session(session_factory) -> Iterator[Session]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(session_factory) -> Iterator[TestClient]:
    fake_user = SimpleNamespace(is_admin=True, player_id=None)

    def override_get_session():
        session = session_factory()
        try:
            yield session
            session.commit()
        finally:
            session.close()

    def override_get_current_user():
        return fake_user

    def override_require_player_access(player_id: int | None = None):
        return fake_user

    def override_require_admin():
        return fake_user

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[require_player_access] = override_require_player_access
    app.dependency_overrides[require_admin] = override_require_admin
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture()
async def async_session() -> AsyncIterator[AsyncSession]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async with session_maker() as session:
        yield session

    await engine.dispose()
