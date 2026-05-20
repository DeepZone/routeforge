<p align="center">
  <img src="frontend/public/routeforge.png" alt="RouteForge Logo" width="420">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/version-v0.6.4--beta-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-AGPL--3.0--or--later-orange" alt="License">
  <img src="https://img.shields.io/badge/status-beta-yellow" alt="Status">
  <img src="https://img.shields.io/badge/selfhosted-ready-success" alt="Selfhosted">
  <img src="https://img.shields.io/badge/read--only-routing%20safe-informational" alt="Read-only">
</p>

<p align="center">
  Read-only routing preflight and explainability for BGP, RPKI, Registry/IRR and Routing Visibility.
</p>

___

<!-- Screenshot gallery placeholder:
- docs/screenshots/dashboard.png
- docs/screenshots/asn-check.png
- docs/screenshots/asn-batch-available.png
- docs/screenshots/asn-batch-unavailable.png
- docs/screenshots/prefix-check-overall.png
- docs/screenshots/preflight-check.png
- docs/screenshots/reports-view.png
- docs/screenshots/export-actions.png
- docs/screenshots/demo-mode-banner.png
See docs/screenshots/README.md for capture guidance.
-->

## What RouteForge does

RouteForge helps operators answer three practical questions before a routing change:
- Is it authorized? (RPKI)
- Is it documented? (Registry/IRR)
- Is it visible? (Routing Visibility)

It combines these checks into an explainable, read-only preflight workflow.

## Why it exists

Routing changes often require fast but traceable checks across multiple external data views. RouteForge provides a single UI/API workflow so teams can run consistent preflight checks, share results, and keep a documented decision trail.

## Current Alpha Status

RouteForge is a **functional beta** release with production-like workflows for read-only validation and demo usage. Current release target: **v0.6.4-beta**.

## Quickstart with Docker Compose

```bash
git clone https://github.com/DeepZone/routeforge.git
cd routeforge
cp .env.example .env
docker compose up --build
```

URLs:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Health: http://localhost:8000/health
- System Info (via frontend proxy): http://localhost:3000/api/system/info
- Direct System Info (backend): http://localhost:8000/api/system/info


## System Status

RouteForge exposes runtime operational checks via `GET /api/system/status` and a **System** page in the GUI.

Visible information includes:
- Version
- Mode (live/demo)
- Read-only safety state
- Database status
- RIPEstat runtime settings
- Enabled core features

```bash
curl http://localhost:3000/api/system/status
```

or directly against backend:

```bash
curl http://localhost:8000/api/system/status
```

## Demo Mode

Set `ROUTEFORGE_DEMO_MODE=true` to use fixed demo data.

Use cases:
- Presentations
- Repeatable tests
- Offline demos

Do **not** use demo mode for real routing decisions.

```bash
ROUTEFORGE_DEMO_MODE=true docker compose up --build
```

Or set in `.env`:

```env
ROUTEFORGE_DEMO_MODE=true
```

## Core Checks

- ASN Check
- Prefix Check
- RPKI Check
- Registry/IRR Plausibility Check
- Routing Visibility Check
- Change Preflight Mode

## Result Model

Check severities:
- `OK`
- `WARNING`
- `CRITICAL`
- `UNKNOWN`

Preflight decision model:
- `GO`
- `CAUTION`
- `NO-GO`
- `UNKNOWN`

## Cache and Freshness


## Retry and Resilience

RouteForge retries temporary RIPEstat failures with configurable timeout/retry settings and exposes attempt/retry diagnostics in Data Source Diagnostics.

When stale-cache fallback is enabled, RouteForge can use stale cached data if the live request fails, and explicitly marks this in diagnostics and reports.

Configuration:
- `RIPESTAT_TIMEOUT_SECONDS`
- `RIPESTAT_MAX_RETRIES`
- `RIPESTAT_RETRY_BACKOFF_SECONDS`
- `RIPESTAT_USE_STALE_CACHE_ON_ERROR`


RouteForge shows per-source diagnostics indicating whether data was fetched live or served from cache. Cache Age, TTL and Freshness help operators assess how current a result is.

Freshness values:
- `LIVE`: queried live
- `FRESH`: cached and fresh
- `EXPIRING_SOON`: cache close to expiry
- `STALE`: older than TTL
- `UNKNOWN`: cache age cannot be determined

## Export and Sharing

RouteForge reports can be exported/shared as:
- Summary (plain text)
- Markdown
- HTML

## Report History

RouteForge keeps report history so teams can revisit previous checks and share consistent outputs in change workflows.

## Read-only Security Model

RouteForge is read-only by design:
- no RIPE DB writes
- no ROA creation
- no router deployment

## Known Limitations

- Alpha software, interfaces may evolve.
- RIPEstat payloads can vary over time.
- No local RPKI validator yet.
- No full BGP monitoring replacement.
- No user management yet.


## Selfhosting

### Dev/Demo Start
```bash
cp .env.example .env
docker compose up --build
```

### Production Start
```bash
cp .env.example .env
# edit .env (especially POSTGRES_PASSWORD, DATABASE_URL, CORS_ORIGINS)
docker compose -f docker-compose.prod.yml up -d postgres
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
docker compose -f docker-compose.prod.yml up -d --build
```

### Selfhosting Networking Default
- Frontend UI: `http://<host>:3000`
- API via same host (proxied by frontend nginx): `http://<host>:3000/api/...`
- Direct backend access (optional/diagnostics): `http://<host>:8000`

In the standard setup, RouteForge does **not** require a hardcoded host IP in the frontend build. The frontend nginx proxies `/api` internally to the backend service (`backend:8000`).

### Environment
- `.env.example` documents required production variables.
- Keep RouteForge read-only (no write operations to RIPE DB, RPKI, or routers).

### Database
- Recommended production path: PostgreSQL via `docker-compose.prod.yml`.
- Production/PostgreSQL lifecycle is managed with Alembic migrations.
- SQLite/dev mode keeps lightweight startup initialization (`create_all`) for local/demo compatibility.
- Run migrations manually before production upgrades (`alembic upgrade head`).

### SQLite permission note
- For SQLite selfhosting setups, the backend entrypoint ensures `/app/data` is writable by the non-root runtime user `routeforge` at container startup.

### Operations docs
- Backup/Restore: `docs/operations/backup-restore.md`
- Reverse Proxy: `docs/operations/reverse-proxy.md`
- Troubleshooting: `docs/operations/troubleshooting.md`
- Logging: `docs/operations/logging.md`
- Upgrades: `docs/operations/upgrades.md`

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## Development

Local setup and contribution process are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## Tests

Backend:

```bash
cd backend
pytest -q
```

Frontend:

```bash
cd frontend
npm run build
```

## License

RouteForge is licensed under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later).


## Security baseline

For production polish and selfhosting hardening guidance, see:

- `docs/operations/security.md`
- `docs/operations/release-checklist.md`

In the standard Docker setup, API calls are same-origin via frontend nginx (`/api` proxy). CORS is primarily needed for split frontend/backend deployments.
