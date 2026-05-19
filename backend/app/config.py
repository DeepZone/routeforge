from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RouteForge"
    environment: str = "development"
    database_url: str = "sqlite:///./routeforge.db"
    ripestat_base_url: str = "https://stat.ripe.net/data"
    http_timeout_seconds: int = 10
    cache_ttl_seconds: int = 900
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
