# Release Notes: v0.2.0-alpha

## Überblick

RouteForge v0.2.0-alpha ist ein selfhosted, read-only Preflight- und Explainability-Tool für BGP/RPKI/RIPE-nahe Prüfabläufe.  
Diese Alpha-Version ist für Demos, frühes Feedback und nachvollziehbare Erstbewertungen gedacht.

## Highlights

- Change Preflight Mode
- Routing Visibility Check
- Modernisierte Operator-GUI
- RPKI + Registry/IRR + Routing Visibility Gesamtbewertung
- Demo-Modus weiterhin read-only

## Enthaltene Funktionen

- ASN Check (inkl. Prefix-Extraktion aus sichtbaren Ankündigungen)
- Prefix Check mit optionalem Origin-AS
- RPKI Einzelprüfung im Prefix-Check
- ASN-RPKI-Batchprüfung für sichtbare Prefixe
- Registry/IRR-Plausibilitätscheck
- Kombinierte Prefix-Gesamtbewertung mit Einzelprüfungen
- Routing Visibility Check als zusätzliche read-only Alpha-Prüfung
- Reports in JSON, Markdown und HTML
- Demo-Modus mit festen Beispieldaten
- Robuste Parser und CI-Basis

## Nicht enthalten

- Keine neuen externen Datenquellen
- Keine Schreibzugriffe auf Registries/IRR-Systeme
- Keine ROA-Erstellung
- Kein Router-Deployment
- Keine EVPN/VXLAN-Funktionalität
- Keine große Refaktorierung bestehender Endpoints

## Read-only Sicherheitsmodell

RouteForge arbeitet in v0.2.0-alpha vollständig read-only.  
Das Tool sammelt, normalisiert und bewertet Daten, nimmt aber keine operativen Änderungen an Routing-Infrastruktur oder Registry-Systemen vor.

## Demo-Modus

Mit `ROUTEFORGE_DEMO_MODE=true` nutzt RouteForge feste Beispieldaten für reproduzierbare Vorführungen und Offline-Demos.  
**Demo data, not for operational use.**

## Bekannte Einschränkungen

- RIPEstat-/Whois-Strukturen können variieren und unterschiedliche Detailgrade liefern.
- Registry/IRR Check ist eine Plausibilitätsprüfung, keine autoritative Entscheidung.
- Demo-Modus nutzt feste Beispieldaten und ist nicht für operative Entscheidungen geeignet.
- Keine Schreibzugriffe (read-only by design).
- Kein lokaler RPKI Validator enthalten.
- Noch keine RIPE Atlas Messungen.
- Noch keine historische Trendanalyse.

## Beispielablauf

1. RouteForge im Demo-Modus starten.
2. ASN Check für eine Beispiel-ASN ausführen.
3. ASN-RPKI-Batchprüfung der sichtbaren Prefixe starten.
4. Prefix + Origin-AS einzeln prüfen.
5. Gesamtbewertung und Einzelprüfungen vergleichen.
6. Markdown-Report kopieren und im Team teilen.

## Nächste geplante Schritte

- Dokumentation und Demo-Artefakte weiter schärfen.
- UI-Microcopy für technische Zielgruppen weiter vereinfachen.
- Weitere Beispielreports für typische Warn-/Unknown-Szenarien ergänzen.
- Stabilität, Testabdeckung und Präsentationsreife vor breiterem Alpha-Feedback erhöhen.

- Added Change Preflight Mode (alpha): read-only planned Prefix-Origin assessment with no ROA creation, no registry writes, and no router deployment.
