from __future__ import annotations

from typing import Any

OK = "OK"
CACHE_HIT = "CACHE_HIT"
CACHE_MISS = "CACHE_MISS"
EMPTY_RESPONSE = "EMPTY_RESPONSE"
NO_DATA = "NO_DATA"
TIMEOUT = "TIMEOUT"
HTTP_ERROR = "HTTP_ERROR"
PARSE_ERROR = "PARSE_ERROR"
UNKNOWN_STRUCTURE = "UNKNOWN_STRUCTURE"
RATE_LIMITED = "RATE_LIMITED"
ERROR = "ERROR"

KNOWN_SOURCE_STATUSES = {
    OK,
    CACHE_HIT,
    CACHE_MISS,
    EMPTY_RESPONSE,
    NO_DATA,
    TIMEOUT,
    HTTP_ERROR,
    PARSE_ERROR,
    UNKNOWN_STRUCTURE,
    RATE_LIMITED,
    ERROR,
}


def make_cache_metadata(
    cached: bool | None,
    cache_age_seconds: int | None = None,
    cache_ttl_seconds: int | None = None,
    fetched_at: str | None = None,
    expires_at: str | None = None,
) -> dict[str, Any]:
    freshness = "UNKNOWN"
    if cached is False:
        freshness = "LIVE"
    elif cached is True and cache_age_seconds is not None and cache_ttl_seconds is not None:
        if cache_age_seconds <= cache_ttl_seconds * 0.75:
            freshness = "FRESH"
        elif cache_age_seconds <= cache_ttl_seconds:
            freshness = "EXPIRING_SOON"
        else:
            freshness = "STALE"

    return {
        "cached": cached,
        "cache_age_seconds": cache_age_seconds,
        "cache_ttl_seconds": cache_ttl_seconds,
        "fetched_at": fetched_at,
        "expires_at": expires_at,
        "freshness": freshness,
    }


def make_source_diagnostic(
    name: str,
    endpoint: str,
    status: str,
    message: str,
    duration_ms: int | None = None,
    cached: bool | None = None,
    cache_age_seconds: int | None = None,
    cache_ttl_seconds: int | None = None,
    fetched_at: str | None = None,
    expires_at: str | None = None,
    freshness: str | None = None,
    http_status: int | None = None,
    error_type: str | None = None,
    details: dict[str, Any] | None = None,
    retry_count: int | None = None,
    attempts: int | None = None,
    fallback_used: bool | None = None,
    fallback_reason: str | None = None,
    stale_cache_used: bool | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "endpoint": endpoint,
        "status": status,
        "message": message,
        "duration_ms": duration_ms,
        "cached": cached,
        "cache_age_seconds": cache_age_seconds,
        "cache_ttl_seconds": cache_ttl_seconds,
        "fetched_at": fetched_at,
        "expires_at": expires_at,
        "freshness": freshness,
        "http_status": http_status,
        "error_type": error_type,
        "details": details or {},
        "retry_count": retry_count,
        "attempts": attempts,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "stale_cache_used": stale_cache_used,
    }
