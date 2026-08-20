import asyncio
from typing import Any, Protocol
from uuid import UUID

import jwt
from jwt import PyJWKClient

from app.domain.enums import AgentKind
from app.domain.types import Principal


class PrincipalVerifier(Protocol):
    async def verify(self, bearer_token: str) -> Principal: ...


class OidcJwksPrincipalVerifier:
    def __init__(self, *, issuer: str, audience: str, jwks_url: str) -> None:
        self._issuer = issuer
        self._audience = audience
        self._jwks = PyJWKClient(jwks_url)

    async def verify(self, bearer_token: str) -> Principal:
        signing_key = await asyncio.to_thread(
            self._jwks.get_signing_key_from_jwt, bearer_token
        )
        claims = jwt.decode(
            bearer_token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience=self._audience,
            issuer=self._issuer,
            options={
                "require": sorted(REQUIRED_AUTHORITY_CLAIMS)
            },
        )
        return principal_from_claims(claims)


REQUIRED_AUTHORITY_CLAIMS = frozenset(
    {
        "exp",
        "iat",
        "iss",
        "aud",
        "sub",
        "jti",
        "workspace_id",
        "agent_id",
        "agent_kind",
    }
)


def principal_from_claims(claims: dict[str, Any]) -> Principal:
    missing = REQUIRED_AUTHORITY_CLAIMS.difference(claims)
    if missing:
        raise ValueError(f"OIDC access token is missing required claims: {sorted(missing)}")
    memberships = claims.get("memberships", [])
    delegated_actions = claims.get("delegated_actions", [])
    if not isinstance(memberships, list) or not isinstance(delegated_actions, list):
        raise ValueError("Optional authority claims must be arrays.")
    return Principal(
        principal_id=UUID(str(claims["sub"])),
        workspace_id=UUID(str(claims["workspace_id"])),
        agent_id=UUID(str(claims["agent_id"])),
        agent_kind=AgentKind(str(claims["agent_kind"])),
        memberships=frozenset(UUID(str(value)) for value in memberships),
        delegated_actions=frozenset(str(value) for value in delegated_actions),
    )
