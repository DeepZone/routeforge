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


def make_source_diagnostic(
    name: str,
    endpoint: str,
    status: str,
    message: str,
    duration_ms: int | None = None,
    cached: bool | None = None,
    cache_age_seconds: int | None = None,
    http_status: int | None = None,
    error_type: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "endpoint": endpoint,
        "status": status,
        "message": message,
        "duration_ms": duration_ms,
        "cached": cached,
        "cache_age_seconds": cache_age_seconds,
        "http_status": http_status,
        "error_type": error_type,
        "details": details or {},
    }
