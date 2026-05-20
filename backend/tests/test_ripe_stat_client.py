import httpx

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


def _resp(code=200, payload=None, headers=None):
    req = httpx.Request('GET', 'https://x')
    return httpx.Response(code, json=payload or {'data': {'ok': True}}, headers=headers, request=req)


def test_demo_mode_diagnostics_live(monkeypatch):
    import app.config as config
    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ROUTEFORGE_DEMO_MODE=True))
    client = RipeStatClient(DummyDb())
    _, diag = client.get_with_diagnostics('as-overview', {'resource': 'AS3320'})
    assert diag['attempts'] == 1 and diag['retry_count'] == 0


def test_timeout_then_success(monkeypatch):
    import app.config as config
    from app.services import ripe_stat_client as module
    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ROUTEFORGE_DEMO_MODE=False, ripestat_max_retries=1))
    calls = {'n': 0}
    def fake_get(self, *_a, **_k):
        calls['n'] += 1
        if calls['n'] == 1:
            raise httpx.TimeoutException('timeout')
        return _resp()
    monkeypatch.setattr(httpx.Client, 'get', fake_get)
    monkeypatch.setattr(module, 'set_cached', lambda *_a, **_k: None)
    payload, diag = RipeStatClient(DummyDb()).get_with_diagnostics('routing-status', {'resource': '1.1.1.0/24'}, force_refresh=True)
    assert payload is not None and diag['status'] == 'OK' and diag['attempts'] == 2 and diag['retry_count'] == 1


def test_503_then_success(monkeypatch):
    import app.config as config
    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ripestat_max_retries=1))
    seq = iter([_resp(503), _resp(200)])
    monkeypatch.setattr(httpx.Client, 'get', lambda self,*a,**k: next(seq))
    payload, diag = RipeStatClient(DummyDb()).get_with_diagnostics('whois', {'resource': '1.1.1.0/24'}, force_refresh=True)
    assert payload is not None and diag['attempts'] == 2 and diag['status'] == 'OK'


def test_404_no_retry(monkeypatch):
    import app.config as config
    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ripestat_max_retries=3))
    monkeypatch.setattr(httpx.Client, 'get', lambda self,*a,**k: _resp(404))
    payload, diag = RipeStatClient(DummyDb()).get_with_diagnostics('whois', {'resource': 'x'}, force_refresh=True)
    assert payload is None and diag['attempts'] == 1 and diag['status'] == 'HTTP_ERROR'


def test_429_rate_limited(monkeypatch):
    import app.config as config
    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ripestat_max_retries=3))
    monkeypatch.setattr(httpx.Client, 'get', lambda self,*a,**k: _resp(429, headers={'Retry-After': '60'}))
    _payload, diag = RipeStatClient(DummyDb()).get_with_diagnostics('whois', {'resource': 'x'}, force_refresh=True)
    assert diag['status'] == 'RATE_LIMITED' and diag['details'].get('retry_after') == '60'


def test_timeout_with_stale_cache(monkeypatch):
    import app.config as config
    from app.services import ripe_stat_client as module
    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ripestat_max_retries=0, ripestat_use_stale_cache_on_error=True))
    monkeypatch.setattr(httpx.Client, 'get', lambda self,*a,**k: (_ for _ in ()).throw(httpx.TimeoutException('t')))
    monkeypatch.setattr(module, 'get_cached', lambda *_a, **_k: {'payload': {'data': {'cached': True}}})
    payload, diag = RipeStatClient(DummyDb()).get_with_diagnostics('whois', {'resource': 'x'}, force_refresh=True)
    assert payload == {'data': {'cached': True}} and diag['fallback_used'] is True and diag['stale_cache_used'] is True and diag['freshness'] == 'STALE'


def test_timeout_no_cache(monkeypatch):
    import app.config as config
    monkeypatch.setattr(config, 'settings', Settings(_env_file=None, ripestat_max_retries=0, ripestat_use_stale_cache_on_error=True))
    monkeypatch.setattr(httpx.Client, 'get', lambda self,*a,**k: (_ for _ in ()).throw(httpx.TimeoutException('t')))
    payload, diag = RipeStatClient(DummyDb()).get_with_diagnostics('whois', {'resource': 'x'}, force_refresh=True)
    assert payload is None and diag['status'] == 'TIMEOUT'
