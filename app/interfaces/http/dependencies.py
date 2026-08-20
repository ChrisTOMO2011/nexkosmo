from functools import lru_cache
from typing import Annotated, cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.character_service import CharacterService
from app.application.operational_service import OperationalStatusService
from app.application.ports import UnitOfWorkFactory
from app.application.project_service import ProjectService
from app.domain.types import Principal
from app.infrastructure.audit_delivery import (
    SqlAuditDeliveryDispatcher,
    SqlIndependentAuditPort,
)
from app.infrastructure.auth import OidcJwksPrincipalVerifier, PrincipalVerifier
from app.infrastructure.config import settings
from app.infrastructure.database import (
    audit_engine,
    audit_session_factory,
    engine,
    session_factory,
)
from app.infrastructure.idempotency import SqlTransactionalIdempotency
from app.infrastructure.readiness import ReadinessService
from app.infrastructure.uow import SqlAlchemyUnitOfWork

_bearer = HTTPBearer(auto_error=False)


@lru_cache
def principal_verifier() -> PrincipalVerifier:
    config = settings()
    return OidcJwksPrincipalVerifier(
        issuer=config.oidc_issuer,
        audience=config.oidc_audience,
        jwks_url=config.oidc_jwks_url,
    )


async def get_principal(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[PrincipalVerifier, Depends(principal_verifier)],
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication is required.",
        )
    try:
        principal = await verifier.verify(credentials.credentials)
        request.state.principal = principal
        return principal
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication failed.",
        ) from exc


@lru_cache
def project_service() -> ProjectService:
    config = settings()
    independent_audit = SqlIndependentAuditPort(audit_session_factory)
    audit_delivery = SqlAuditDeliveryDispatcher(
        session_factory,
        independent_audit,
        max_attempts=config.audit_retry_max_attempts,
        base_delay_seconds=config.audit_retry_base_seconds,
        max_delay_seconds=config.audit_retry_max_seconds,
    )
    uow_factory = cast(
        UnitOfWorkFactory,
        lambda principal: SqlAlchemyUnitOfWork(session_factory, principal),
    )
    return ProjectService(
        uow_factory,
        SqlTransactionalIdempotency(session_factory),
        audit_delivery,
    )


@lru_cache
def character_service() -> CharacterService:
    config = settings()
    independent_audit = SqlIndependentAuditPort(audit_session_factory)
    audit_delivery = SqlAuditDeliveryDispatcher(
        session_factory,
        independent_audit,
        max_attempts=config.audit_retry_max_attempts,
        base_delay_seconds=config.audit_retry_base_seconds,
        max_delay_seconds=config.audit_retry_max_seconds,
    )
    uow_factory = cast(
        UnitOfWorkFactory,
        lambda principal: SqlAlchemyUnitOfWork(session_factory, principal),
    )
    return CharacterService(
        uow_factory,
        SqlTransactionalIdempotency(session_factory),
        audit_delivery,
    )


@lru_cache
def operational_status_service() -> OperationalStatusService:
    uow_factory = cast(
        UnitOfWorkFactory,
        lambda principal: SqlAlchemyUnitOfWork(session_factory, principal),
    )
    return OperationalStatusService(uow_factory)


@lru_cache
def readiness_service() -> ReadinessService:
    return ReadinessService(engine, audit_engine, settings())


PrincipalDependency = Annotated[Principal, Depends(get_principal)]
ProjectServiceDependency = Annotated[ProjectService, Depends(project_service)]
CharacterServiceDependency = Annotated[CharacterService, Depends(character_service)]
OperationalStatusServiceDependency = Annotated[
    OperationalStatusService, Depends(operational_status_service)
]
ReadinessServiceDependency = Annotated[ReadinessService, Depends(readiness_service)]
