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

- Backend container runs as non-root user `routeforge`.
- Backend image keeps only runtime-relevant files.
- Frontend image is multi-stage (build + runtime).
- Nginx container still runs with default upstream behavior; strict non-root nginx runtime can be added later as a dedicated hardening step.

## What RouteForge does not do

- no ROA creation
- no RIPE DB writes
- no router deployment

## Current limitations

- no authentication yet
- no multi-user support yet
