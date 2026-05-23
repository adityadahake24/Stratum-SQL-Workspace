from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Platform
    secret_key: str = "change-me"
    encryption_key: str = "change-me-32-bytes-fernet-key"
    environment: str = "development"

    # Internal DB
    database_url: str = "postgresql+asyncpg://stratum:stratum@postgres:5432/stratum"

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # JWT
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days (refresh token)
    jwt_access_expire_minutes: int = 15  # 15 minutes (access token)

    # App
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"

    # Query limits
    max_query_runtime_seconds: int = 60
    max_result_rows: int = 1000
    max_rows_per_page: int = 100
    undo_max_rows_threshold: int = 100000

    # Connection tokens
    connection_token_expire_minutes: int = 30

    # Sentry
    sentry_dsn: Optional[str] = None

    # Logging
    log_level: str = "info"


settings = Settings()
