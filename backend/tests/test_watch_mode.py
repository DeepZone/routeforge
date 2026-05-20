import importlib
from fastapi.testclient import TestClient
import app.config as config


def _client() -> TestClient:
    config.settings = config.Settings(_env_file=None, ROUTEFORGE_DEMO_MODE=True)
    import app.main as main_module
    import app.database as database
    importlib.reload(main_module)
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    return TestClient(main_module.app)

def _setup(client, u='admin', p='AdminPass123!'):
    r=client.post('/api/auth/setup', json={'username':u,'email':'a@b.c','password':p,'password_confirm':p})
    if r.status_code==403:
      assert client.post('/api/auth/login', json={'username':u,'password':p}).status_code==200

def test_watch_create_and_run_and_run_due():
    c=_client(); _setup(c)
    resp=c.post('/api/watch-targets', json={'name':'t1','watch_type':'prefix','prefix':'192.0.2.0/24','interval_minutes':60,'is_active':True})
    assert resp.status_code==200
    tid=resp.json()['id']
    assert c.get('/api/watch-targets').status_code==200
    run=c.post(f'/api/watch-targets/{tid}/run'); assert run.status_code==200
    assert run.json()['changed'] is False
    due=c.post('/api/watch-targets/run-due'); assert due.status_code==200

def test_viewer_readonly_watch():
    c=_client(); _setup(c)
    assert c.post('/api/users', json={'username':'viewer','email':'v@e.c','password':'ViewerPass123!','role':'viewer'}).status_code==200
    c.post('/api/auth/logout'); assert c.post('/api/auth/login', json={'username':'viewer','password':'ViewerPass123!'}).status_code==200
    assert c.get('/api/watch-targets').status_code==200
    assert c.post('/api/watch-targets', json={'name':'x','watch_type':'asn','asn':'AS3320'}).status_code==403


def test_end_to_end_change_case_workflow_with_audit_and_reports():
    c=_client(); _setup(c)
    cc=c.post('/api/change-cases', json={'title':'E2E Case','description':'workflow'}); assert cc.status_code==200
    cc_id=cc.json()['id']

    bgp=c.post('/api/check/bgp-visibility', json={'prefix':'192.0.2.0/24','expected_origin_as':'AS3320','change_case_id':cc_id}); assert bgp.status_code==200
    roa=c.post('/api/check/roa-preflight', json={'prefix':'192.0.2.0/24','origin_as':'AS3320','max_length':24,'change_case_id':cc_id}); assert roa.status_code==200

    wt=c.post('/api/watch-targets', json={'name':'e2e-watch','watch_type':'prefix','prefix':'192.0.2.0/24','interval_minutes':60,'is_active':True,'change_case_id':cc_id}); assert wt.status_code==200
    tid=wt.json()['id']
    run=c.post(f'/api/watch-targets/{tid}/run'); assert run.status_code==200

    runs=c.get(f'/api/watch-targets/{tid}/runs'); assert runs.status_code==200
    assert len(runs.json()) >= 1
    assert runs.json()[0].get('id')

    reports=c.get(f'/api/change-cases/{cc_id}/reports'); assert reports.status_code==200
    report_rows=reports.json()
    assert len(report_rows) >= 2
    assert any(r.get('check_type') == 'bgp-visibility' for r in report_rows)
    assert any(r.get('check_type') == 'roa-preflight' for r in report_rows)

    audit=c.get('/api/audit-log?limit=500'); assert audit.status_code==200
    actions={item.get('action') for item in audit.json().get('items', [])}
    for expected in ['change_case_created','bgp_visibility_checked','roa_preflight_checked','watch_target_created','watch_target_run','report_generated','report_attached_to_change_case']:
        assert expected in actions
