# RouteForge v0.2.0-alpha

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


## Routing Visibility Check

Der Routing Visibility Check prüft read-only, ob aus verfügbaren RIPEstat-Routingdaten sichtbare Origin-ASNs für ein Prefix abgeleitet werden können.
Er ersetzt kein vollständiges BGP-Monitoring und keine manuelle Looking-Glass-Prüfung.

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

## Alpha Demo Flow

1. Demo-Modus starten (`ROUTEFORGE_DEMO_MODE=true`).
2. ASN Check ausführen.
3. ASN-RPKI-Batchprüfung starten.
4. Prefix + Origin-AS prüfen.
5. Gesamtbewertung und Einzelprüfungen lesen.
6. Markdown Report kopieren.

## Bekannte Einschränkungen

- RIPEstat-/Whois-Strukturen können je nach Antwort variieren.
- Der Registry/IRR Check ist eine Plausibilitätsprüfung und keine autoritative Entscheidung.
- Der Demo-Modus nutzt feste Beispieldaten.
- RouteForge arbeitet vollständig read-only (keine Schreibzugriffe).
- Es gibt noch keinen lokalen RPKI Validator.
- RIPE Atlas Messungen sind noch nicht integriert.
- Eine historische Trendanalyse ist noch nicht enthalten.

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
RouteForge v0.2.0-alpha ist vollständig read-only.


## Change Preflight Mode
RouteForge kann geplante Prefix-Origin-Announcements read-only prüfen. Es erzeugt keine ROAs, ändert keine Registry-Daten und deployt keine Router-Konfiguration.

```bash
curl -X POST http://localhost:8000/api/check/preflight \
  -H "Content-Type: application/json" \
  -d '{"prefix":"203.0.113.0/24","planned_origin_as":"AS64500"}'
```

## Result clarity and holder display

RouteForge stellt Ergebnisse mit klarer Ergebnis-Zusammenfassung dar und versucht den Holder (Ressource-Inhaber) aus vorhandenen AS-/Prefix-/Whois-/Registry-Daten abzuleiten.
Wenn keine belastbare Quelle vorhanden ist, zeigt RouteForge **"Unknown"** an.
Die Holder-Erkennung ist **read-only**, rein informativ und führt keine Schreiboperationen (keine ROA-Erstellung, keine RIPE-DB-Änderungen, kein Deployment) aus.

## Export and sharing

RouteForge Reports können als **Markdown**, **HTML** oder als kurze **Plain-Text Summary** exportiert werden.
Die Summary ist für Change-Tickets, Maintenance-Dokumentation oder interne Reviews gedacht.

```bash
curl http://localhost:8000/api/reports/1/summary
curl http://localhost:8000/api/reports/1/markdown -o routeforge-report.md
curl http://localhost:8000/api/reports/1/html -o routeforge-report.html
```
