# Troubleshooting

## sqlite3.OperationalError: attempt to write a readonly database

### Cause

In SQLite deployments, the database is commonly stored at `/app/data/routeforge.db`.
If the Docker volume at `/app/data` is owned by root, the non-root runtime user `routeforge` cannot write to the SQLite file. Check persistence then fails with `sqlite3.OperationalError: attempt to write a readonly database`.

### Fix since v0.5.5-beta

Since `v0.5.5-beta`, the backend entrypoint sets ownership for `/app/data` to `routeforge:routeforge` at container startup and then keeps running as non-root user `routeforge`.

### Workaround for older versions

```bash
docker compose down
docker compose run --rm --user root backend sh -c "mkdir -p /app/data && chown -R routeforge:routeforge /app/data && chmod -R u+rwX /app/data"
docker compose up -d --build
```


## KeyError: 'formatters' (Alembic)

### Cause

Older versions used a minimal `backend/alembic.ini` without logging sections while `backend/alembic/env.py` still called `fileConfig(...)`.

### Fix

Upgrade to `v0.6.4-beta` or newer, then:

```bash
docker compose exec backend alembic upgrade head
```


## I do not see check menu items

Check role permissions: `viewer` can only see Dashboard/Reports/About.

## 403 for checks

The user is `viewer` or inactive. Verify role and `is_active` in Admin User Management.

## Login does not work

Check: Is the user active? Is the password correct? Was `SECRET_KEY` changed?

## After SECRET_KEY change

All sessions become invalid. Log in again.


## Migration required in UI/System Status

If `migration_status=behind` is reported, run in order:

```bash
alembic current
alembic heads
alembic upgrade head
```

Use `alembic stamp 0001_initial_schema` only when the schema already exists and exactly matches the baseline state.
