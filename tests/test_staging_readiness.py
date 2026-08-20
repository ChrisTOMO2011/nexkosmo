from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.infrastructure.audit_delivery import retry_delay_seconds
from app.infrastructure.auth import principal_from_claims
from app.infrastructure.config import Settings
from app.infrastructure.readiness import ReadinessService


def _settings(**overrides: Any) -> Settings:
    values: dict[str, Any] = {
        "app_env": "test",
        "deployment_release": "test-release",
        "expected_migration_head": "0005_staging_readiness",
        "database_url": "postgresql+asyncpg://app:test@localhost/nexkosmo",
        "migration_database_url": "postgresql+psycopg://owner:test@localhost/nexkosmo",
        "audit_database_url": "postgresql+asyncpg://audit:test@localhost/nexkosmo",
        "oidc_issuer": "https://identity.example.test/",
        "oidc_audience": "nexkosmo-test",
        "oidc_jwks_url": "https://identity.example.test/jwks.json",
    }
    values.update(overrides)
    return Settings(**values)


def test_staging_oidc_configuration_fails_closed() -> None:
    with pytest.raises(ValidationError, match="configured for the deployed environment"):
        _settings(
            app_env="staging",
            deployment_release="staging-1",
            oidc_issuer="https://identity.example.invalid/",
        )
    with pytest.raises(ValidationError, match="DEPLOYMENT_RELEASE"):
        _settings(app_env="staging", deployment_release="development")


def test_oidc_claim_contract_requires_authority_context() -> None:
    claims = {
        "exp": 1,
        "iat": 1,
        "iss": "https://identity.example.test/",
        "aud": "nexkosmo-test",
        "sub": str(uuid4()),
        "jti": str(uuid4()),
        "workspace_id": str(uuid4()),
        "agent_id": str(uuid4()),
        "agent_kind": "human",
    }
    principal = principal_from_claims(claims)
    assert str(principal.workspace_id) == claims["workspace_id"]
    with pytest.raises(ValueError, match="workspace_id"):
        without_workspace = {
            key: value for key, value in claims.items() if key != "workspace_id"
        }
        principal_from_claims(without_workspace)


def test_audit_backoff_is_deterministic_and_bounded() -> None:
    assert [
        retry_delay_seconds(value, base_seconds=30, max_seconds=300)
        for value in range(1, 7)
    ] == [30, 60, 120, 240, 300, 300]


def test_operational_scripts_do_not_embed_identity_or_database_passwords() -> None:
    root = Path(__file__).resolve().parents[1]
    backup = (root / "scripts" / "backup_restore_rehearsal.sh").read_text()
    bootstrap = (root / "scripts" / "bootstrap_staging_workspace.py").read_text()
    assert "PGPASSWORD=change_owner" not in backup
    assert "BACKUP_DATABASE_PASSWORD" in backup
    assert 'parser.add_argument("--owner-principal-id", required=True' in bootstrap
    assert 'parser.add_argument("--owner-agent-id", required=True' in bootstrap
    assert "christopher" not in bootstrap.lower()
    assert "the-last-dawn" not in bootstrap.lower()


class _Connection:
    def __init__(self, migration_head: str | None = None) -> None:
        self.migration_head = migration_head

    async def __aenter__(self) -> "_Connection":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def execute(self, *_: object) -> None:
        return None

    async def scalar(self, *_: object) -> str | None:
        return self.migration_head


class _Engine:
    def __init__(self, migration_head: str | None = None) -> None:
        self.connection = _Connection(migration_head)

    def connect(self) -> _Connection:
        return self.connection


@pytest.mark.asyncio
async def test_readiness_blocks_on_migration_head_mismatch() -> None:
    service = ReadinessService(
        _Engine("0004_character_foundation"),  # type: ignore[arg-type]
        _Engine(),  # type: ignore[arg-type]
        _settings(),
    )
    result = await service.check()
    assert result.ready is False
    assert result.checks["migration_head"]["matches"] is False
    assert result.checks["outbox"]["mode"] == "durable-storage-only"
