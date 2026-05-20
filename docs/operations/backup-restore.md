# Backup and Restore

## What to back up
- PostgreSQL data (logical dump and/or Docker volume snapshot).
- `.env` and any reverse proxy configuration.
- Optional exported reports if you archive them outside the DB.

## PostgreSQL backup
```bash
docker compose -f docker-compose.prod.yml exec postgres pg_dump -U routeforge routeforge > routeforge-backup.sql
```

## PostgreSQL restore
```bash
cat routeforge-backup.sql | docker compose -f docker-compose.prod.yml exec -T postgres psql -U routeforge routeforge
```

## Docker volume notes
- The persistent database volume is `routeforge_postgres_data`.
- For crash-consistent volume snapshots, stop writes first (or stop backend temporarily).

## Configuration backup
- Back up `.env` separately from database dumps.
- Keep secrets in a secure secret manager or encrypted backup location.

## Verification after restore
- Start stack and check backend health:
```bash
curl http://localhost:8000/health
```
- Open UI and verify report history is present.
- If using demo/SQLite setups, back up the SQLite file separately.
