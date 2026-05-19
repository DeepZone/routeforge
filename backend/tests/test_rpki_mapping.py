from app.core.status import CheckStatus
from app.services.rpki_checker import map_rpki


def test_rpki_mapping():
    assert map_rpki("valid") == CheckStatus.OK
    assert map_rpki("invalid") == CheckStatus.CRITICAL
    assert map_rpki("not-found") == CheckStatus.WARNING
    assert map_rpki(None) == CheckStatus.UNKNOWN
