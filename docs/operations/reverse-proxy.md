# Reverse Proxy

## Empfehlung
Für einfaches Selfhosting wird **Variante A** empfohlen. Dabei zeigt Ihr externer Reverse Proxy nur auf den Frontend-Service. API-Aufrufe unter `/api` funktionieren automatisch über den internen Frontend-Nginx-Proxy.

## Variante A: Externer Proxy -> `frontend:80` (empfohlen)
- Externer Reverse Proxy leitet `/` an `frontend:80` weiter.
- Frontend-Nginx liefert SPA-Dateien aus.
- Frontend-Nginx proxied `/api/` intern an `backend:8000/api/`.
- Frontend-Nginx proxied `/health` intern an `backend:8000/health`.

Vorteile:
- Einfachste Konfiguration
- Kein separates externes `/api`-Routing nötig
- Keine hardcodierte Host-IP im Frontend-Build erforderlich

## Variante B: Externer Proxy split-routed `/` und `/api`
- Externer Reverse Proxy leitet `/` an `frontend:80` weiter.
- Externer Reverse Proxy leitet `/api/` direkt an `backend:8000/api/` weiter.
- Optional `/health` direkt an `backend:8000/health`.

Diese Variante ist nur für spezielle Setups nötig (z. B. wenn API-Traffic getrennt behandelt werden soll).

## Nginx Proxy Manager Beispiel
- Proxy Host Domain `routeforge.example.com` -> `frontend:80`.
- Bei Variante B zusätzliche Advanced Locations für `/api` und optional `/health` auf `backend:8000`.
- HTTPS-Zertifikat aktivieren (Let's Encrypt empfohlen).

## Classic Nginx Beispiele

### Variante A (empfohlen)
```nginx
server {
  listen 443 ssl;
  server_name routeforge.example.com;

  location / {
    proxy_pass http://frontend:80;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

### Variante B (nur bei Bedarf)
```nginx
server {
  listen 443 ssl;
  server_name routeforge.example.com;

  location / {
    proxy_pass http://frontend:80;
    proxy_set_header Host $host;
  }

  location /api/ {
    proxy_pass http://backend:8000/api/;
    proxy_set_header Host $host;
  }

  location /health {
    proxy_pass http://backend:8000/health;
  }
}
```

## HTTPS und CORS
- HTTPS-Termination bevorzugt im externen Proxy.
- Bei Standard-Setup mit Variante A sind Browser-API-Calls same-origin (`/api` über denselben Host).
- `CORS_ORIGINS` ist primär relevant für getrennte Frontend/Backend-Deployments.

## Security-Hinweis
- Backend-Port `8000` nur exponieren, wenn benötigt (z. B. Diagnose).
- Wenn Frontend bereits sauber über Proxy bereitgestellt wird, Backend nach Möglichkeit intern halten.
