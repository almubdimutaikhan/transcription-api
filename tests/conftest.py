import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

import app.database as db_module
from app.main import app as fastapi_app
from app.models.base import Base

TEST_DATABASE_URL = (
    'postgresql+asyncpg://postgres:postgres@localhost:5432/transcript_test_db'
)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_schema():
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()
    yield
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(setup_schema):
    """
    NullPool → fresh connection per request, no event-loop binding between tests.
    Truncate before each test for a clean slate.
    """
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    db_module.engine = engine
    db_module.AsyncSessionLocal = session_factory

    async with engine.begin() as conn:
        await conn.execute(
            text('TRUNCATE users, transcription_jobs, audit_logs RESTART IDENTITY CASCADE')
        )

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url='http://test'
    ) as ac:
        yield ac

    await engine.dispose()
