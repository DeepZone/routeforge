import app.config as config
from app.core.system_status import safe_database_url

import importlib

from fastapi.testclient import TestClient


def _client(**overrides) -> TestClient:
    import app.config as config

    config.settings = config.Settings(_env_file=None, ROUTEFORGE_DEMO_MODE=True, **overrides)
    import app.main as main_module
    import app.database as database

    importlib.reload(main_module)
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    return TestClient(main_module.app)


def _setup_and_login(client: TestClient, username: str = "admin", password: str = "AdminPass123!") -> None:
    setup = client.post('/api/auth/setup', json={'username': username, 'email': 'admin@example.org', 'password': password, 'password_confirm': password})
    if setup.status_code == 403:
        login = client.post('/api/auth/login', json={'username': username, 'password': password})
        assert login.status_code == 200
        return
    assert setup.status_code == 200


def test_health() -> None:
    client = _client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json().get('status') == 'ok'


def test_prefix_check_without_origin_as() -> None:
    client = _client()
    _setup_and_login(client)
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
    assert any('attempts' in d for d in payload.get('details', {}).get('source_diagnostics', []) if isinstance(d, dict))


def test_asn_check() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.post('/api/check/asn', json={'asn': 'AS3320'})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    details = payload.get('details', {})
    assert details.get('rpki_applicable') is False or details.get('rpki_explanation')
    assert 'extracted_prefixes' in details
    assert details.get('rpki_batch', {}).get('available') is True
    assert details.get('resource_holder')
    assert any('attempts' in d for d in details.get('source_diagnostics', []) if isinstance(d, dict))


def test_asn_check_without_prefixes_has_batch_reason() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.post('/api/check/asn', json={'asn': 'AS4491'})
    assert response.status_code == 200
    details = response.json().get('details', {})
    rpki_batch = details.get('rpki_batch', {})
    assert rpki_batch.get('available') is False
    assert rpki_batch.get('reason_code')
    assert rpki_batch.get('message')


def test_asn_rpki_batch() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.post('/api/check/asn-rpki', json={'asn': 'AS3320', 'limit': 3})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    details = payload.get('details', {})
    assert isinstance(details.get('rpki_summary'), dict)
    assert isinstance(details.get('results'), list)
    assert int(details.get('checked_prefixes', 0)) <= 3


def test_asn_rpki_batch_without_prefixes() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.post('/api/check/asn-rpki', json={'asn': 'AS4491', 'limit': 25})
    assert response.status_code == 200
    payload = response.json()
    details = payload.get('details', {})
    assert payload.get('status') in {'UNKNOWN', 'WARNING'}
    assert details.get('checked_prefixes') == 0
    assert details.get('rpki_batch', {}).get('message')


def test_system_info() -> None:
    client = _client()
    response = client.get('/api/system/info')
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('name') == 'RouteForge'
    assert payload.get('read_only') is True


def test_reports_list_empty_or_present() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.get('/api/reports')
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)


def test_preflight_check() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.post('/api/check/preflight', json={'prefix': '192.0.2.0/24', 'planned_origin_as': 'AS3320'})
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('report_id')
    checks = payload.get('checks', {})
    assert 'rpki' in checks
    assert 'registry' in checks
    assert 'routing_visibility' in checks
    assert payload.get('details', {}).get('preflight_mode') is True
    assert isinstance(payload.get('details', {}).get('source_diagnostics'), list)
    assert any('attempts' in d for d in payload.get('details', {}).get('source_diagnostics', []) if isinstance(d, dict))
    assert payload.get('details', {}).get('resource_holder')
    assert payload.get('details', {}).get('preflight_decision') in {'GO', 'CAUTION', 'NO-GO', 'UNKNOWN'}


def test_report_export_endpoints() -> None:
    client = _client()
    _setup_and_login(client)
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


