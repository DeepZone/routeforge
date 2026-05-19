from __future__ import annotations

from collections.abc import Iterator

from app.core.normalize import format_asn, normalize_asn
from app.core.status import CheckStatus


class RoutingVisibilityChecker:
    _ASN_FIELDS = {"origin", "origin_as", "origin_asn", "asn"}
    _CONTAINER_FIELDS = {"origins", "observed_origins", "visibility", "routes", "entries", "data"}

    def check(self, prefix: str, origin_as: str | None, routing_payload: dict | None = None) -> dict:
        _ = prefix
        payload = routing_payload if isinstance(routing_payload, dict) else None
        expected_origin = format_asn(normalize_asn(origin_as)) if origin_as else None

        if not payload or payload.get("error"):
            return self._result_unknown(payload)

        visible_origins = self._extract_visible_origins(payload)
        raw = {"routing_payload": payload, "visible_origins": sorted(visible_origins)}

        if not visible_origins:
            return {
                "status": CheckStatus.WARNING.value,
                "summary": "Prefix visibility unclear",
                "explanation": "Es wurden Routingdaten gefunden, aber kein klares sichtbares Origin-AS extrahiert.",
                "risk": "Das Prefix könnte nicht sichtbar sein oder die Datenstruktur wurde nicht eindeutig erkannt.",
                "recommendations": [
                    "Prüfe das Prefix zusätzlich über ein Looking Glass.",
                    "Prüfe, ob das Prefix aktuell announced werden soll.",
                ],
                "raw": raw,
            }

        if not expected_origin:
            return {
                "status": CheckStatus.OK.value,
                "summary": "Visible routing origins found",
                "explanation": "Für das Prefix wurden sichtbare Origin-ASNs gefunden. Ohne erwartetes Origin-AS erfolgt kein Konsistenzabgleich.",
                "risk": "Die Sichtbarkeit ist grundsätzlich erkennbar, aber die erwartete Origin-Zuordnung wurde nicht geprüft.",
                "recommendations": ["Gib ein erwartetes Origin-AS an, um die Sichtbarkeit vollständig zu bewerten."],
                "raw": raw,
            }

        if expected_origin in visible_origins:
            return {
                "status": CheckStatus.OK.value,
                "summary": "Prefix is visible with expected Origin-AS",
                "explanation": "Das Prefix wird mit dem erwarteten Origin-AS im Routing sichtbar.",
                "risk": "Keine offensichtliche Routing-Visibility-Inkonsistenz erkannt.",
                "recommendations": ["Routing-Sichtbarkeit weiter überwachen."],
                "raw": raw,
            }

        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "Visible Origin-AS differs from expected Origin-AS",
            "explanation": "Das Prefix ist sichtbar, aber nicht mit dem erwarteten Origin-AS.",
            "risk": "Möglicher Routing-Fehler, falsches Announcement oder Hijack-Risiko.",
            "recommendations": [
                "Sichtbares Origin-AS prüfen.",
                "BGP Announcement und Upstream-Konfiguration prüfen.",
                "RPKI und Registry/IRR-Daten gegenprüfen.",
            ],
            "raw": raw,
        }

    def _result_unknown(self, payload: dict | None) -> dict:
        return {
            "status": CheckStatus.UNKNOWN.value,
            "summary": "Routing visibility could not be determined",
            "explanation": "Die Sichtbarkeit des Prefixes im globalen Routing konnte aus den verfügbaren Daten nicht zuverlässig bestimmt werden.",
            "risk": "Die Bewertung ist unvollständig.",
            "recommendations": [
                "Prüfe die Rohdaten.",
                "Wiederhole die Abfrage später.",
                "Vergleiche bei Bedarf mit einer zweiten Routing-Quelle oder einem Looking Glass.",
            ],
            "raw": {"routing_payload": payload or {}},
        }

    def _extract_visible_origins(self, payload: dict) -> set[str]:
        origins: set[str] = set()
        for key, value in self._walk_node(payload):
            if key in self._ASN_FIELDS:
                asn = self._normalize_asn(value)
                if asn:
                    origins.add(asn)
            elif key in self._CONTAINER_FIELDS and isinstance(value, (list, tuple, set)):
                for item in value:
                    asn = self._normalize_asn(item)
                    if asn:
                        origins.add(asn)
        return origins

    def _normalize_asn(self, value: object) -> str | None:
        if isinstance(value, int):
            return f"AS{value}" if value > 0 else None
        if isinstance(value, str):
            stripped = value.strip().upper()
            if not stripped:
                return None
            if stripped.startswith("AS") and stripped[2:].isdigit():
                return stripped
            if stripped.isdigit():
                return f"AS{stripped}"
        return None

    def _walk_node(self, node: object) -> Iterator[tuple[str | None, object]]:
        if isinstance(node, dict):
            for key, value in node.items():
                normalized_key = key.lower() if isinstance(key, str) else None
                yield normalized_key, value
                yield from self._walk_node(value)
        elif isinstance(node, list):
            for item in node:
                yield from self._walk_node(item)
