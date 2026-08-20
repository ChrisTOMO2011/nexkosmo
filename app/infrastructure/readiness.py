from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.infrastructure.config import Settings


@dataclass(frozen=True, slots=True)
class ReadinessResult:
    ready: bool
    checks: dict[str, Any]


class ReadinessService:
    def __init__(
        self,
        business_engine: AsyncEngine,
        audit_engine: AsyncEngine,
        config: Settings,
    ) -> None:
        self._business_engine = business_engine
        self._audit_engine = audit_engine
        self._config = config

    async def check(self) -> ReadinessResult:
        checks: dict[str, Any] = {
            "configuration": "valid",
            "release": self._config.deployment_release,
            "outbox": {
                "mode": self._config.outbox_mode,
                "published": False,
            },
        }
        ready = True
        try:
            async with self._business_engine.connect() as connection:
                await connection.execute(text("select 1"))
                migration_head = await connection.scalar(
                    text("select version_num from alembic_version")
                )
            checks["database"] = "reachable"
            checks["migration_head"] = {
                "expected": self._config.expected_migration_head,
                "actual": migration_head,
                "matches": migration_head == self._config.expected_migration_head,
            }
            ready = ready and migration_head == self._config.expected_migration_head
        except Exception as exc:
            checks["database"] = "unavailable"
            checks["database_error"] = type(exc).__name__
            ready = False

        try:
            async with self._audit_engine.connect() as connection:
                await connection.execute(text("select 1"))
            checks["independent_audit"] = "reachable"
        except Exception as exc:
            checks["independent_audit"] = "unavailable"
            checks["audit_error"] = type(exc).__name__
            ready = False
        return ReadinessResult(ready=ready, checks=checks)
