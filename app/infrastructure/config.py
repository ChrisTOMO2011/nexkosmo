from functools import lru_cache
from typing import Literal
from uuid import UUID

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: Literal["development", "test", "production"] = "development"
    database_url: str
    migration_database_url: str
    audit_database_url: str
    oidc_issuer: str
    oidc_audience: str
    oidc_jwks_url: str
    log_level: str = "INFO"
    auth_mode: Literal["oidc", "development"] = "development"
    development_workspace_id: UUID = UUID("00000000-0000-4000-8000-000000000001")
    development_principal_id: UUID = UUID("00000000-0000-4000-8000-000000000002")
    development_agent_id: UUID = UUID("00000000-0000-4000-8000-000000000003")
    cors_origins: str = "http://127.0.0.1:4173,http://localhost:4173"
    migration_head: str = "0011_environment_forest"
    outbox_dispatcher_enabled: bool = False
    outbox_poll_interval_seconds: float = 1.0
    outbox_batch_size: int = 25
    outbox_max_attempts: int = 8

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def reject_unsafe_production_configuration(self) -> "Settings":
        if self.app_env != "production":
            return self
        if self.auth_mode != "oidc":
            raise ValueError("Production requires AUTH_MODE=oidc.")
        oidc_values = (self.oidc_issuer, self.oidc_audience, self.oidc_jwks_url)
        if any(not value.strip() or "example.invalid" in value for value in oidc_values):
            raise ValueError("Production requires configured OIDC issuer, audience, and JWKS URL.")
        if not self.oidc_issuer.startswith("https://") or not self.oidc_jwks_url.startswith(
            "https://"
        ):
            raise ValueError("Production OIDC endpoints must use HTTPS.")
        return self


@lru_cache
def settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
