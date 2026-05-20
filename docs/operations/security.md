# Security Baseline

## Read-only safety model

RouteForge is read-only by design. It validates routing state and preflight conditions but does not push configuration changes to external systems.

## Reverse proxy / HTTPS recommendation

Use RouteForge behind a reverse proxy with TLS termination in production (for example Caddy, Traefik, or Nginx). Keep plain HTTP only for local lab usage.

## Secrets and .env handling

- Copy `.env.example` to `.env` and set real values before production use.
- Never commit `.env` files to git.
- Change `POSTGRES_PASSWORD` from the example default.

## Default password warning

`/api/system/status` exposes `security_warnings` when a risky default is detected (currently: `POSTGRES_PASSWORD=change-me`). No secret values are returned.

## CORS guidance

In the standard Docker setup, frontend and API are same-origin via nginx (`/api` proxy). CORS is mainly relevant for split deployments where frontend and backend are served from different origins.

## Security headers

Frontend nginx sets baseline headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer-when-downgrade`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- A conservative initial Content-Security-Policy for SPA usage

## Container hardening

- Backend container starts through an entrypoint as root only long enough to normalize `/app/data` ownership, then drops privileges to non-root user `routeforge` for runtime.

- Backend container runs as non-root user `routeforge`.
- Backend image keeps only runtime-relevant files.
- Frontend image is multi-stage (build + runtime).
- Nginx container still runs with default upstream behavior; strict non-root nginx runtime can be added later as a dedicated hardening step.

## SQLite volume permissions (Docker Compose)

In the standard `docker-compose.yml` setup with SQLite, the database file is stored at `/app/data/routeforge.db` via the named volume mount `routeforge_data:/app/data`.

The backend entrypoint ensures `/app/data` is writable for the non-root runtime user `routeforge` on container start. This prevents SQLite write failures such as `sqlite3.OperationalError: attempt to write a readonly database` when a mounted volume is root-owned.

## What RouteForge does not do

- no ROA creation
- no RIPE DB writes
- no router deployment

## Current limitations

- Role model: admin/operator/viewer
- Admin-only user management
- Inactive users cannot log in
- Password reset is admin-driven (set new password in user management)
- No external auth/SSO in this version
