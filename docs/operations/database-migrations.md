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
