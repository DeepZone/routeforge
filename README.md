# RouteForge v0.1.0-alpha

RouteForge ist ein selfhosted, read-only Preflight- und Explainability-Tool für BGP/RPKI/RIPE-Daten.

## Was kann v0.1?
- ASN Check (RIPEstat as-overview + announced-prefixes)
- Prefix Check (routing-status, whois, optional rpki-validation mit Origin-AS)
- ASN-RPKI-Batchprüfung für sichtbare Prefixe
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

## Typische Nutzung

### 1) Prefix gegen Origin-AS prüfen
```bash
curl -X POST http://localhost:8000/api/check/prefix \
  -H "Content-Type: application/json" \
  -d '{"prefix":"193.0.6.0/24","origin_as":"AS3333"}'
```

### 2) ASN prüfen
```bash
curl -X POST http://localhost:8000/api/check/asn \
  -H "Content-Type: application/json" \
  -d '{"asn":"AS3320"}'
```

### 3) RPKI Batchprüfung für sichtbare Prefixe einer ASN
```bash
curl -X POST http://localhost:8000/api/check/asn-rpki \
  -H "Content-Type: application/json" \
  -d '{"asn":"AS3320","limit":25}'
```

## Statuswerte

- **OK:** Keine akute Auffälligkeit im geprüften Kontext.
- **WARNING:** Prüfung war möglich, aber es gibt Hinweise wie fehlende ROA-Abdeckung oder unvollständige Daten.
- **CRITICAL:** Es wurde ein kritisches RPKI-Problem gefunden, zum Beispiel `invalid_asn` oder `invalid_length`.
- **UNKNOWN:** Die Bewertung konnte nicht zuverlässig durchgeführt werden, zum Beispiel wegen fehlender Daten oder API-Fehlern.


## Registry/IRR Check

Der Prefix Check enthält zusätzlich einen read-only Registry/IRR-Plausibilitätscheck auf Basis verfügbarer RIPEstat-/Whois-/Registry-Daten.
Der Check bewertet Hinweise auf route/route6-Objekte und eine mögliche Origin-AS-Plausibilität, liefert bei unklarer Datenlage bewusst `UNKNOWN` oder `WARNING` und zeigt Rohdaten zur Nachvollziehbarkeit an.
Er ersetzt keine manuelle Registry-Prüfung.


## Kombinierte Prefix-Bewertung

RouteForge bewertet Prefix-Checks nicht nur anhand einer einzelnen Quelle. RPKI und Registry/IRR werden getrennt angezeigt, aber zusätzlich zu einer Gesamtbewertung zusammengeführt.
Ein `CRITICAL` aus einer Einzelprüfung bleibt `CRITICAL` in der Gesamtbewertung. `WARNING` weist auf unvollständige oder unsichere Datenlage hin.

## Demo-Modus

`ROUTEFORGE_DEMO_MODE=true` nutzt feste Beispieldaten und ist für Präsentationen, Tests und Offline-Demos gedacht.  
Der Demo-Modus darf nicht für echte Routing-Bewertungen verwendet werden.

Beispiel per Umgebungsvariable:
```bash
ROUTEFORGE_DEMO_MODE=true docker compose up --build
```

Alternativ über `.env`:
```env
ROUTEFORGE_DEMO_MODE=true
```

## Tests ausführen

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

## CLI Beispiele
```bash
cd backend
routeforge check-asn AS3320
routeforge check-prefix 193.0.22.0/23 --origin-as AS3333
routeforge report 1 --format markdown
```

## Datenquellen
- RIPEstat Data API: https://stat.ripe.net/docs/02.data-api
- RPKI Validation Endpoint: https://stat.ripe.net/docs/data-api/api-endpoints/rpki-validation
- RIPEstat Dokumentation: https://www.ripe.net/publications/documentation/ripestat-documentation/

## Security Hinweis
RouteForge v0.1.0-alpha ist vollständig read-only.
