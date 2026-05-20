## v0.7.2-beta: BGP Visibility Details

### Motivation
Improve prefix visibility checks with explicit BGP origin visibility details while preserving RouteForge's strict read-only model.

### Implemented Changes
- Added dedicated backend service and API endpoint `POST /api/check/bgp-visibility`.
- Added frontend BGP Visibility page and Change Case integration action.
- Added audit event `bgp_visibility_checked` plus existing case attachment events when linked to a Change Case.
- Extended report output to include structured BGP visibility details via generic detail rendering.

### BGP Visibility Logic
- `OK`: prefix visible and expected origin (if provided) is seen.
- `WARNING`: prefix visible with multiple or unexpected origins (without strict expectation).
- `CRITICAL`: prefix not visible with expected origin requirement, or expected origin not visible.
- `UNKNOWN`: no reliable source data.

### Security Notes
BGP visibility checks remain read-only and do not modify RIPE DB, RPKI objects, or routers. Results are external visibility snapshots.

### Testing
- backend: `pytest -q`
- frontend: `npm run build`

### Known Limitations
- Visibility depends on external RIPEstat data quality and timing.
- Results are point-in-time and not a substitute for continuous monitoring.

## v0.7.0-beta
- Added Projects / Change Cases lifecycle (draft, in_review, approved, closed).
- Added Change Case API, UI navigation and detail workflow.
- Checks and reports can be attached to Change Cases for local RouteForge workflow traceability.
- Added audit events for Change Case and attachment operations.
- Security: Change Cases are local workflow metadata only; no writes to RIPE DB, RPKI, or routers are performed.

# Release Notes

## v0.7.0-beta

**Audit Log UI & Session Hardening**

### Highlights

- Added centralized backend audit logging service and audit events for setup/auth/user/check/report actions.
- Added admin-only `GET /api/audit-log` API with basic filters and newest-first sorting.
- Added admin-only Audit Log UI with table, loading/error/empty states and filters.
- Session cookie handling now consistently uses `SESSION_COOKIE_NAME` and `COOKIE_SECURE` settings for set/delete.
- Added backend tests for audit permissions/events and session cookie hardening behavior.

### Security notes

- Audit events exclude passwords, password hashes, session tokens and secrets.
- `login_failed` entries store only username/reason and request metadata.
- RouteForge remains read-only against RIPE DB, RPKI and routers; no write paths were introduced.
- Audit logging is local to RouteForge storage only.

---

## v0.6.5-beta

**Auth UX & Admin Console Polish**

### Highlights

- Logged-in user and role are clearly visible in the UI.
- Added visible logout flow.
- Added admin-only user management UI.
- Added role-aware navigation for admin/operator/viewer.
- Improved permission and session-expired messages.
- Dashboard now explains current user capabilities.
- User management API responses avoid password hash exposure.
- Audit Log UI/API may be included if implemented.

### Known limitations

- No OAuth/SSO yet.
- No LDAP yet.
- No email password reset flow yet.
- Audit log UI may still be limited if not implemented in this sprint.

---

## v0.6.4-beta

**Alembic Logging Config Hotfix**

### Highlights

- Fixed Alembic CLI crash with `KeyError: "formatters"`.
- Alembic `env.py` now handles minimal `alembic.ini` files safely.
- Database migration commands now work in Docker selfhosting setups.
- Migration troubleshooting documentation updated.

---

## v0.6.2-beta

**Frontend Auth Render Hotfix**

### Highlights

- Fixed white screen after initial admin setup/login.
- Fixed React hook ordering issue in `App.tsx`.
- Auth bootstrap flow now renders setup/login/app states without hook crashes.
- No backend routing/check logic changed.

---

## v0.6.1-beta

**Auth Bootstrap Fix**

### Highlights

- Fixed missing Initial Admin Setup screen.
- App now blocks dashboard/check views until setup/login state is resolved.
- Fixed NoneType crash when running checks without authenticated user.
- Check endpoints now return 401/403 instead of HTTP 500.
- API requests include session cookies consistently.

---


## v0.5.4-beta

**Production Polish & Security Baseline**

### Highlights

- Security headers for frontend Nginx
- Improved same-origin proxy security guidance
- Container hardening review
- Safer environment and secrets documentation
- Logging baseline improvements
- Security operations documentation
- Release checklist documentation
- Optional security warnings in system status

### Known limitations

- No authentication yet
- No multi-user support yet
- No advanced RBAC yet
- No automated release pipeline yet

---


## Licensing

RouteForge is now licensed under AGPL-3.0-or-later.

The license choice reflects RouteForge's selfhosted-first and network-service nature and ensures that improvements to publicly hosted modified versions remain available to users.

---

## v0.5.3-beta

**Database Lifecycle & Migrations**

### Highlights

- Alembic migration baseline for backend schema lifecycle
- Initial schema migration `0001_initial_schema`
- Migration status visibility in `/api/system/status`
- Database schema version visibility in GUI System view
- Upgrade process updated with explicit migration steps
- Backup/restore documentation updated for migration-safe operations

### Known limitations

- Existing alpha databases may need manual baseline handling (`alembic stamp 0001_initial_schema`)
- No advanced rollback automation yet
- Authentication is not implemented yet

---

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

## v0.6.4-beta

**Migration UX & Auth Visibility Hotfix**

### Highlights

- Improved visibility for database migration status.
- Added clearer troubleshooting for missing `created_by_user_id` columns after v0.6 upgrade.
- Added logged-in user and role display in the UI.
- Added visible logout action.
- Improved migration warnings in Dashboard/System views.
- Improved handling of stale database schemas.

## v0.7.0-beta hotfix: Change Cases UX polish

- Added `DELETE /api/change-cases/{id}` for operators/admins with check detachment and audit logging (`change_case_deleted`).
- Improved Change Cases frontend UX with in-app create/edit forms, status workflow buttons, check execution inputs, report table, and delete action with confirmation.
- Added frontend API helpers for deleting cases and running prefix/preflight checks with `change_case_id`.
- Added backend tests for change-case deletion authorization, detachment behavior, and audit event emission.
