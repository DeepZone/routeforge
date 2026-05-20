from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.config import settings


def safe_database_url(database_url: str) -> str:
    if not database_url:
        return "unknown"
    try:
        parsed = urlsplit(database_url)
        if parsed.scheme.startswith("sqlite"):
            return database_url
        if not parsed.scheme or not parsed.netloc:
            return "configured"

        host = parsed.hostname or ""
        port = f":{parsed.port}" if parsed.port else ""
        user = parsed.username or ""
        auth = f"{user}@" if user else ""
        netloc = f"{auth}{host}{port}"
        scheme = parsed.scheme.split("+", 1)[0]
        return urlunsplit((scheme, netloc, parsed.path, parsed.query, parsed.fragment))
    except Exception:
        return "configured"


def database_type_from_url(database_url: str) -> str:
    if not database_url:
        return "unknown"
    scheme = (urlsplit(database_url).scheme or "unknown").split("+", 1)[0]
    return scheme or "unknown"


def _safe_error_message(exc: Exception) -> str:
    message = str(exc)
    db_url = settings.database_url
    sanitized = safe_database_url(db_url)
    if db_url:
        message = message.replace(db_url, "[database-url]")
    if sanitized and sanitized != db_url:
        message = message.replace(sanitized, "[database-url]")
    return message[:300]


def get_database_status(engine: Engine | None) -> dict:
    db_url = settings.database_url
    payload = {
        "status": "unknown",
        "type": database_type_from_url(db_url),
        "url_safe": safe_database_url(db_url),
    }
    if engine is None:
        return payload
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        payload["status"] = "ok"
    except Exception as exc:
        payload["status"] = "error"
        payload["error_message"] = _safe_error_message(exc)
    return payload


def build_system_status(engine: Engine | None) -> dict:
    return {
        "status": "ok",
        "name": settings.app_name,
        "version": "v0.5.2-beta",
        "read_only": True,
        "mode": "demo" if settings.demo_mode else "live",
        "demo_mode": settings.demo_mode,
        "database": get_database_status(engine),
        "api_proxy": {"status": "ok", "mode": "same-origin", "frontend_proxy_expected": True},
        "ripestat": {
            "cache_ttl_seconds": settings.cache_ttl_seconds,
            "timeout_seconds": settings.ripestat_timeout_seconds,
            "max_retries": settings.ripestat_max_retries,
            "retry_backoff_seconds": settings.ripestat_retry_backoff_seconds,
            "use_stale_cache_on_error": settings.ripestat_use_stale_cache_on_error,
        },
        "features": {
            "asn_check": True,
            "prefix_check": True,
            "preflight": True,
            "reports": True,
            "exports": True,
            "data_source_diagnostics": True,
            "cache_freshness": True,
            "retry_resilience": True,
        },
    }
