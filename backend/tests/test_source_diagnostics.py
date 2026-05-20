from app.core.source_diagnostics import KNOWN_SOURCE_STATUSES, OK, TIMEOUT, make_source_diagnostic


def test_make_source_diagnostic_shape() -> None:
    d = make_source_diagnostic("RIPEstat routing-status", "routing-status", OK, "ok", duration_ms=12, cached=False)
    assert d["name"] == "RIPEstat routing-status"
    assert d["endpoint"] == "routing-status"
    assert d["status"] == OK
    assert d["duration_ms"] == 12
    assert d["cached"] is False
    assert isinstance(d["details"], dict)


def test_make_source_diagnostic_optional_defaults() -> None:
    d = make_source_diagnostic("x", "y", TIMEOUT, "timeout")
    assert d["duration_ms"] is None
    assert d["http_status"] is None
    assert d["error_type"] is None


def test_known_status_values_present() -> None:
    for value in [OK, TIMEOUT, "HTTP_ERROR", "PARSE_ERROR", "UNKNOWN_STRUCTURE", "RATE_LIMITED", "CACHE_HIT", "CACHE_MISS", "EMPTY_RESPONSE", "NO_DATA", "ERROR"]:
        assert value in KNOWN_SOURCE_STATUSES
