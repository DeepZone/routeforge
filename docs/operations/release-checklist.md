# Release Checklist

## v0.9.1-rc: Deployment QA & UX Validation

### 1) Pre-release validation

- `git pull`
- Run backend tests (`cd backend && pytest -q`)
- Run frontend production build (`cd frontend && npm run build`)
- Validate Compose (`docker compose config` and production config)

### 2) Deployment smoke check

Run after backend/frontend are up and frontend artifacts were built:

```bash
python backend/scripts/check_deployment_health.py --base-url http://localhost:8000 --check-setup
```

The script validates:
- Backend reachable (`/health`)
- `/api/system/status` reachable
- `version` present
- `read_only=true`
- `database.status`, `schema_version`, `migration_head` present
- `migration_status` is not `behind`
- Frontend build artifacts exist (`frontend/dist/index.html`)
- Optional `/api/setup/required` reachability

### 3) UX QA checklist

- [ ] Setup Flow works and initial admin creation succeeds
- [ ] Login/Logout works end-to-end
- [ ] User Management roles behave correctly (admin/operator/viewer)
- [ ] Audit Log is visible only for admin users
- [ ] Change Case create/edit/delete works for authorized roles
- [ ] BGP Visibility check works and stores report
- [ ] ROA Planner check works and stores report
- [ ] Watch Target create/edit/run-due works for authorized roles
- [ ] Report export works for Markdown/HTML/Summary
- [ ] Viewer can read data but cannot execute checks/watch/change operations
- [ ] Operator can execute checks/watch/change cases, but cannot access user/audit admin-only features

### 4) Tagging

- `git tag -a v0.9.1-rc -m "RouteForge v0.9.1-rc"`
- `git push origin v0.9.1-rc`

### 5) GitHub Release

- Release title aligned with `v0.9.1-rc`
- Mark as prerelease
- Include deployment, upgrade, and security QA notes

### 6) Post-release smoke test

- `GET /health`
- `GET /api/system/info`
- `GET /api/system/status`
- Basic ASN check
- Basic Prefix check
- Export summary from report history
