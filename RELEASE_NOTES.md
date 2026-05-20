# Release Notes

## v0.5.2-beta

**System Status & Operational Checks**

### Highlights

- New `/api/system/status` endpoint
- GUI System Status view
- Database health visibility
- RIPEstat runtime settings visibility
- Read-only safety state shown
- API proxy status visible from frontend
- Improved selfhosting observability

### Known limitations

- No authentication yet
- No multi-user support yet
- No advanced alerting
- No scheduled health checks yet

---

## v0.5.0-beta

**Production Selfhosting Foundation**

### Highlights

- Production Docker Compose
- PostgreSQL-backed deployment path
- Healthchecks
- Backup/Restore documentation
- Reverse proxy documentation
- Logging and upgrade documentation
- Continued read-only safety model

### Known limitations

- Database migrations are currently simple/alpha-grade and will be hardened before v1.0.
- No authentication yet
- No multi-user support yet
- No write operations

---

## v0.4.2-alpha

### Highlights

- Retry & Resilience
- Retry diagnostics
- Attempts/retry count visible
- Rate-limit handling
- Optional stale cache fallback
- UI/report warning when fallback data is used

---

## v0.4.1-alpha

### Highlights

- Cache & Freshness Transparency
- Cache age and TTL shown in diagnostics
- Freshness classification LIVE/FRESH/EXPIRING_SOON/STALE/UNKNOWN
- Force Refresh support prepared internally

---

## v0.4.0-alpha

**Product Demo & Release Readiness**

### Highlights

- Improved README for public alpha usage
- Demo flow documentation
- Screenshot plan
- Clear Quickstart
- v0.2.x features summarized:
  - Change Preflight Mode
  - Routing Visibility Check
  - Holder display
  - Export/Sharing
  - ASN-RPKI batch availability explanations

### Known Limitations

- Alpha software
- RIPEstat payloads can vary
- No write operations
- No usermanagement yet
- No local RPKI validator yet
- No full BGP monitoring

---

## v0.2.0-alpha (history)

RouteForge v0.2.0-alpha introduced the functional alpha baseline for read-only routing preflight checks.

Key capabilities in v0.2.x:
- Change Preflight Mode
- Routing Visibility Check
- Holder detection/display
- Export & sharing (Summary, Markdown, HTML)
- ASN-RPKI batch availability explanations
- Demo mode and CI-backed test workflows
