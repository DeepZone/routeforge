# Release Checklist

## Before release

- `git pull`
- Run backend tests (`cd backend && pytest -q`)
- Run frontend production build (`cd frontend && npm run build`)
- Validate Compose (`docker compose config` and production config)
- Check system status endpoint (`/api/system/status`)
- Check migration status visibility (`database.schema_version`, `migration_head`, `migration_status`)

## Tagging

- `git tag -a vX.Y.Z[-beta] -m "RouteForge vX.Y.Z[-beta]"`
- `git push origin vX.Y.Z[-beta]`

## GitHub Release

- Use release title matching the version and sprint scope
- Enable **prerelease** checkbox for beta versions
- Include structured release notes with highlights and known limitations

## Post-release smoke test

- `GET /health`
- `GET /api/system/info`
- `GET /api/system/status`
- Basic ASN check
- Basic Prefix check
- Export summary from report history
