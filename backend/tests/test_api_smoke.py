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
    assert payload.get('details', {}).get('resource_holder')


def test_asn_check() -> None:
    client = _client()
    response = client.post('/api/check/asn', json={'asn': 'AS3320'})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    details = payload.get('details', {})
    assert details.get('rpki_applicable') is False or details.get('rpki_explanation')
    assert 'extracted_prefixes' in details
    assert details.get('resource_holder')


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


def test_preflight_check() -> None:
    client = _client()
    response = client.post('/api/check/preflight', json={'prefix': '192.0.2.0/24', 'planned_origin_as': 'AS3320'})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    checks = payload.get('checks', {})
    assert 'rpki' in checks
    assert 'registry' in checks
    assert 'routing_visibility' in checks
    assert payload.get('details', {}).get('preflight_mode') is True
    assert payload.get('details', {}).get('resource_holder')
    assert payload.get('details', {}).get('preflight_decision') in {'GO', 'CAUTION', 'NO-GO', 'UNKNOWN'}


def test_report_export_endpoints() -> None:
    client = _client()
    check_response = client.post('/api/check/prefix', json={'prefix': '193.0.6.0/24'})
    assert check_response.status_code == 200
    report_id = check_response.json().get('report_id')
    assert report_id

    summary_response = client.get(f'/api/reports/{report_id}/summary')
    assert summary_response.status_code == 200
    assert 'text/plain' in summary_response.headers.get('content-type', '')
    assert 'RouteForge' in summary_response.text
    assert 'Status:' in summary_response.text

    markdown_response = client.get(f'/api/reports/{report_id}/markdown')
    assert markdown_response.status_code == 200
    assert 'text/markdown' in markdown_response.headers.get('content-type', '')

    html_response = client.get(f'/api/reports/{report_id}/html')
    assert html_response.status_code == 200
    assert 'text/html' in html_response.headers.get('content-type', '')
