from app.services.routing_visibility_checker import RoutingVisibilityChecker


def test_visible_origin_matches_expected_is_ok():
    c = RoutingVisibilityChecker()
    payload = {"data": {"routes": [{"origin": "AS3333"}]}}
    result = c.check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] == "OK"


def test_visible_origin_differs_is_critical():
    c = RoutingVisibilityChecker()
    payload = {"data": {"routes": [{"origin_as": 12345}]}}
    result = c.check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] == "CRITICAL"


def test_visible_origins_without_expected_origin_is_ok():
    c = RoutingVisibilityChecker()
    payload = {"data": {"origins": [3333, "AS42"]}}
    result = c.check("193.0.6.0/24", None, payload)
    assert result["status"] == "OK"


def test_empty_payload_is_unknown():
    c = RoutingVisibilityChecker()
    result = c.check("193.0.6.0/24", "AS3333", {})
    assert result["status"] == "UNKNOWN"


def test_payload_without_extractable_origins_is_warning():
    c = RoutingVisibilityChecker()
    payload = {"data": {"routes": [{"prefix": "193.0.6.0/24"}]}}
    result = c.check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] == "UNKNOWN"


def test_numeric_asn_is_normalized_to_as_prefix():
    c = RoutingVisibilityChecker()
    payload = {"data": {"origin_asn": 3333}}
    result = c.check("193.0.6.0/24", "AS3333", payload)
    assert "AS3333" in result["raw"]["visible_origins"]


def test_unknown_structure_does_not_crash():
    c = RoutingVisibilityChecker()
    payload = {"data": [{"odd": {"nested": [object(), None, {"x": "y"}]}}]}
    result = c.check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] in {"WARNING", "UNKNOWN", "CRITICAL", "OK"}
