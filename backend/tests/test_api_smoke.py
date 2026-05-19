import importlib

from fastapi.testclient import TestClient


def _client() -> TestClient:
    import app.config as config

    config.settings = config.Settings(_env_file=None, ROUTEFORGE_DEMO_MODE=True)
    import app.main as main_module
    import app.database as database

    importlib.reload(main_module)
    database.Base.metadata.create_all(bind=database.engine)
    return TestClient(main_module.app)


def test_health() -> None:
    client = _client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json().get('status') == 'ok'


def test_prefix_check_without_origin_as() -> None:
    client = _client()
    response = client.post('/api/check/prefix', json={'prefix': '193.0.6.0/24'})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    assert payload.get('status') in {'OK', 'WARNING', 'CRITICAL', 'UNKNOWN'}
    assert payload.get('summary')
    assert isinstance(payload.get('details'), dict)
    assert payload.get('markdown')
    assert payload.get('html')


def test_asn_check() -> None:
    client = _client()
    response = client.post('/api/check/asn', json={'asn': 'AS3320'})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    details = payload.get('details', {})
    assert details.get('rpki_applicable') is False or details.get('rpki_explanation')
    assert 'extracted_prefixes' in details


def test_asn_rpki_batch() -> None:
    client = _client()
    response = client.post('/api/check/asn-rpki', json={'asn': 'AS3320', 'limit': 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    details = payload.get('details', {})
    assert isinstance(details.get('rpki_summary'), dict)
    assert isinstance(details.get('results'), list)
    assert int(details.get('checked_prefixes', 0)) <= 3


def test_system_info() -> None:
    client = _client()
    response = client.get('/api/system/info')
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('name') == 'RouteForge'
    assert payload.get('read_only') is True


def test_reports_list_empty_or_present() -> None:
    client = _client()
    response = client.get('/api/reports')
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
