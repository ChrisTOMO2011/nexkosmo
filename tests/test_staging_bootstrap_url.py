from sqlalchemy.engine import URL

from scripts.bootstrap_staging_workspace import _async_url


def test_async_url_preserves_credentials_without_rendering_password(caplog) -> None:
    synthetic_password = "synthetic-test-password"
    url = _async_url(
        "postgresql+psycopg://synthetic-owner:"
        f"{synthetic_password}@staging-db:5432/nexkosmo"
    )

    assert isinstance(url, URL)
    assert url.drivername == "postgresql+asyncpg"
    assert url.username == "synthetic-owner"
    assert url.password == synthetic_password
    assert url.host == "staging-db"
    assert url.database == "nexkosmo"
    assert synthetic_password not in str(url)
    assert synthetic_password not in caplog.text
