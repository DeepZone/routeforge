from app.core.recommendations import evaluate_rpki_status


def test_rpki_valid_maps_to_ok():
    result = evaluate_rpki_status("valid", "193.0.6.0/24", "AS3333")
    assert result["status"] == "OK"


def test_rpki_invalid_maps_to_critical():
    result = evaluate_rpki_status("invalid", "193.0.6.0/24", "AS3333")
    assert result["status"] == "CRITICAL"


def test_rpki_not_found_maps_to_warning():
    result = evaluate_rpki_status("not_found", "193.0.6.0/24", "AS3333")
    assert result["status"] == "WARNING"


def test_rpki_without_origin_as_maps_to_warning():
    result = evaluate_rpki_status("valid", "193.0.6.0/24", None)
    assert result["status"] == "WARNING"


def test_rpki_none_maps_to_unknown():
    result = evaluate_rpki_status(None, "193.0.6.0/24", "AS3333")
    assert result["status"] == "UNKNOWN"
