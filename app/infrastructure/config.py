from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str
    migration_database_url: str
    audit_database_url: str
    oidc_issuer: str
    oidc_audience: str
    oidc_jwks_url: str
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def settings() -> Settings:
    # BaseSettings supplies these required values from the environment at runtime.
    return Settings()  # type: ignore[call-arg]