def test_report_export_not_found() -> None:
    client = _client()
    _setup_and_login(client)
    for endpoint in ('summary', 'markdown', 'html'):
        response = client.get(f'/api/reports/999999/{endpoint}')
        assert response.status_code == 404
        assert response.json().get('detail') == 'Report not found'


def test_system_status_endpoint() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.get('/api/system/status')
    assert response.status_code == 200
    payload = response.json()
    assert payload.get('version') == 'v0.7.1-beta'
    assert payload.get('read_only') is True
    assert payload.get('database', {}).get('status')
    assert payload.get('ripestat', {}).get('cache_ttl_seconds') is not None
    assert payload.get('features', {}).get('preflight') is True


def test_safe_database_url() -> None:
    assert safe_database_url('postgresql+psycopg://routeforge:secret@postgres:5432/routeforge') == 'postgresql://routeforge@postgres:5432/routeforge'
    assert safe_database_url('sqlite:////app/data/routeforge.db') == 'sqlite:////app/data/routeforge.db'
    assert safe_database_url('not a url') == 'configured'


def test_system_status_includes_migration_fields() -> None:
    client = _client()
    _setup_and_login(client)
    response = client.get('/api/system/status')
    assert response.status_code == 200
    database = response.json().get('database', {})
    assert 'schema_version' in database
    assert 'migration_status' in database
    assert 'migration_head' in database


def test_migration_status_unknown_does_not_crash() -> None:
    from app.core import system_status as ss

    class FakeBrokenEngine:
        def connect(self):
            raise RuntimeError('db down')

    payload = ss.get_database_status(FakeBrokenEngine())
    assert payload.get('status') == 'error'
    assert payload.get('migration_status') == 'error'


def test_setup_required_without_users() -> None:
    client = _client()
    response = client.get('/api/auth/setup-required')
    assert response.status_code == 200
    assert response.json().get('setup_required') is True


def test_asn_check_requires_authentication() -> None:
    client = _client()
    response = client.post('/api/check/asn', json={'asn': 'AS3320'})
    assert response.status_code == 401


def test_asn_check_forbidden_for_viewer() -> None:
    client = _client()
    _setup_and_login(client)
    create = client.post('/api/users', json={'username': 'viewer', 'email': 'viewer@example.org', 'password': 'ViewerPass123!', 'role': 'viewer'})
    assert create.status_code == 200
    client.post('/api/auth/logout')
    login = client.post('/api/auth/login', json={'username': 'viewer', 'password': 'ViewerPass123!'})
    assert login.status_code == 200
    response = client.post('/api/check/asn', json={'asn': 'AS3320'})
    assert response.status_code == 403


def test_asn_check_allowed_for_operator() -> None:
    client = _client()
    _setup_and_login(client)
    create = client.post('/api/users', json={'username': 'operator1', 'email': 'op@example.org', 'password': 'OperatorPass123!', 'role': 'operator'})
    assert create.status_code == 200
    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'operator1', 'password': 'OperatorPass123!'}).status_code == 200
    response = client.post('/api/check/asn', json={'asn': 'AS3320'})
    assert response.status_code == 200


def test_system_status_warns_when_migration_behind(monkeypatch) -> None:
    from app.core import system_status as ss

    monkeypatch.setattr(ss, "get_database_status", lambda _engine: {"status": "ok", "migration_status": "behind", "schema_version": "0001", "migration_head": "0002"})
    payload = ss.build_system_status(None)
    assert payload.get("database", {}).get("migration_status") == "behind"
    assert payload.get("operational_warnings")


def test_check_store_operational_error_message() -> None:
    from sqlalchemy.exc import OperationalError
    from app.api import routes_checks as rc

    class FakeDB:
        def add(self, _):
            return None
        def commit(self):
            raise OperationalError("insert", {}, Exception("no column named created_by_user_id"))
        def refresh(self, _):
            return None
        def rollback(self):
            return None

    try:
        rc._store_and_respond(FakeDB(), "asn", "AS3320", None, {"status": "OK", "summary": "ok", "recommendations": [], "details": {}}, 1)
        assert False
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 503
        assert "Database schema is not up to date" in str(getattr(exc, "detail", ""))

