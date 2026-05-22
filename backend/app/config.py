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

    rpki_provider: str = Field(default="ripestat", validation_alias="RPKI_PROVIDER")
    rpki_routinator_url: str = Field(default="http://routinator:8323", validation_alias="RPKI_ROUTINATOR_URL")
    rpki_local_json_path: str = Field(default="", validation_alias="RPKI_LOCAL_JSON_PATH")
    rpki_provider_timeout_seconds: float = Field(default=5, validation_alias="RPKI_PROVIDER_TIMEOUT_SECONDS")
    rpki_fallback_to_ripestat: bool = Field(default=True, validation_alias="RPKI_FALLBACK_TO_RIPESTAT")
    bgp_visibility_providers: str = Field(default="ripestat", validation_alias="BGP_VISIBILITY_PROVIDERS")
    bgp_generic_url_template: str = Field(default="", validation_alias="BGP_GENERIC_URL_TEMPLATE")
    bgp_provider_timeout_seconds: float = Field(default=5, validation_alias="BGP_PROVIDER_TIMEOUT_SECONDS")
    bgp_visibility_require_source_agreement: bool = Field(default=False, validation_alias="BGP_VISIBILITY_REQUIRE_SOURCE_AGREEMENT")
    bgp_visibility_min_confidence: int = Field(default=60, validation_alias="BGP_VISIBILITY_MIN_CONFIDENCE")
    post_change_default_recheck_minutes: str = Field(default="15,30,60", validation_alias="POST_CHANGE_DEFAULT_RECHECK_MINUTES")
    alert_webhook_enabled: bool = Field(default=False, validation_alias="ALERT_WEBHOOK_ENABLED")
    alert_webhook_url: str = Field(default="", validation_alias="ALERT_WEBHOOK_URL")
    alert_webhook_secret: str = Field(default="", validation_alias="ALERT_WEBHOOK_SECRET")
    alert_on_status_change_only: bool = Field(default=True, validation_alias="ALERT_ON_STATUS_CHANGE_ONLY")
    alert_webhook_timeout_seconds: float = Field(default=5, validation_alias="ALERT_WEBHOOK_TIMEOUT_SECONDS")
    alert_webhook_max_retries: int = Field(default=1, validation_alias="ALERT_WEBHOOK_MAX_RETRIES")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
