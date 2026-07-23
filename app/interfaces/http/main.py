from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.domain.errors import DomainError
from app.infrastructure.database import engine
from app.interfaces.http.problem import ProblemDetails

app = FastAPI(
    title="Nexkosmo Semantic Kernel",
    version="0.1.0",
    description="Milestone 1R++ controlled semantic-kernel proof.",
)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status = 403 if exc.code == "authorization_denied" else 409
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
async def ready() -> dict[str, str]:
    async with engine.connect() as connection:
        await connection.execute(text("select 1"))
    return {"status": "ready"}
