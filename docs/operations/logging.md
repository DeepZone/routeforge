# Logging

## Docker Compose logs
```bash
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f postgres
```

## Backend logs
- Backend logs are emitted to container stdout/stderr.
- Use `LOG_LEVEL` in `.env` (for example `INFO` or `DEBUG`) to tune verbosity.

## Frontend logs
- Nginx access/error logs are available via frontend container logs.

## Diagnostics in reports
- RIPEstat request diagnostics and fallback behavior are surfaced in reports.
- Use these fields to distinguish source errors vs. app errors.

## Troubleshooting checklist
- Confirm `/health` is `ok`.
- Check Postgres health and credentials (`DATABASE_URL`).
- Validate `CORS_ORIGINS` and `VITE_API_URL` alignment.
- Inspect retry/fallback diagnostics for upstream RIPEstat outages.
- If you see `sqlite3.OperationalError: attempt to write a readonly database` in dev/compose mode, check volume ownership on `/app/data` and rebuild/restart with the fixed backend image that normalizes volume permissions at startup.