def test_users_endpoint_admin_only_and_no_password_hash() -> None:
    client = _client()
    _setup_and_login(client)
    created = client.post('/api/users', json={'username': 'u1', 'email': 'u1@example.org', 'password': 'UserPass123!', 'role': 'viewer'})
    assert created.status_code == 200
    assert 'password_hash' not in created.json()
    resp = client.get('/api/users')
    assert resp.status_code == 200
    for row in resp.json():
        assert 'password_hash' not in row
        assert 'updated_at' in row
        assert 'last_login_at' in row


def test_users_endpoint_forbidden_for_operator_and_viewer() -> None:
    client = _client()
    _setup_and_login(client)
    assert client.post('/api/users', json={'username': 'op2', 'email': 'op2@example.org', 'password': 'OperatorPass123!', 'role': 'operator'}).status_code == 200
    assert client.post('/api/users', json={'username': 'vw2', 'email': 'vw2@example.org', 'password': 'ViewerPass123!', 'role': 'viewer'}).status_code == 200

    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'op2', 'password': 'OperatorPass123!'}).status_code == 200
    assert client.get('/api/users').status_code == 403

    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'vw2', 'password': 'ViewerPass123!'}).status_code == 200
    assert client.get('/api/users').status_code == 403


def test_inactive_user_cannot_login() -> None:
    client = _client()
    _setup_and_login(client)
    create = client.post('/api/users', json={'username': 'inactive1', 'email': 'inactive@example.org', 'password': 'InactivePass123!', 'role': 'viewer'})
    assert create.status_code == 200
    uid = create.json()['id']
    patch = client.patch(f'/api/users/{uid}', json={'is_active': False})
    assert patch.status_code == 200

    client.post('/api/auth/logout')
    login = client.post('/api/auth/login', json={'username': 'inactive1', 'password': 'InactivePass123!'})
    assert login.status_code == 401

def test_audit_log_admin_only_and_contains_login_success() -> None:
    client = _client()
    _setup_and_login(client)
    resp = client.get('/api/audit-log')
    assert resp.status_code == 200
    actions = [i.get('action') for i in resp.json().get('items', [])]
    assert 'login_success' in actions or 'initial_admin_setup' in actions


def test_audit_log_forbidden_for_operator_and_viewer() -> None:
    client = _client()
    _setup_and_login(client)
    assert client.post('/api/users', json={'username': 'op3', 'email': 'op3@example.org', 'password': 'OperatorPass123!', 'role': 'operator'}).status_code == 200
    assert client.post('/api/users', json={'username': 'vw3', 'email': 'vw3@example.org', 'password': 'ViewerPass123!', 'role': 'viewer'}).status_code == 200
    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'op3', 'password': 'OperatorPass123!'}).status_code == 200
    assert client.get('/api/audit-log').status_code == 403
    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'vw3', 'password': 'ViewerPass123!'}).status_code == 200
    assert client.get('/api/audit-log').status_code == 403


def test_login_failed_audit_has_no_password() -> None:
    client = _client()
    _setup_and_login(client)
    bad = client.post('/api/auth/login', json={'username': 'admin', 'password': 'wrong'})
    assert bad.status_code == 401
    resp = client.get('/api/audit-log')
    events = [i for i in resp.json().get('items', []) if i.get('action') == 'login_failed']
    assert events
    assert 'password' not in str(events[0].get('details_json', {})).lower()


