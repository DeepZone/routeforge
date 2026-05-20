# Troubleshooting

## sqlite3.OperationalError: attempt to write a readonly database

### Ursache

Bei SQLite-Deployments liegt die Datenbank häufig unter `/app/data/routeforge.db`.
Wenn das Docker-Volume auf `/app/data` root-owned ist, kann der non-root Runtime-User `routeforge` nicht in die SQLite-Datei schreiben. Dadurch schlagen Check-Speicherungen mit `sqlite3.OperationalError: attempt to write a readonly database` fehl.

### Fix ab v0.5.5-beta

Ab `v0.5.5-beta` setzt der Backend-Entrypoint beim Containerstart die Ownership für `/app/data` auf `routeforge:routeforge` und startet danach den Prozess weiterhin als non-root User `routeforge`.

### Workaround für ältere Versionen

```bash
docker compose down
docker compose run --rm --user root backend sh -c "mkdir -p /app/data && chown -R routeforge:routeforge /app/data && chmod -R u+rwX /app/data"
docker compose up -d --build
```


## KeyError: 'formatters' (Alembic)

### Ursache

Ältere Versionen hatten eine minimale `backend/alembic.ini` ohne Logging-Sektionen, während `backend/alembic/env.py` `fileConfig(...)` aufgerufen hat.

### Fix

Update auf `v0.6.4-beta` oder neuer, dann:

```bash
docker compose exec backend alembic upgrade head
```


## Ich sehe keine Check-Menüpunkte

Rolle prüfen: `viewer` sieht nur Dashboard/Reports/About.

## 403 bei Checks

User ist `viewer` oder inaktiv. Rolle und `is_active` im Admin User Management prüfen.

## Login geht nicht

Prüfen: User aktiv? Passwort korrekt? Wurde `SECRET_KEY` geändert?

## Nach SECRET_KEY Änderung

Alle Sessions sind ungültig. Bitte neu einloggen.
