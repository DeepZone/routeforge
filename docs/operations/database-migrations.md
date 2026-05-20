# Database Migrations

RouteForge uses Alembic for schema lifecycle tracking from `v0.5.3-beta`.

## Commands
```bash
docker compose exec backend alembic current
docker compose exec backend alembic heads
docker compose exec backend alembic upgrade head
```

## Docker QA runbook (v0.9.1-rc)

```bash
docker compose up -d
docker compose logs backend
docker compose exec backend alembic current
docker compose exec backend alembic heads
docker compose exec backend alembic upgrade head
docker compose restart backend
```

Validation goals:
- backend comes up without migration crash
- `alembic current` equals `alembic heads`
- after restart, `/api/system/status` remains `migration_status=up_to_date`

## Reverse proxy notes

Use a reverse proxy for production TLS termination and same-origin `/api` forwarding.
See `docs/operations/reverse-proxy.md` for deployment examples.

## Existing pre-baseline databases
If schema already exists from historical `create_all`, mark baseline first only after schema verification:
```bash
docker compose exec backend alembic stamp 0001_initial_schema
docker compose exec backend alembic upgrade head
```
