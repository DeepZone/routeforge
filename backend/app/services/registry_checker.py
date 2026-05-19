from app.core.status import CheckStatus


class RegistryChecker:
    def check(self, prefix: str, origin_as: str | None, whois_payload: dict) -> dict:
        if not isinstance(whois_payload, dict) or whois_payload.get("error"):
            return {
                "status": CheckStatus.UNKNOWN.value,
                "summary": "Registry-/IRR-Daten konnten nicht bestimmt werden",
                "explanation": "Die Whois-/Registry-Datenquelle war nicht erreichbar oder lieferte einen Fehler.",
                "risk": "Die Bewertung ist unvollständig.",
                "recommendations": [
                    "Prüfe die Rohdaten der Registry-Quelle.",
                    "Wiederhole die Abfrage später.",
                    "Vergleiche das Ergebnis mit einer zweiten Registry-/IRR-Quelle.",
                ],
                "raw": whois_payload if isinstance(whois_payload, dict) else {},
            }

        route_origins = self._extract_route_origins(whois_payload)
        has_registry_data = bool(whois_payload.get("data") or route_origins)

        if not has_registry_data:
            return {
                "status": CheckStatus.UNKNOWN.value,
                "summary": "Keine verwertbaren Registry-/IRR-Daten gefunden",
                "explanation": "Die Quelle lieferte keine eindeutig parsebaren Daten zum Prefix.",
                "risk": "Es kann keine belastbare Plausibilitätsaussage getroffen werden.",
                "recommendations": [
                    "Prüfe das Prefix manuell in der zuständigen Registry.",
                    "Vergleiche die Daten mit einer alternativen Whois-/IRR-Quelle.",
                ],
                "raw": whois_payload,
            }

        if not route_origins:
            return {
                "status": CheckStatus.WARNING.value,
                "summary": "Registry-Daten vorhanden, aber kein route/route6-Hinweis gefunden",
                "explanation": "Es wurden allgemeine Whois-/Registry-Daten gefunden, jedoch kein klares route/route6-Objekt.",
                "risk": "Ohne route/route6-Hinweis bleibt die Origin-Plausibilität eingeschränkt.",
                "recommendations": [
                    "Prüfe, ob ein passendes route/route6-Objekt in der IRR gepflegt ist.",
                    "Validiere die Origin-Zuordnung zusätzlich manuell.",
                ],
                "raw": whois_payload,
            }

        if not origin_as:
            return {
                "status": CheckStatus.OK.value,
                "summary": "Route/route6-Hinweise gefunden",
                "explanation": "Es wurden route/route6-Objekte bzw. Origin-Hinweise zum Prefix gefunden. Ohne angegebenes Origin-AS erfolgt keine AS-Konsistenzprüfung.",
                "risk": "Grundsätzliche Registry-Plausibilität ist gegeben, AS-Abgleich ist offen.",
                "recommendations": [
                    "Für eine strengere Prüfung optional ein Origin-AS mitgeben.",
                ],
                "raw": whois_payload,
            }

        normalized_origin = origin_as.upper()
        if normalized_origin in route_origins:
            return {
                "status": CheckStatus.OK.value,
                "summary": "Plausibles route/route6-Origin gefunden",
                "explanation": f"Mindestens ein route/route6-Hinweis enthält das erwartete Origin {normalized_origin}.",
                "risk": "Keine offensichtliche Registry-Inkonsistenz erkannt.",
                "recommendations": [
                    "Registry-Daten regelmäßig aktuell halten.",
                ],
                "raw": whois_payload,
            }

        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "Route/route6-Origin widerspricht dem angegebenen Origin-AS",
            "explanation": f"Gefundene Origins: {', '.join(sorted(route_origins))}. Erwartet wurde {normalized_origin}.",
            "risk": "Möglicher Konfigurations- oder Registry-Fehler mit Hijack-Risiko.",
            "recommendations": [
                "Origin-AS und route/route6-Objekte in der zuständigen Registry abgleichen.",
                "Fehlerhafte Registry-Einträge korrigieren.",
            ],
            "raw": whois_payload,
        }

    def _extract_route_origins(self, payload: dict) -> set[str]:
        objects = payload.get("data", {}).get("irr_records") or payload.get("data", {}).get("records") or []
        origins: set[str] = set()

        for obj in objects:
            route_seen = False
            current_origin: str | None = None

            for field in obj if isinstance(obj, list) else []:
                key = str(field.get("key", "")).lower()
                value = str(field.get("value", "")).strip().upper()

                if key in {"route", "route6"} and value:
                    route_seen = True
                if key == "origin" and value.startswith("AS"):
                    current_origin = value

            if route_seen and current_origin:
                origins.add(current_origin)

        return origins
