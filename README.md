# RouteForge v0.1

RouteForge ist ein selfhosted, read-only Preflight- und Explainability-Tool für BGP/RPKI/RIPE-Daten.

## Was kann v0.1?
- ASN Check (RIPEstat as-overview + announced-prefixes)
- Prefix Check (routing-status, whois, optional rpki-validation mit Origin-AS)
- Ampelstatus: OK, WARNING, CRITICAL, UNKNOWN
- Reports als JSON, Markdown, HTML
- REST API, Web UI, Typer CLI

## Was kann v0.1 bewusst noch nicht?
- Keine RIPE DB Schreibzugriffe
- Keine ROA Erstellung
- Kein Router Deployment
- Keine EVPN/VXLAN Features
- Kein Cloud-Zwang

## Installation
```bash
docker compose up --build
```

Mit Hot Reload:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## API Beispiele
```bash
curl http://192.168.58.167:8000/health
curl -X POST http://192.168.58.167:8000/api/check/asn -H 'content-type: application/json' -d '{"asn":"AS3320"}'
curl -X POST http://192.168.58.167:8000/api/check/prefix -H 'content-type: application/json' -d '{"prefix":"193.0.22.0/23","origin_as":"AS3333"}'
```

## CLI Beispiele
```bash
cd backend
routeforge check-asn AS3320
routeforge check-prefix 193.0.22.0/23 --origin-as AS3333
routeforge report 1 --format markdown
```

## Debugging
```bash
docker compose logs -f backend
docker compose logs -f frontend

curl http://192.168.58.167:8000/health

curl -X POST http://192.168.58.167:8000/api/check/asn \
  -H "Content-Type: application/json" \
  -d '{"asn":"AS3320"}'

curl -X POST http://192.168.58.167:8000/api/check/prefix \
  -H "Content-Type: application/json" \
  -d '{"prefix":"193.0.6.0/24","origin_as":"AS3333"}'
```

## Datenquellen
- RIPEstat Data API: https://stat.ripe.net/docs/02.data-api
- RPKI Validation Endpoint: https://stat.ripe.net/docs/data-api/api-endpoints/rpki-validation
- RIPEstat Dokumentation: https://www.ripe.net/publications/documentation/ripestat-documentation/

## Security Hinweis
RouteForge v0.1 ist vollständig read-only.

## Roadmap
- v0.1: ASN/Prefix/RPKI Checks, Reports, Web UI, CLI
- v0.2: bessere RIPE DB/IRR Konsistenzchecks, mehr Routing-Sichtbarkeit, Report-Historie
- v0.3: RIPE Atlas Integration, aktive Messungen
- v0.4: optionaler FRR/BIRD Config Parser, weiterhin read-only
