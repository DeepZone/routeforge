# Reverse Proxy

## Recommended patterns
1. **Simple port exposure**: publish `3000` (frontend) and optionally `8000` (backend) on trusted networks.
2. **Domain + reverse proxy**: expose only proxy, keep backend internal where possible.

## Nginx Proxy Manager example
- Proxy Host domain `routeforge.example.com` -> `frontend:80`.
- Add advanced location `/api` -> `backend:8000`.
- Optional `/health` -> `backend:8000/health`.
- Enable HTTPS certificate (Let's Encrypt recommended).

## Classic Nginx example
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

## HTTPS and CORS
- Prefer HTTPS termination at proxy.
- Set `CORS_ORIGINS` to the public frontend origin(s).
- RouteForge currently does not require websocket proxy settings.

## Security note
- Avoid exposing backend directly to the internet if frontend is already proxied.
