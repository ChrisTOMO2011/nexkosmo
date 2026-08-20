from types import SimpleNamespace
from uuid import UUID

import jwt
import pytest
from pydantic import ValidationError

from app.domain.enums import AgentKind
from app.infrastructure.auth import OidcJwksPrincipalVerifier
from app.infrastructure.config import Settings

ISSUER = "https://identity.test/"
AUDIENCE = "nexkosmo-test"
JWKS_URL = "https://identity.test/.well-known/jwks.json"


def settings_values(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "database_url": "postgresql+asyncpg://app:test@localhost/test",
        "migration_database_url": "postgresql+psycopg://owner:test@localhost/test",
        "audit_database_url": "postgresql+asyncpg://audit:test@localhost/test",
        "oidc_issuer": ISSUER,
        "oidc_audience": AUDIENCE,
        "oidc_jwks_url": JWKS_URL,
    }
    values.update(overrides)
    return values


class StubJwks:
    def get_signing_key_from_jwt(self, _token: str) -> SimpleNamespace:
        return SimpleNamespace(key="test-key")


@pytest.mark.asyncio
async def test_oidc_verifier_resolves_principal(monkeypatch: pytest.MonkeyPatch) -> None:
    verifier = OidcJwksPrincipalVerifier(issuer=ISSUER, audience=AUDIENCE, jwks_url=JWKS_URL)
    verifier._jwks = StubJwks()  # type: ignore[assignment]
    claims = {
        "sub": "10000000-0000-4000-8000-000000000001",
        "workspace_id": "10000000-0000-4000-8000-000000000002",
        "agent_id": "10000000-0000-4000-8000-000000000003",
        "agent_kind": "human",
    }
    monkeypatch.setattr(jwt, "decode", lambda *_args, **_kwargs: claims)

    principal = await verifier.verify("signed-token")

    assert principal.principal_id == UUID(claims["sub"])
    assert principal.workspace_id == UUID(claims["workspace_id"])
    assert principal.agent_kind is AgentKind.HUMAN


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [jwt.InvalidSignatureError("invalid"), jwt.ExpiredSignatureError("expired")],
)
async def test_oidc_verifier_rejects_invalid_or_expired_tokens(
    monkeypatch: pytest.MonkeyPatch, error: Exception
) -> None:
    verifier = OidcJwksPrincipalVerifier(issuer=ISSUER, audience=AUDIENCE, jwks_url=JWKS_URL)
    verifier._jwks = StubJwks()  # type: ignore[assignment]

    def reject(*_args: object, **_kwargs: object) -> None:
        raise error

    monkeypatch.setattr(jwt, "decode", reject)
    with pytest.raises(type(error)):
        await verifier.verify("bad-token")


def test_production_rejects_development_auth() -> None:
    with pytest.raises(ValidationError, match="AUTH_MODE=oidc"):
        Settings(**settings_values(app_env="production", auth_mode="development"))


def test_production_accepts_configured_oidc() -> None:
    value = Settings(**settings_values(app_env="production", auth_mode="oidc"))
    assert value.auth_mode == "oidc"
