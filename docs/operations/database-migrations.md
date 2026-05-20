# Database Migrations

RouteForge uses Alembic for schema lifecycle tracking from `v0.5.3-beta`.

## Why
- Traceable schema history
- Safe, repeatable upgrades
- Visible migration state in system status

## Engines
- Production: PostgreSQL (recommended)
- Dev/demo: SQLite supported

## Commands
```bash
cd backend
alembic history
alembic current
alembic upgrade head
```

## Existing pre-baseline databases
If the schema already exists from historical `create_all`, mark baseline first:
```bash
alembic stamp 0001_initial_schema
```

## Auto migration
`ROUTEFORGE_AUTO_MIGRATE` is not enabled by default in this beta.
Run migrations manually before production upgrades.

## Troubleshooting: missing `created_by_user_id` after v0.6 upgrade

Fehlerbild:

`sqlite3.OperationalError: table checks has no column named created_by_user_id`

Ursache:

Die Migration `0002_users_and_report_ownership` wurde auf einer bestehenden Datenbank nicht ausgeführt.

Fix:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic heads
docker compose exec backend alembic upgrade head
```

Wenn bestehende Pre-Alembic DB:

```bash
docker compose exec backend alembic stamp 0001_initial_schema
docker compose exec backend alembic upgrade head
```

Vorher Backup:

```bash
docker compose exec backend sh -c 'cp /app/data/routeforge.db /app/data/routeforge.db.bak.$(date +%s)'
```
