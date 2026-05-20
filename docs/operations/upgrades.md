# Upgrades

1. Read release notes before upgrade.
2. Create backup before migration and container changes.
3. Pull/update code and rebuild images.

```bash
git pull
docker compose -f docker-compose.prod.yml build
```

## Upgrade QA matrix (v0.9.1-rc)

### A) Fresh SQLite DB

```bash
rm -f backend/data/routeforge.db
cd backend && alembic upgrade head
cd .. && docker compose up -d
```

Expected:
- backend starts cleanly
- `/api/system/status` shows `migration_status=up_to_date`

### B) Existing SQLite DB from older revision

```bash
cd backend && alembic current
cd backend && alembic heads
cd backend && alembic upgrade head
cd .. && docker compose restart backend
```

Expected:
- `alembic current` matches `alembic heads`
- application starts without migration warnings

### C) Behavior when DB is behind

Expected behavior:
- `/api/system/status` returns database migration status `behind`
- operational warnings include upgrade command hints
- release/deployment checks must fail until DB is upgraded

### D) `ALLOW_SQLITE_CREATE_ALL=false`

Expected behavior:
- SQLite startup must not silently create schema via `create_all`
- migration discipline remains Alembic-first

### E) Safe `alembic stamp` usage

Use `alembic stamp <revision>` only when:
- schema was inspected and confirmed equivalent to stamped revision
- DB is a pre-Alembic legacy DB initialized outside Alembic

Recommended sequence:

```bash
alembic current
alembic heads
# verify tables/columns align with target baseline revision first
alembic stamp 0001_initial_schema
alembic upgrade head
```

## Database migration workflow (production)

```bash
docker compose -f docker-compose.prod.yml up -d postgres
docker compose -f docker-compose.prod.yml run --rm backend alembic current
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
docker compose -f docker-compose.prod.yml up -d
curl http://localhost:3000/api/system/status
```

## Post-upgrade checks
- Verify backend health endpoint response.
- Verify `/api/system/status` database migration fields:
  - `schema_version`
  - `migration_status`
  - `migration_head`
- Open frontend and run a sample check.
- Verify existing reports can still be viewed.
