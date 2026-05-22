from app.core.status import CheckStatus
import re


class RegistryChecker:
    def check(self, prefix: str, origin_as: str | None, whois_payload: dict) -> dict:
        if not isinstance(whois_payload, dict) or whois_payload.get("error"):
            return {
                "status": CheckStatus.UNKNOWN.value,
                "summary": "Registry-/IRR-Daten konnten nicht bestimmt werden",
                "explanation": "Die Whois-/Registry-Datenquelle war nicht erreichbar oder lieferte einen Fehler.",
                "risk": "The assessment is incomplete.",
                "recommendations": [
                    "Prüfe die Rohdaten der Registry-Quelle.",
                    "Retry the query later.",
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
            "risk": "Möglicher Konfigurations- oder Registry-Fehler mit Hijack-Risk.",
            "recommendations": [
                "Origin-AS und route/route6-Objekte in der zuständigen Registry abgleichen.",
                "Fehlerhafte Registry-Einträge korrigieren.",
            ],
            "raw": whois_payload,
        }

    def _extract_route_origins(self, payload: dict) -> set[str]:
        origins: set[str] = set()
        data = payload.get("data", {}) if isinstance(payload, dict) else {}

        for record in self._walk_records(data):
            route_seen, normalized_origin = self._extract_fields_from_record(record)
            if route_seen and normalized_origin:
                origins.add(normalized_origin)

        return origins

    def _walk_records(self, data: dict):
        sources = []
        if isinstance(data, dict):
            sources.extend([data.get("irr_records"), data.get("records")])
            if "fields" in data:
                sources.append(data.get("fields"))
        for source in sources:
            yield from self._walk_node(source)

    def _walk_node(self, node):
        if isinstance(node, dict):
            if isinstance(node.get("fields"), list):
                yield node
            else:
                for value in node.values():
                    yield from self._walk_node(value)
            return

        if isinstance(node, list):
            if self._looks_like_field_list(node):
                yield node
            else:
                for item in node:
                    yield from self._walk_node(item)

    def _looks_like_field_list(self, node: list) -> bool:
        return bool(node) and all(isinstance(item, dict) and "key" in item for item in node)

    def _extract_fields_from_record(self, record) -> tuple[bool, str | None]:
        route_seen = False
        current_origin: str | None = None
        text_blobs: list[str] = []

        fields = []
        if isinstance(record, dict):
            maybe_fields = record.get("fields")
            if isinstance(maybe_fields, list):
                fields = maybe_fields
            else:
                fields = [record]
        elif isinstance(record, list):
            fields = record

        for field in fields:
            if isinstance(field, dict):
                key = str(field.get("key", "")).strip().lower()
                value = str(field.get("value", "")).strip()
                if key in {"route", "route6"} and value:
                    route_seen = True
                elif key == "origin":
                    normalized = self._normalize_origin(value)
                    if normalized:
                        current_origin = normalized
                text_blobs.extend([key, value])
            elif isinstance(field, str):
                text_blobs.append(field)

        if route_seen and current_origin:
            return True, current_origin

        combined_text = " ".join(part for part in text_blobs if part)
        if not route_seen and re.search(r"\broute6?\b\s*:", combined_text, re.IGNORECASE):
            route_seen = True
        if not route_seen and re.search(r"\broute6?\b\s+\S+", combined_text, re.IGNORECASE):
            route_seen = True

        if route_seen and not current_origin:
            origin_match = re.search(r"\borigin\b\s*:?\s*(AS)?\s*(\d+)\b", combined_text, re.IGNORECASE)
            if origin_match:
                current_origin = self._normalize_origin(origin_match.group(0))

        return route_seen, current_origin

    def _normalize_origin(self, value: str) -> str | None:
        if not value:
            return None
        cleaned = str(value).strip().upper()
        match = re.search(r"\b(AS)?\s*(\d+)\b", cleaned)
        if not match:
            return None
        return f"AS{match.group(2)}"
