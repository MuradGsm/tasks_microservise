import os
import sys
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

os.environ["POSTGRES_USER"] = "sjira"
os.environ["POSTGRES_PASSWORD"] = "sjira"
os.environ["POSTGRES_DB"] = "sjira_issue_test"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["PROJECT_SERVICE_URL"] = "http://fake-project-service"

import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.config.database import Base, get_session

TEST_DATABASE_URL = "postgresql+asyncpg://sjira:sjira@localhost/sjira_issue_test"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture
async def db_cleanup(session_factory):
    async with session_factory() as session:
        await session.execute(
            text(
                "TRUNCATE TABLE issuehistory, issuecomment, issue, issuecounter "
                "RESTART IDENTITY CASCADE"
            )
        )
        await session.commit()
    yield


@pytest_asyncio.fixture
async def project_service_mock():
    return {
        "project_key": "SJ",
        "has_project_access": True,
        "assignee_has_access": True,
    }


@pytest_asyncio.fixture
async def client(session_factory, db_cleanup, monkeypatch, project_service_mock):
    async def override_get_session():
        async with session_factory() as session:
            yield session

    async def fake_get_project_key(project_id: int, user_id: int) -> str:
        if not project_service_mock["has_project_access"]:
            raise HTTPException(
                status_code=404,
                detail="Project not found or access denied",
            )
        return project_service_mock["project_key"]

    async def fake_check_project_access(project_id: int, user_id: int) -> bool:
        return project_service_mock["assignee_has_access"]

    app.dependency_overrides[get_session] = override_get_session

    monkeypatch.setattr(
        "app.services.project_key.get_project_key",
        fake_get_project_key,
    )
    monkeypatch.setattr(
        "app.services.project_key.check_project_access",
        fake_check_project_access,
    )

    monkeypatch.setattr(
        "app.services.issues_service.get_project_key",
        fake_get_project_key,
    )
    monkeypatch.setattr(
        "app.services.issues_service.check_project_access",
        fake_check_project_access,
    )
    monkeypatch.setattr(
        "app.services.comments_service.get_project_key",
        fake_get_project_key,
    )
    monkeypatch.setattr(
        "app.services.history_service.get_project_key",
        fake_get_project_key,
    )

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()