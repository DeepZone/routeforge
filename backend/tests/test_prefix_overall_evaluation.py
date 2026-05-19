from app.core.prefix_evaluation import evaluate_prefix_overall


def _check(status: str) -> dict:
    return {"status": status}


def test_rpki_ok_registry_ok_is_ok():
    result = evaluate_prefix_overall(_check("OK"), _check("OK"), "193.0.6.0/24", "AS3333")
    assert result["status"] == "OK"


def test_rpki_ok_registry_warning_is_warning():
    result = evaluate_prefix_overall(_check("OK"), _check("WARNING"), "193.0.6.0/24", "AS3333")
    assert result["status"] == "WARNING"


def test_rpki_critical_registry_ok_is_critical():
    result = evaluate_prefix_overall(_check("CRITICAL"), _check("OK"), "193.0.6.0/24", "AS3333")
    assert result["status"] == "CRITICAL"


def test_rpki_warning_registry_warning_is_warning():
    result = evaluate_prefix_overall(_check("WARNING"), _check("WARNING"), "193.0.6.0/24", "AS3333")
    assert result["status"] == "WARNING"


def test_rpki_unknown_registry_ok_is_warning():
    result = evaluate_prefix_overall(_check("UNKNOWN"), _check("OK"), "193.0.6.0/24", "AS3333")
    assert result["status"] == "WARNING"


def test_rpki_unknown_registry_unknown_is_unknown():
    result = evaluate_prefix_overall(_check("UNKNOWN"), _check("UNKNOWN"), "193.0.6.0/24", "AS3333")
    assert result["status"] == "UNKNOWN"


def test_registry_critical_rpki_ok_is_critical():
    result = evaluate_prefix_overall(_check("OK"), _check("CRITICAL"), "193.0.6.0/24", "AS3333")
    assert result["status"] == "CRITICAL"


def test_missing_origin_as_is_warning():
    result = evaluate_prefix_overall(_check("OK"), _check("OK"), "193.0.6.0/24", None)
    assert result["status"] == "WARNING"