def test_cookie_name_and_logout_cookie_settings() -> None:
    secure_client = _client(SESSION_COOKIE_NAME='rf_cookie_test', COOKIE_SECURE=True)
    setup = secure_client.post('/api/auth/setup', json={'username': 'admin', 'email': 'admin@example.org', 'password': 'AdminPass123!', 'password_confirm': 'AdminPass123!'})
    assert setup.status_code == 200
    cookie_header = setup.headers.get('set-cookie', '')
    assert 'rf_cookie_test=' in cookie_header
    assert 'Secure' in cookie_header

    client = _client(SESSION_COOKIE_NAME='rf_cookie_test', COOKIE_SECURE=False)
    setup2 = client.post('/api/auth/setup', json={'username': 'admin', 'email': 'admin@example.org', 'password': 'AdminPass123!', 'password_confirm': 'AdminPass123!'})
    assert setup2.status_code == 200
    out = client.post('/api/auth/logout')
    assert out.status_code == 200
    logout_cookie = out.headers.get('set-cookie', '')
    assert 'rf_cookie_test=' in logout_cookie

def test_change_case_crud_and_roles() -> None:
    client = _client()
    _setup_and_login(client)
    create = client.post('/api/change-cases', json={'title': 'Case 1', 'description': 'desc'})
    assert create.status_code == 200
    cid = create.json()['id']
    assert client.get('/api/change-cases').status_code == 200
    patch = client.patch(f'/api/change-cases/{cid}', json={'status': 'in_review'})
    assert patch.status_code == 200

    client.post('/api/users', json={'username': 'viewer2', 'email': 'viewer2@example.org', 'password': 'ViewerPass123!', 'role': 'viewer'})
    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'viewer2', 'password': 'ViewerPass123!'}).status_code == 200
    assert client.get('/api/change-cases').status_code == 200
    assert client.post('/api/change-cases', json={'title': 'Nope'}).status_code == 403


def test_change_case_invalid_status_and_check_attach_and_audit() -> None:
    client = _client()
    _setup_and_login(client)
    cid = client.post('/api/change-cases', json={'title': 'Case 2', 'description': ''}).json()['id']
    bad = client.patch(f'/api/change-cases/{cid}', json={'status': 'invalid'})
    assert bad.status_code == 400
    check = client.post('/api/check/asn', json={'asn': 'AS3320', 'change_case_id': cid})
    assert check.status_code == 200
    reports = client.get(f'/api/change-cases/{cid}/reports')
    assert reports.status_code == 200
    assert isinstance(reports.json(), list)
    audit = client.get('/api/audit-log')
    actions = [i.get('action') for i in audit.json().get('items', [])]
    assert 'check_attached_to_change_case' in actions
    assert 'report_attached_to_change_case' in actions

def test_change_case_delete_admin_detaches_checks_and_audit() -> None:
    client = _client()
    _setup_and_login(client)
    cid = client.post('/api/change-cases', json={'title': 'Delete Me', 'description': 'desc'}).json()['id']
    check = client.post('/api/check/asn', json={'asn': 'AS3320', 'change_case_id': cid})
    assert check.status_code == 200

    before_reports = client.get('/api/reports')
    assert before_reports.status_code == 200
    report_count_before = len(before_reports.json())

    deleted = client.delete(f'/api/change-cases/{cid}')
    assert deleted.status_code == 200
    assert deleted.json().get('ok') is True
    assert deleted.json().get('detached_checks') == 1

    assert client.get(f'/api/change-cases/{cid}').status_code == 404

    after_reports = client.get('/api/reports')
    assert after_reports.status_code == 200
    assert len(after_reports.json()) == report_count_before

    reports_for_case = client.get(f'/api/change-cases/{cid}/reports')
    assert reports_for_case.status_code == 404

    audit = client.get('/api/audit-log')
    events = [i for i in audit.json().get('items', []) if i.get('action') == 'change_case_deleted']
    assert events
    details = events[0].get('details_json', {})
    assert details.get('title') == 'Delete Me'
    assert details.get('status') == 'draft'
    assert details.get('detached_checks') == 1


