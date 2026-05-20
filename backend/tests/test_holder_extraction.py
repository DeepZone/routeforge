from app.core.holder_extraction import extract_holder


def test_holder_direct():
    assert extract_holder({"holder": "RIPE NCC"})["holder"] == "RIPE NCC"


def test_organisation_priority():
    result = extract_holder({"name": "Fallback"}, {"organisation": "Demo Org"})
    assert result["holder"] == "Demo Org"
    assert result["holder_confidence"] == "high"


def test_org_name():
    assert extract_holder({"org-name": "Org Name"})["holder"] == "Org Name"


def test_as_name():
    assert extract_holder({"as-name": "AS-DEMO"})["holder"] == "AS-DEMO"


def test_netname_fallback():
    assert extract_holder({"netname": "NET-DEMO"})["holder"] == "NET-DEMO"


def test_nested_structure():
    result = extract_holder({"data": {"objects": [{"attributes": {"organisation": "Nested Org"}}]}})
    assert result["holder"] == "Nested Org"


def test_unknown_empty():
    assert extract_holder({})["holder"] == "Unknown"


def test_skip_abuse_admin_tech():
    assert extract_holder({"abuse-c": "X", "admin-c": "Y", "tech-c": "Z"})["holder"] == "Unknown"
