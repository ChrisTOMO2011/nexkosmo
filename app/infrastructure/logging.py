import logging
import re
from time import perf_counter
from uuid import uuid4

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.infrastructure.config import Settings

_REQUEST_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def configure_logging(config: Settings) -> None:
    logging.basicConfig(level=config.log_level.upper(), format="%(message)s")
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.log_level.upper(), logging.INFO)
        ),
    )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, *, release: str) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._release = release
        self._logger = structlog.get_logger("nexkosmo.http")

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        supplied = request.headers.get("x-request-id", "")
        request_id = supplied if _REQUEST_ID.fullmatch(supplied) else str(uuid4())
        request.state.request_id = request_id
        started = perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            principal = getattr(request.state, "principal", None)
            route = request.scope.get("route")
            route_path = getattr(route, "path", request.url.path)
            self._logger.info(
                "http_request_completed",
                request_id=request_id,
                release=self._release,
                method=request.method,
                route=route_path,
                status=status_code,
                latency_ms=round((perf_counter() - started) * 1000, 2),
                workspace_id=str(principal.workspace_id) if principal else None,
                principal_id=str(principal.principal_id) if principal else None,
                agent_id=str(principal.agent_id) if principal else None,
            )