def test_change_case_delete_operator_allowed_viewer_forbidden() -> None:
    client = _client()
    _setup_and_login(client)
    client.post('/api/users', json={'username': 'op3', 'email': 'op3@example.org', 'password': 'OperatorPass123!', 'role': 'operator'})
    client.post('/api/users', json={'username': 'vw4', 'email': 'vw4@example.org', 'password': 'ViewerPass123!', 'role': 'viewer'})
    cid = client.post('/api/change-cases', json={'title': 'Role Delete', 'description': ''}).json()['id']

    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'op3', 'password': 'OperatorPass123!'}).status_code == 200
    assert client.delete(f'/api/change-cases/{cid}').status_code == 200

    cid2 = client.post('/api/change-cases', json={'title': 'Role Delete 2', 'description': ''})
    assert cid2.status_code == 200
    cid2v = cid2.json()['id']

    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'vw4', 'password': 'ViewerPass123!'}).status_code == 200
    assert client.delete(f'/api/change-cases/{cid2v}').status_code == 403

def test_bgp_visibility_roles_status_change_case_and_audit(monkeypatch) -> None:
    client = _client()
    _setup_and_login(client)

    from app.services import bgp_visibility_service as svc

    def fake_ok(self, prefix: str, expected_origin_as: str | None):
        return {
            'status': 'OK', 'summary': 'ok', 'explanation': 'x', 'risk': 'r', 'recommendations': ['a'],
            'input': {'prefix': prefix, 'expected_origin_as': expected_origin_as}, 'checks': None,
            'details': {'prefix': prefix, 'visible': True, 'origins': ['AS3320'], 'expected_origin_as': expected_origin_as, 'expected_origin_seen': True, 'multiple_origins': False, 'peer_count': 10, 'more_specifics': [], 'less_specifics': [], 'source_diagnostics': []}
        }

    monkeypatch.setattr(svc.BgpVisibilityService, 'check', fake_ok)

    cid = client.post('/api/change-cases', json={'title': 'BGP Case', 'description': ''}).json()['id']
    ok = client.post('/api/check/bgp-visibility', json={'prefix': '192.0.2.0/24', 'expected_origin_as': 'AS3320', 'change_case_id': cid})
    assert ok.status_code == 200
    assert ok.json().get('status') == 'OK'

    missing = client.post('/api/check/bgp-visibility', json={'prefix': '192.0.2.0/24', 'change_case_id': 999999})
    assert missing.status_code == 404

    client.post('/api/users', json={'username': 'opbgp', 'email': 'opbgp@example.org', 'password': 'OperatorPass123!', 'role': 'operator'})
    client.post('/api/users', json={'username': 'vwbgp', 'email': 'vwbgp@example.org', 'password': 'ViewerPass123!', 'role': 'viewer'})

    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'opbgp', 'password': 'OperatorPass123!'}).status_code == 200
    assert client.post('/api/check/bgp-visibility', json={'prefix': '192.0.2.0/24'}).status_code == 200

    client.post('/api/auth/logout')
    assert client.post('/api/auth/login', json={'username': 'vwbgp', 'password': 'ViewerPass123!'}).status_code == 200
    assert client.post('/api/check/bgp-visibility', json={'prefix': '192.0.2.0/24'}).status_code == 403


def test_bgp_visibility_status_mapping():
    from app.services.bgp_visibility_service import BgpVisibilityService

    class C:
        def __init__(self, responses): self.responses = responses
        def get_with_diagnostics(self, endpoint, _): return self.responses.get(endpoint, ({}, {}))

    svc = BgpVisibilityService(C({'routing-status': ({'data': {'routes': [{'origin': 'AS64496'}]}}, {}), 'bgp-state': ({'data': {}}, {})}))
    assert svc.check('198.51.100.0/24', 'AS3320')['status'] == 'CRITICAL'
    svc2 = BgpVisibilityService(C({'routing-status': ({'data': {'routes': [{'origin': 'AS3320'}, {'origin': 'AS64496'}]}}, {}), 'bgp-state': ({'data': {}}, {})}))
    assert svc2.check('198.51.100.0/24', None)['status'] == 'WARNING'
