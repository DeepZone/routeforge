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
