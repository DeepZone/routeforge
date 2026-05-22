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
                "status": CheckStatus.UNKNOWN.value,
                "summary": "Routing visibility could not be determined",
                "explanation": "RIPEstat routing-status returned data, but RouteForge could not extract visible Origin-AS information from the response.",
                "risk": "The data structure could not be evaluated unambiguously.",
                "recommendations": [
                    "Check the prefix with an additional looking glass.",
                    "Verify whether the prefix should currently be announced.",
                ],
                "raw": {**raw, "structure_unknown": True},
            }

        if not expected_origin:
            return {
                "status": CheckStatus.OK.value,
                "summary": "Visible routing origins found",
                "explanation": "Visible origin ASNs were found for this prefix. Without an expected origin AS, no consistency comparison is performed.",
                "risk": "Visibility is generally confirmed, but the expected origin mapping was not validated.",
                "recommendations": ["Provide an expected origin AS to fully evaluate visibility."],
                "raw": {**raw, "structure_unknown": True},
            }

        if expected_origin in visible_origins:
            return {
                "status": CheckStatus.OK.value,
                "summary": "Prefix is visible with expected Origin-AS",
                "explanation": "Das Prefix wird mit dem erwarteten Origin-AS im Routing sichtbar.",
                "risk": "Keine offensichtliche Routing-Visibility-Inkonsistenz erkannt.",
                "recommendations": ["Continue monitoring routing visibility."],
                "raw": {**raw, "structure_unknown": True},
            }

        return {
            "status": CheckStatus.CRITICAL.value,
            "summary": "Visible Origin-AS differs from expected Origin-AS",
            "explanation": "The prefix is visible, but not with the expected origin AS.",
            "risk": "Possible routing error, incorrect announcement, or hijack risk.",
            "recommendations": [
                "Sichtbares Check the origin AS.",
                "Check BGP announcement and upstream configuration.",
                "Cross-check RPKI and Registry/IRR data.",
            ],
            "raw": raw,
        }

    def _result_unknown(self, payload: dict | None) -> dict:
        return {
            "status": CheckStatus.UNKNOWN.value,
            "summary": "Routing visibility could not be determined",
            "explanation": "RIPEstat routing-status did not respond before the configured timeout or returned no usable payload.",
            "risk": "The assessment is incomplete.",
            "recommendations": [
                "Check the raw data.",
                "Retry the query later.",
                "Compare with a secondary routing source or a looking glass if needed.",
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
