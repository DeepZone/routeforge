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

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
