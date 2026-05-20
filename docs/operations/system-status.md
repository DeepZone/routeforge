# System Status

RouteForge provides operational visibility through the **System** page in the UI and the endpoint `GET /api/system/status`.

## Endpoints

- `GET /api/system/status`: detailed runtime/operational status.
- `GET /health`: lightweight liveness status (compatible baseline endpoint).

## What to check

### If `database=status:error`
- Verify `DATABASE_URL` in `.env`.
- Verify database container/service availability.
- Verify network routing between backend and database.
- Verify credentials and database existence.

### If API Proxy shows `ERROR` in UI
- Verify frontend nginx is running.
- Verify `/api` proxy config in frontend nginx.
- Verify backend service is reachable from frontend container.
- Verify browser calls use same-origin `/api/...`.

### Demo Mode
- Check `demo_mode` field in `/api/system/status`.
- Check `ROUTEFORGE_DEMO_MODE` runtime value.

### Version
- Validate expected deployed version in `/api/system/status` and `/health`.
