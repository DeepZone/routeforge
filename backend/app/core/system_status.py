from __future__ import annotations

from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
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


def _migration_snapshot(engine: Engine) -> dict:
    payload = {"schema_version": "unknown", "migration_head": "unknown", "migration_status": "unknown"}
    try:
        alembic_ini = Path(__file__).resolve().parents[2] / "alembic.ini"
        cfg = Config(str(alembic_ini))
        cfg.set_main_option("script_location", str(Path(__file__).resolve().parents[2] / "alembic"))
        cfg.set_main_option("sqlalchemy.url", settings.database_url)
        script = ScriptDirectory.from_config(cfg)
        head = script.get_current_head()
        payload["migration_head"] = head or "unknown"

        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current = context.get_current_revision()
        payload["schema_version"] = current or "unknown"

        if payload["schema_version"] == "unknown" or payload["migration_head"] == "unknown":
            payload["migration_status"] = "unknown"
        elif payload["schema_version"] == payload["migration_head"]:
            payload["migration_status"] = "up_to_date"
        else:
            payload["migration_status"] = "behind"
    except Exception as exc:
        payload["migration_status"] = "unknown"
        payload["migration_message"] = _safe_error_message(exc)
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            has_alembic_version = "alembic_version" in tables
        if not has_alembic_version and tables:
            payload["schema_version"] = "unknown"
            if payload["migration_head"] != "unknown":
                payload["migration_status"] = "behind"
                payload["migration_message"] = "alembic_version table is missing while database tables exist"
            else:
                payload["migration_status"] = "unknown"
    except Exception:
        pass
    return payload


def get_database_status(engine: Engine | None) -> dict:
    db_url = settings.database_url
    payload = {
        "status": "unknown",
        "type": database_type_from_url(db_url),
        "url_safe": safe_database_url(db_url),
        "schema_version": "unknown",
        "migration_status": "unknown",
        "migration_head": "unknown",
    }
    if engine is None:
        return payload
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        payload["status"] = "ok"
        payload.update(_migration_snapshot(engine))
    except Exception as exc:
        payload["status"] = "error"
        payload["migration_status"] = "error"
        payload["error_message"] = _safe_error_message(exc)
    return payload


def _security_warnings() -> list[str]:
    warnings: list[str] = []
    if settings.secret_key == "change-me":
        warnings.append("SECRET_KEY uses the default example value. Change it before production use.")
    if settings.postgres_password == "change-me":
        warnings.append("POSTGRES_PASSWORD uses the default example value. Change it before production use.")
    if not settings.cookie_secure:
        warnings.append("COOKIE_SECURE is false. Use true behind HTTPS in production.")
    if settings.cookie_samesite.lower() not in {"lax", "strict", "none"}:
        warnings.append("COOKIE_SAMESITE should be one of: lax, strict, none.")
    if settings.cookie_samesite.lower() == "none" and not settings.cookie_secure:
        warnings.append("COOKIE_SAMESITE=none requires COOKIE_SECURE=true in modern browsers.")
    if settings.cors_origins.strip() in {"*", ""}:
        warnings.append("CORS_ORIGINS is too permissive. Set explicit frontend origins.")
    return warnings


def build_system_status(engine: Engine | None) -> dict:
    database = get_database_status(engine)
    operational_warnings: list[str] = []
    if database.get("migration_status") != "up_to_date":
        operational_warnings.append(
            "Database schema is behind the application version. Run database migrations before using checks."
        )
    if database.get("migration_status") == "behind":
        operational_warnings.extend(
            [
                "Run: alembic current",
                "Run: alembic heads",
                "Run: alembic upgrade head",
            ]
        )

    return {
        "status": "ok",
        "name": settings.app_name,
        "version": "v1.0.2",
        "read_only": True,
        "mode": "demo" if settings.demo_mode else "live",
        "demo_mode": settings.demo_mode,
        "database": database,
        "api_proxy": {"status": "ok", "mode": "same-origin", "frontend_proxy_expected": True},
        "rpki": {"provider": settings.rpki_provider, "fallback_to_ripestat": settings.rpki_fallback_to_ripestat, "routinator_url": settings.rpki_routinator_url, "local_json_path": settings.rpki_local_json_path, "timeout_seconds": settings.rpki_provider_timeout_seconds},
        "bgp_visibility": {"providers": [x.strip() for x in settings.bgp_visibility_providers.split(",") if x.strip()], "require_source_agreement": settings.bgp_visibility_require_source_agreement, "min_confidence": settings.bgp_visibility_min_confidence},
        "alerts": {"webhook_enabled": settings.alert_webhook_enabled, "webhook_url_configured": bool(settings.alert_webhook_url), "on_status_change_only": settings.alert_on_status_change_only},
        "ripestat": {
            "cache_ttl_seconds": settings.cache_ttl_seconds,
            "timeout_seconds": settings.ripestat_timeout_seconds,
            "max_retries": settings.ripestat_max_retries,
            "retry_backoff_seconds": settings.ripestat_retry_backoff_seconds,
            "use_stale_cache_on_error": settings.ripestat_use_stale_cache_on_error,
        },
        "security_warnings": _security_warnings(),
        "operational_warnings": operational_warnings,
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
