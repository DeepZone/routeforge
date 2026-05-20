# Upgrades

1. Read release notes before upgrade.
2. Create backup before migration and container changes.
3. Pull/update code and rebuild images.

```bash
git pull
docker compose -f docker-compose.prod.yml build
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

## Notes on existing alpha databases
- If tables were created via `create_all` before Alembic baseline, apply baseline carefully:

```bash
docker compose -f docker-compose.prod.yml run --rm backend alembic stamp 0001_initial_schema
```

- Then run normal upgrades (`alembic upgrade head`).
