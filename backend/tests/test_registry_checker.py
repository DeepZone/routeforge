from app.services.registry_checker import RegistryChecker


def test_route_object_matching_origin_is_ok():
    payload = {
        "data": {
            "records": [
                [
                    {"key": "route", "value": "193.0.6.0/24"},
                    {"key": "origin", "value": "AS3333"},
                ]
            ]
        }
    }
    result = RegistryChecker().check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] == "OK"


def test_no_route_object_is_warning():
    payload = {"data": {"records": [[{"key": "descr", "value": "example"}]]}}
    result = RegistryChecker().check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] == "WARNING"


def test_route_object_origin_mismatch_is_critical():
    payload = {
        "data": {
            "records": [
                [
                    {"key": "route", "value": "193.0.6.0/24"},
                    {"key": "origin", "value": "AS64500"},
                ]
            ]
        }
    }
    result = RegistryChecker().check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] == "CRITICAL"


def test_empty_data_is_unknown():
    result = RegistryChecker().check("193.0.6.0/24", "AS3333", {})
    assert result["status"] == "UNKNOWN"
