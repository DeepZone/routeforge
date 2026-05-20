# Security Baseline

## Security QA checklist (v0.9.1-rc)

- [ ] `SECRET_KEY` changed from any default/dev value
- [ ] `COOKIE_SECURE=true` when running behind HTTPS
- [ ] `COOKIE_SAMESITE` is plausible (`lax` recommended, `none` only with `COOKIE_SECURE=true`)
- [ ] `CORS_ORIGINS` is explicit and not `*`
- [ ] Admin password is strong and unique
- [ ] Demo mode is disabled for production usage
- [ ] Backup exists and restore procedure is tested
- [ ] Alembic is current (`alembic current == alembic heads`)
- [ ] Watch Mode external cron/triggering is access-restricted and authenticated
- [ ] No public write-endpoints exist to RIPE/RPKI/router systems

## Read-only safety model

RouteForge is read-only by design. It validates routing state and preflight conditions but does not push configuration changes to external systems.

## Reverse proxy / HTTPS recommendation

Use RouteForge behind a reverse proxy with TLS termination in production (for example Caddy, Traefik, or Nginx). Keep plain HTTP only for local lab usage.

## Secrets and .env handling

- Copy `.env.example` to `.env` and set real values before production use.
- Never commit `.env` files to git.
- Change `POSTGRES_PASSWORD` from the example default.

## HTTPS cookie and CORS guidance

- `COOKIE_SECURE=true` for HTTPS deployments.
- `COOKIE_SAMESITE=lax` is the recommended default.
- `COOKIE_SAMESITE=none` requires `COOKIE_SECURE=true`.
- In split-origin deployments set explicit `CORS_ORIGINS` to frontend domains.

## Security headers

Frontend nginx sets baseline headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: no-referrer-when-downgrade`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`
- A conservative initial Content-Security-Policy for SPA usage

## What RouteForge does not do

- no ROA creation
- no RIPE DB writes
- no router deployment
