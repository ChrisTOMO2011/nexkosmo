from functools import lru_cache
from typing import Annotated, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.application.character_service import CharacterService
from app.application.ports import UnitOfWorkFactory
from app.application.project_service import ProjectService
from app.domain.types import Principal
from app.infrastructure.audit_delivery import (
    SqlAuditDeliveryDispatcher,
    SqlIndependentAuditPort,
)
from app.infrastructure.auth import OidcJwksPrincipalVerifier, PrincipalVerifier
from app.infrastructure.config import settings
from app.infrastructure.database import audit_session_factory, session_factory
from app.infrastructure.idempotency import SqlTransactionalIdempotency
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
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    verifier: Annotated[PrincipalVerifier, Depends(principal_verifier)],
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication is required.",
        )
    try:
        return await verifier.verify(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication failed.",
        ) from exc


@lru_cache
def project_service() -> ProjectService:
    independent_audit = SqlIndependentAuditPort(audit_session_factory)
    audit_delivery = SqlAuditDeliveryDispatcher(session_factory, independent_audit)
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
    independent_audit = SqlIndependentAuditPort(audit_session_factory)
    audit_delivery = SqlAuditDeliveryDispatcher(session_factory, independent_audit)
    uow_factory = cast(
        UnitOfWorkFactory,
        lambda principal: SqlAlchemyUnitOfWork(session_factory, principal),
    )
    return CharacterService(
        uow_factory,
        SqlTransactionalIdempotency(session_factory),
        audit_delivery,
    )


PrincipalDependency = Annotated[Principal, Depends(get_principal)]
ProjectServiceDependency = Annotated[ProjectService, Depends(project_service)]
CharacterServiceDependency = Annotated[CharacterService, Depends(character_service)]
