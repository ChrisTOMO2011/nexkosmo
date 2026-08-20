from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.errors import DomainError
from app.infrastructure.config import settings
from app.infrastructure.logging import RequestLoggingMiddleware, configure_logging
from app.interfaces.http.character_routes import router as character_router
from app.interfaces.http.dependencies import ReadinessServiceDependency
from app.interfaces.http.operational_routes import router as operational_router
from app.interfaces.http.problem import ProblemDetails
from app.interfaces.http.project_routes import router as project_router

app = FastAPI(
    title="Nexkosmo Semantic Kernel",
    version="0.1.0",
    description="Milestone 1R++ controlled semantic-kernel proof.",
)
_config = settings()
configure_logging(_config)
app.add_middleware(RequestLoggingMiddleware, release=_config.deployment_release)
app.include_router(project_router)
app.include_router(character_router)
app.include_router(operational_router)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    if exc.code == "authorization_denied":
        status = 403
    elif exc.code == "resource_not_found":
        status = 404
    else:
        status = 409
    body = ProblemDetails(
        type=f"urn:nexkosmo:problem:{exc.code}",
        title="Domain rule rejected the request",
        status=status,
        detail=str(exc),
        instance=str(request.url.path),
        code=exc.code,
    )
    return JSONResponse(status_code=status, content=body.model_dump())


@app.get("/health/live")
async def live() -> dict[str, str]:
    return {"status": "live"}


@app.get("/health/ready")
async def ready(service: ReadinessServiceDependency) -> JSONResponse:
    result = await service.check()
    status_code = 200 if result.ready else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if result.ready else "not_ready",
            "checks": result.checks,
        },
    )
