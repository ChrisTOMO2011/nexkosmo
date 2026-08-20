from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError, PyJWKClientError

from app.application.character_service import CharacterApplicationService
from app.application.environment_service import EnvironmentApplicationService
from app.application.project_service import ProjectProductionApplicationService
from app.domain.enums import AgentKind
from app.domain.types import Principal
from app.infrastructure.auth import OidcJwksPrincipalVerifier
from app.infrastructure.config import Settings, settings
from app.infrastructure.database import audit_session_factory, session_factory
from app.infrastructure.operational_adapters import (
    AuditDeliveryCoordinator,
    SqlAlchemyAuditAdapter,
    SqlAlchemyIdempotencyAdapter,
)
from app.infrastructure.uow import SqlAlchemyUnitOfWorkFactory

bearer = HTTPBearer(auto_error=False)


@lru_cache
def principal_verifier() -> OidcJwksPrincipalVerifier:
    config = settings()
    return OidcJwksPrincipalVerifier(
        issuer=config.oidc_issuer,
        audience=config.oidc_audience,
        jwks_url=config.oidc_jwks_url,
    )


@lru_cache
def character_application_service() -> CharacterApplicationService:
    audit_delivery = AuditDeliveryCoordinator(
        session_factory, SqlAlchemyAuditAdapter(audit_session_factory)
    )
    return CharacterApplicationService(
        SqlAlchemyUnitOfWorkFactory(session_factory),
        audit_delivery,
        SqlAlchemyIdempotencyAdapter(session_factory),
    )


@lru_cache
def environment_application_service() -> EnvironmentApplicationService:
    audit_delivery = AuditDeliveryCoordinator(
        session_factory, SqlAlchemyAuditAdapter(audit_session_factory)
    )
    return EnvironmentApplicationService(
        SqlAlchemyUnitOfWorkFactory(session_factory),
        audit_delivery,
        SqlAlchemyIdempotencyAdapter(session_factory),
    )


@lru_cache
def project_application_service() -> ProjectProductionApplicationService:
    audit_delivery = AuditDeliveryCoordinator(
        session_factory, SqlAlchemyAuditAdapter(audit_session_factory)
    )
    return ProjectProductionApplicationService(
        SqlAlchemyUnitOfWorkFactory(session_factory),
        audit_delivery,
        SqlAlchemyIdempotencyAdapter(session_factory),
    )


async def get_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    config: Annotated[Settings, Depends(settings)],
    x_workspace_id: Annotated[UUID | None, Header()] = None,
    x_principal_id: Annotated[UUID | None, Header()] = None,
    x_agent_id: Annotated[UUID | None, Header()] = None,
) -> Principal:
    if config.auth_mode == "development":
        return Principal(
            principal_id=x_principal_id or config.development_principal_id,
            workspace_id=x_workspace_id or config.development_workspace_id,
            agent_id=x_agent_id or config.development_agent_id,
            agent_kind=AgentKind.HUMAN,
        )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Bearer authentication is required.")
    try:
        return await principal_verifier().verify(credentials.credentials)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Bearer token is invalid or expired.") from exc
    except (PyJWKClientError, OSError) as exc:
        raise HTTPException(status_code=503, detail="Identity key service is unavailable.") from exc


PrincipalDependency = Annotated[Principal, Depends(get_principal)]
CharacterServiceDependency = Annotated[
    CharacterApplicationService, Depends(character_application_service)
]
EnvironmentServiceDependency = Annotated[
    EnvironmentApplicationService, Depends(environment_application_service)
]
ProjectServiceDependency = Annotated[
    ProjectProductionApplicationService, Depends(project_application_service)
]
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=200)]
