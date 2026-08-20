import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.responses import Response

from app.domain.errors import DomainError
from app.infrastructure.config import settings
from app.infrastructure.database import audit_engine, engine
from app.interfaces.http.character_routes import router as character_router
from app.interfaces.http.environment_routes import router as environment_router
from app.interfaces.http.problem import ProblemDetails
from app.interfaces.http.project_routes import router as project_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Nexkosmo Semantic Kernel",
    version="0.1.0",
    description="Milestone 1R++ controlled semantic-kernel proof.",
)
_config = settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in _config.cors_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Idempotency-Key",
        "X-Workspace-Id",
        "X-Principal-Id",
        "X-Agent-Id",
        "X-Request-Id",
    ],
)
app.include_router(character_router)
app.include_router(environment_router)
app.include_router(project_router)


def _request_id(request: Request) -> str:
    supplied = request.headers.get("X-Request-Id", "").strip()
    if (
        supplied
        and len(supplied) <= 128
        and all(character.isalnum() or character in "-_.:" for character in supplied)
    ):
        return supplied
    return str(uuid4())


@app.middleware("http")
async def correlate_request(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    trace_id = _request_id(request)
    request.state.trace_id = trace_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = trace_id
    return response


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status = {
        "authorization_denied": 403,
        "not_found": 404,
        "validation_failed": 422,
        "invariant_violation": 422,
        "concurrency_conflict": 409,
        "idempotency_conflict": 409,
    }.get(exc.code, 409)
    body = ProblemDetails(
        type=f"urn:nexkosmo:problem:{exc.code}",
        title="Domain rule rejected the request",
        status=status,
        detail=str(exc),
        instance=str(request.url.path),
        code=exc.code,
        trace_id=getattr(request.state, "trace_id", None),
    )
    return JSONResponse(status_code=status, content=body.model_dump())


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = getattr(request.state, "trace_id", str(uuid4()))
    logger.error(
        "Unhandled request failure trace_id=%s method=%s path=%s",
        trace_id,
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    body = ProblemDetails(
        type="urn:nexkosmo:problem:internal_server_error",
        title="Unexpected server error",
        status=500,
        detail="The server could not complete the request.",
        instance=str(request.url.path),
        code="internal_server_error",
        trace_id=trace_id,
    )
    return JSONResponse(
        status_code=500,
        content=body.model_dump(),
        headers={"X-Request-Id": trace_id},
    )


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready")
async def ready() -> dict[str, object]:
    try:
        async with engine.connect() as connection:
            revision = await connection.scalar(text("select version_num from alembic_version"))
        async with audit_engine.connect() as connection:
            await connection.execute(text("select 1"))
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database dependency is unavailable.") from exc
    if revision != _config.migration_head:
        raise HTTPException(
            status_code=503,
            detail=f"Database migration head is {revision!r}; expected {_config.migration_head!r}.",
        )
    return {
        "status": "ready",
        "database_revision": revision,
        "audit_database": "ready",
        "outbox_dispatcher": ("configured" if _config.outbox_dispatcher_enabled else "disabled"),
        "semantic_kernel": "deferred",
    }
