from typing import Protocol
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
        signing_key = self._jwks.get_signing_key_from_jwt(bearer_token)
        claims = jwt.decode(
            bearer_token,
            signing_key.key,
            algorithms=["RS256", "ES256"],
            audience=self._audience,
            issuer=self._issuer,
            options={
                "require": ["exp", "iat", "iss", "aud", "sub", "jti", "workspace_id", "agent_id"]
            },
        )
        return Principal(
            principal_id=UUID(claims["sub"]),
            workspace_id=UUID(claims["workspace_id"]),
            agent_id=UUID(claims["agent_id"]),
            agent_kind=AgentKind(claims["agent_kind"]),
            memberships=frozenset(UUID(x) for x in claims.get("memberships", [])),
            delegated_actions=frozenset(claims.get("delegated_actions", [])),
        )
