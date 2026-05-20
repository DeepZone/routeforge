# Upgrades

1. Read release notes before upgrade.
2. Create backup before changing containers.
3. Pull/update code and rebuild images.

```bash
git pull
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
curl http://localhost:8000/health
```

## Post-upgrade checks
- Verify backend health endpoint response.
- Open frontend and run a sample check.
- Verify existing reports can still be viewed.

## Notes on database changes
- Current migration handling is still beta-grade.
- Database migrations are currently simple/alpha-grade and will be hardened before v1.0.
