from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.interfaces.http.main import correlate_request, unexpected_error_handler


def build_observability_client() -> TestClient:
    app = FastAPI()
    app.middleware("http")(correlate_request)
    app.add_exception_handler(Exception, unexpected_error_handler)

    @app.get("/ok")
    async def ok() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/failure")
    async def failure(_request: Request) -> None:
        raise RuntimeError("observable test failure")

    return TestClient(app, raise_server_exceptions=False)


def test_request_id_is_echoed_on_success() -> None:
    response = build_observability_client().get(
        "/ok", headers={"X-Request-Id": "character-acceptance-test"}
    )
    assert response.status_code == 200
    assert response.headers["X-Request-Id"] == "character-acceptance-test"


def test_unexpected_error_returns_correlated_problem_details() -> None:
    response = build_observability_client().get(
        "/failure", headers={"X-Request-Id": "character-failure-test"}
    )
    assert response.status_code == 500
    assert response.headers["X-Request-Id"] == "character-failure-test"
    assert response.json() == {
        "type": "urn:nexkosmo:problem:internal_server_error",
        "title": "Unexpected server error",
        "status": 500,
        "detail": "The server could not complete the request.",
        "instance": "/failure",
        "code": "internal_server_error",
        "trace_id": "character-failure-test",
    }
