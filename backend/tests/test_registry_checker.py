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


def test_irr_records_structure_finds_origin():
    payload = {
        "data": {
            "irr_records": [
                [
                    {"key": "route", "value": "193.0.6.0/24"},
                    {"key": "origin", "value": "as3333"},
                ]
            ]
        }
    }
    assert RegistryChecker()._extract_route_origins(payload) == {"AS3333"}


def test_fields_structure_finds_origin():
    payload = {
        "data": {
            "records": [
                {
                    "type": "route",
                    "fields": [
                        {"key": "route", "value": "193.0.6.0/24"},
                        {"key": "origin", "value": "3333"},
                    ],
                }
            ]
        }
    }
    assert RegistryChecker()._extract_route_origins(payload) == {"AS3333"}


def test_nested_structure_finds_origin():
    payload = {
        "data": {
            "records": [
                [
                    [
                        {"key": "route6", "value": "2001:db8::/32"},
                        {"key": "origin", "value": "AS3333"},
                    ]
                ]
            ]
        }
    }
    assert RegistryChecker()._extract_route_origins(payload) == {"AS3333"}


def test_origin_without_route_is_ignored():
    payload = {"data": {"records": [[{"key": "origin", "value": "AS3333"}]]}}
    assert RegistryChecker()._extract_route_origins(payload) == set()


def test_route_without_origin_has_no_origin():
    payload = {"data": {"records": [[{"key": "route", "value": "193.0.6.0/24"}]]}}
    assert RegistryChecker()._extract_route_origins(payload) == set()


def test_string_origin_extraction_requires_route_in_same_record():
    payload = {
        "data": {
            "records": [
                [{"key": "remarks", "value": "route: 193.0.6.0/24 origin: AS3333"}],
                [{"key": "remarks", "value": "origin: AS64500"}],
            ]
        }
    }
    assert RegistryChecker()._extract_route_origins(payload) == {"AS3333"}


def test_unknown_structure_does_not_crash_and_is_warning_with_data():
    payload = {"data": {"records": [{"unexpected": {"nested": 1}}]}}
    result = RegistryChecker().check("193.0.6.0/24", "AS3333", payload)
    assert result["status"] == "WARNING"
