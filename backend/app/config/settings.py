"""Validated, environment-backed application configuration."""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Supported deployment environments."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """All backend settings loaded once from environment variables or ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Personal Assistant"
    app_version: str = "1.0.0"
    environment: Environment
    debug: bool = False
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    workers: int = Field(default=4, ge=1)
    log_level: str = "INFO"

    database_url: str
    postgres_db: str
    postgres_user: str
    postgres_password: SecretStr
    database_pool_size: int = Field(default=20, ge=1)
    database_max_overflow: int = Field(default=40, ge=0)
    redis_url: str
    redis_cache_ttl: int = Field(default=3600, ge=1)
    rabbitmq_url: str
    rabbitmq_exchange: str = "assistant.exchange"

    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = Field(default=15, ge=1)
    refresh_token_expire_days: int = Field(default=30, ge=1)
    password_hasher: str = "argon2"
    argon2_time_cost: int = Field(default=3, ge=1)
    argon2_memory_cost: int = Field(default=65536, ge=8192)
    argon2_parallelism: int = Field(default=4, ge=1)
    token_encryption_key: SecretStr

    google_client_id: str = ""
    google_client_secret: SecretStr | None = None
    google_redirect_uri: str = ""
    github_client_id: str = ""
    github_client_secret: SecretStr | None = None
    github_redirect_uri: str = ""
    microsoft_client_id: str = ""
    microsoft_client_secret: SecretStr | None = None
    microsoft_redirect_uri: str = ""
    slack_client_id: str = ""
    slack_client_secret: SecretStr | None = None
    slack_redirect_uri: str = ""
    jira_client_id: str = ""
    jira_client_secret: SecretStr | None = None
    jira_redirect_uri: str = ""

    ai_service_url: str
    ai_api_key: SecretStr | None = None
    grok_api_key: SecretStr | None = None
    xai_api_key: SecretStr | None = None
    ai_request_timeout: int = Field(default=120, ge=1)
    file_storage: str = "local"
    upload_directory: str = "uploads/"
    smtp_host: str = ""
    smtp_port: int = Field(default=587, ge=1, le=65535)
    smtp_username: str = ""
    smtp_password: SecretStr | None = None
    smtp_from: str = ""

    prometheus_enabled: bool = True
    metrics_path: str = "/metrics"
    log_format: str = "json"
    request_id_header: str = "X-Request-ID"
    cors_origins: list[str] = Field(default_factory=list)
    cors_allow_credentials: bool = True
    rate_limit_enabled: bool = True
    login_rate_limit: str = "5/minute"
    api_rate_limit: str = "100/minute"
    enable_voice: bool = False
    enable_file_upload: bool = True
    enable_notifications: bool = False
    enable_memory: bool = True
    enable_rag: bool = True

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("database_url", "redis_url", "rabbitmq_url", "ai_service_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        if "://" not in value:
            raise ValueError("must be an absolute URL")
        return value

    @model_validator(mode="after")
    def validate_security_configuration(self) -> Settings:
        if len(self.jwt_secret.get_secret_value()) < 32:
            raise ValueError("JWT_SECRET must contain at least 32 characters")
        if self.environment is Environment.PRODUCTION and self.debug:
            raise ValueError("DEBUG must be false in production")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the singleton validated settings instance."""

    # Values are intentionally supplied by Pydantic's environment source.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
