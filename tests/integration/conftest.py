import os

import pytest_asyncio
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


@pytest_asyncio.fixture
async def db():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is mandatory; blocking tests may not be skipped.")
    engine = create_async_engine(url, pool_pre_ping=True)
    try:
        async with engine.begin() as conn:
            yield conn
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def workspace_admin_engine():
    url = os.environ.get("MIGRATION_DATABASE_URL")
    if not url:
        raise RuntimeError(
            "MIGRATION_DATABASE_URL is mandatory for privileged test setup."
        )
    admin_url = make_url(url).set(drivername="postgresql+asyncpg")
    engine: AsyncEngine = create_async_engine(admin_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()
