from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.config import settings

_cfg = settings()

engine: AsyncEngine = create_async_engine(
    _cfg.database_url,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
)
audit_engine: AsyncEngine = create_async_engine(
    _cfg.audit_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
)

session_factory = async_sessionmaker(engine, expire_on_commit=False)
audit_session_factory = async_sessionmaker(audit_engine, expire_on_commit=False)
