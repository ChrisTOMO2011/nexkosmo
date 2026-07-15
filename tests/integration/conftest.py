import os

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine


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
