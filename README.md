# BGP, RPKI and ROA Preflight Validation Tool

<p align="center">
  <img src="frontend/public/routeforge.png" alt="RouteForge Logo" width="420">
</p>
<p align="center">
  <img src="https://img.shields.io/badge/version-v1.0.2-blue" alt="Version">
  <img src="https://img.shields.io/badge/license-AGPL--3.0--or--later-orange" alt="License">
  <img src="https://img.shields.io/badge/status-stable-brightgreen" alt="Status">
  <img src="https://img.shields.io/badge/selfhosted-ready-success" alt="Selfhosted">
  <img src="https://img.shields.io/badge/read--only-routing%20safe-informational" alt="Read-only">
</p>

<p align="center">
  Self-hosted read-only preflight validation for BGP, RPKI, ROA, RIPEstat, Registry/IRR and routing visibility workflows.
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

## BGP, RPKI and ROA Preflight Validation Tool

## What this tool does

This self-hosted, read-only platform helps network operators run preflight checks before planned routing changes. It combines BGP visibility, RPKI validation, ROA preflight, Registry/IRR context and RIPEstat data into one explainable workflow.

It is designed for ROA planning and operational safety checks, including ASN checks, prefix-origin validation, routing visibility review, and early detection of signals that may indicate a route leak, origin mismatch, or invalid announcement.

## Why BGP and RPKI preflight validation matters

Before announcing or changing origins, teams need fast evidence from multiple routing data sources. A structured preflight process helps reduce the risk of unintended exposure, catches inconsistencies early, and improves communication across operations and change management.

Using read-only checks before execution helps teams validate assumptions without modifying routers, creating ROAs, or writing to external registries.

## Key Features

- Self-hosted and read-only by design
- Unified BGP visibility and routing visibility checks
- RPKI validation and ROA preflight support for safer ROA planning
- Registry/IRR and RIPEstat enrichment in one workflow
- ASN checks and prefix-origin validation with explainable outcomes
- Change preflight summaries for review and documentation

## Typical Use Cases

- Validate planned origin changes before maintenance windows
- Investigate suspected origin mismatch or invalid announcement scenarios
- Improve route leak awareness during peer and transit change reviews
- Standardize routing security preflight workflows across teams
- Share repeatable evidence for audits and post-change analysis

## Current Release

RouteForge is a **stable** self-hosted release for production-grade read-only validation workflows. Current release: **v1.0.2**.

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

- Stable release with ongoing minor UX/documentation improvements.
- RIPEstat payloads can vary over time.
- No local RPKI validator yet.
- No full BGP monitoring replacement.
- No OAuth/SSO yet.
- No LDAP yet.
- No email password reset flow yet.


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

For frontend Vite development proxying:
- Docker Compose default: `VITE_API_PROXY_TARGET=http://backend:8000`
- Local development outside Docker: `VITE_API_PROXY_TARGET=http://localhost:8000`
- Do not commit local/private IP targets (for example `192.168.x.x`, `10.x.x.x`, `172.16-31.x.x`) to the repository.

### Environment
- `.env.example` documents required production variables.
- Keep RouteForge read-only (no write operations to RIPE DB, RPKI, or routers).

### Database
- Recommended production path: PostgreSQL via `docker-compose.prod.yml`.
- Production/PostgreSQL lifecycle is managed with Alembic migrations.
- SQLite/dev mode can keep lightweight startup initialization (`create_all`) only when `ALLOW_SQLITE_CREATE_ALL=true` (default for local/demo). Disable it in production-like environments.
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


## User Management

- Initial admin setup is required on first start.
- Login/Logout are session-cookie based.
- Roles: `admin`, `operator`, `viewer`.
- User management is **admin-only**.
- Viewers cannot execute checks.
- Keep `SECRET_KEY` stable; changing it invalidates existing sessions.


## BGP Visibility Details
- Read-only BGP visibility validation for prefix and optional expected origin AS.
- Uses external RIPEstat visibility data; results are momentary snapshots and do not replace continuous monitoring.


## Operational docs for provider/workflow extensions
- docs/operations/rpki-provider.md
- docs/operations/bgp-visibility-providers.md
- docs/operations/change-case-workflow.md
- docs/operations/watch-alerts.md
- docs/architecture/providers.md
