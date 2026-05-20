from app.config import Settings
from app.services.ripe_stat_client import RipeStatClient


class DummyQuery:
    def filter(self, *_args, **_kwargs):
        return self

    def first(self):
        return None


class DummyDb:
    def query(self, *_args, **_kwargs):
        return DummyQuery()

    def add(self, *_args, **_kwargs):
        return None

    def commit(self):
        return None


def test_demo_mode_diagnostics_live(monkeypatch):
    import app.config as config

    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ROUTEFORGE_DEMO_MODE=True))
    from app.services import ripe_stat_client as module

    client = RipeStatClient(DummyDb())
    _payload, diag = client.get_with_diagnostics('as-overview', {'resource': 'AS3320'})
    assert diag['cached'] is False
    assert diag['freshness'] == 'LIVE'
    assert diag['message'] == 'Demo data returned'


def test_cached_response_has_age(monkeypatch):
    import app.config as config

    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ROUTEFORGE_DEMO_MODE=False))
    from app.services import ripe_stat_client as module

    monkeypatch.setattr(module, 'get_cached', lambda *_args, **_kwargs: {'payload': {'data': {}}, 'fetched_at': '2026-05-20T00:00:00+00:00', 'ttl_seconds': 900})
    client = RipeStatClient(DummyDb())
    _payload, diag = client.get_with_diagnostics('as-overview', {'resource': 'AS3320'})
    assert diag['cached'] is True
    assert isinstance(diag['cache_age_seconds'], int)
    assert diag['cache_ttl_seconds'] == 900
