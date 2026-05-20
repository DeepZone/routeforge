from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RouteForge"
    environment: str = "development"
    database_url: str = "sqlite:///./routeforge.db"
    ripestat_base_url: str = "https://stat.ripe.net/data"
    http_timeout_seconds: int = 10
    ripestat_timeout_seconds: float = 10
    ripestat_max_retries: int = 1
    ripestat_retry_backoff_seconds: float = 0.5
    ripestat_use_stale_cache_on_error: bool = True
    cache_ttl_seconds: int = Field(default=900, validation_alias="RIPESTAT_CACHE_TTL_SECONDS")
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    demo_mode: bool = Field(default=False, validation_alias="ROUTEFORGE_DEMO_MODE")
    log_level: str = "INFO"
    postgres_password: str = Field(default="", validation_alias="POSTGRES_PASSWORD")
    secret_key: str = Field(default="change-me", validation_alias="SECRET_KEY")
    session_cookie_name: str = Field(default="routeforge_session", validation_alias="SESSION_COOKIE_NAME")
    session_expire_hours: int = Field(default=12, validation_alias="SESSION_EXPIRE_HOURS")
    cookie_secure: bool = Field(default=False, validation_alias="COOKIE_SECURE")
    cookie_samesite: str = Field(default="lax", validation_alias="COOKIE_SAMESITE")
    allow_sqlite_create_all: bool = Field(default=True, validation_alias="ALLOW_SQLITE_CREATE_ALL")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
