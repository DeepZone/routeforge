import pytest

from app.core.normalize import format_asn, normalize_asn


def test_normalize_asn():
    assert normalize_asn("AS3320") == 3320
    assert normalize_asn(" 3320 ") == 3320


def test_normalize_asn_rejects_invalid_prefix():
    with pytest.raises(ValueError):
        normalize_asn("A3320")


def test_format_asn():
    assert format_asn(3333) == "AS3333"
