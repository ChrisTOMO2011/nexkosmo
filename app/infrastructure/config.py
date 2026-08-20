from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    deployment_release: str = "development"
    expected_migration_head: str = "0005_staging_readiness"
    database_url: str
    migration_database_url: str
    audit_database_url: str
    oidc_issuer: str
    oidc_audience: str
    oidc_jwks_url: str
    log_level: str = "INFO"
    audit_retry_max_attempts: int = Field(default=8, ge=1, le=20)
    audit_retry_base_seconds: int = Field(default=30, ge=1, le=3600)
    audit_retry_max_seconds: int = Field(default=3600, ge=1, le=86400)
    outbox_mode: Literal["durable-storage-only"] = "durable-storage-only"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @model_validator(mode="after")
    def validate_runtime_contract(self) -> "Settings":
        environment = self.app_env.strip().lower()
        if environment not in {"development", "test", "staging", "production"}:
            raise ValueError("APP_ENV must be development, test, staging, or production.")
        if not self.oidc_audience.strip():
            raise ValueError("OIDC_AUDIENCE must not be empty.")
        for field_name, value in (
            ("OIDC_ISSUER", self.oidc_issuer),
            ("OIDC_JWKS_URL", self.oidc_jwks_url),
        ):
            parsed = urlparse(value)
            if parsed.scheme != "https" or not parsed.netloc:
                raise ValueError(f"{field_name} must be an absolute HTTPS URL.")
            placeholder_host = parsed.hostname and parsed.hostname.endswith(".invalid")
            if environment in {"staging", "production"} and placeholder_host:
                raise ValueError(f"{field_name} must be configured for the deployed environment.")
        if environment in {"staging", "production"} and self.deployment_release in {
            "",
            "development",
        }:
            raise ValueError("DEPLOYMENT_RELEASE is required outside development and test.")
        if self.audit_retry_max_seconds < self.audit_retry_base_seconds:
            raise ValueError("AUDIT_RETRY_MAX_SECONDS must not be below the base delay.")
        return self


@lru_cache
def settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
