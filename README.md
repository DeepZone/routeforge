# RouteForge

RouteForge is a read-only routing preflight and explainability tool for BGP, RPKI, Registry/IRR and Routing Visibility checks.

Current user-facing version: **v0.4.0-alpha**.

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

RouteForge is a **functional alpha** release with production-like workflows for read-only validation and demo usage. Current release target: **v0.4.0-alpha**.

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
- System Info: http://localhost:8000/api/system/info

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

This project is released under the [MIT License](LICENSE).
