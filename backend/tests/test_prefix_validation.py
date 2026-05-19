from app.core.normalize import validate_prefix


def test_prefix_validation():
    assert validate_prefix("193.0.22.0/23") == "193.0.22.0/23"
    assert validate_prefix("2001:db8::/32") == "2001:db8::/32"
