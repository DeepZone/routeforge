import ipaddress

from app.core.normalize import format_asn, normalize_asn, validate_prefix
from app.services.ripe_stat_client import RipeStatClient


class RoaPlannerService:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def check(self, prefix: str, origin_as: str, max_length: int | None = None) -> dict:
        normalized_prefix = validate_prefix(prefix)
        normalized_origin = format_asn(normalize_asn(origin_as))
        network = ipaddress.ip_network(normalized_prefix, strict=False)
        prefix_length = network.prefixlen
        effective_max_length = max_length if max_length is not None else prefix_length

        diagnostics: list[dict] = []
        recommendations: list[str] = []
        matching_roas: list[dict] = []
        conflicting_roas: list[dict] = []

        if effective_max_length < prefix_length:
            return {
                "status": "CRITICAL",
                "summary": "Max Length ist kleiner als die Prefixlänge und damit ungültig.",
                "recommendations": ["Setzen Sie max_length mindestens auf die Prefixlänge.", "Prüfen Sie Prefix und Eingaben auf Tippfehler."],
                "details": {
                    "prefix": normalized_prefix,
                    "origin_as": normalized_origin,
                    "max_length": max_length,
                    "effective_max_length": effective_max_length,
                    "prefix_length": prefix_length,
                    "planned_validation_state": "invalid",
                    "matching_roas": matching_roas,
                    "conflicting_roas": conflicting_roas,
                    "suggested_roa": {"prefix": normalized_prefix, "origin_as": normalized_origin, "max_length": prefix_length},
                    "max_length_risk": "invalid_too_small",
                    "recommendations": recommendations,
                    "source_diagnostics": diagnostics,
                },
            }

        roas_payload, roas_diag = self.client.get_with_diagnostics("rpki-validation", {"resource": normalized_prefix})
        diagnostics.append(roas_diag)
        if not roas_payload or not isinstance(roas_payload, dict):
            return self._unknown(normalized_prefix, normalized_origin, max_length, effective_max_length, prefix_length, diagnostics)

        validating_roas = (((roas_payload.get("data") or {}).get("validating_roas")) or [])
        if not isinstance(validating_roas, list):
            validating_roas = []

        for roa in validating_roas:
            try:
                roa_origin = format_asn(normalize_asn(str(roa.get("origin") or roa.get("origin_asn") or "")))
                roa_prefix = str(roa.get("prefix") or "")
                roa_max_len = int(roa.get("max_length") or roa.get("maxlength") or ipaddress.ip_network(roa_prefix, strict=False).prefixlen)
            except Exception:
                continue
            record = {"prefix": roa_prefix, "origin_as": roa_origin, "max_length": roa_max_len}
            if roa_origin == normalized_origin and roa_max_len >= prefix_length:
                matching_roas.append(record)
            elif roa_origin != normalized_origin:
                conflicting_roas.append(record)
            elif roa_max_len < prefix_length:
                conflicting_roas.append({**record, "reason": "max_length_too_small"})

        planned_validation_state = "not_found"
        status = "WARNING"
        summary = "Keine passende ROA gefunden; ein read-only Vorschlag wurde erstellt."
        max_length_risk = "none"

        if matching_roas:
            planned_validation_state = "valid"
            status = "OK"
            summary = "Geplantes Announcement ist durch mindestens eine passende ROA abgedeckt."
            recommendations.append("Bestehende ROA-Abdeckung ist vorhanden; Änderungen außerhalb von RouteForge nur bei Bedarf durchführen.")

        if conflicting_roas and not matching_roas:
            planned_validation_state = "invalid"
            status = "CRITICAL"
            summary = "Konfliktierende ROAs deuten auf ein invalides geplantes Announcement hin."
            recommendations.append("Origin-AS oder Prefixplanung prüfen; bestehende ROA-Konflikte außerhalb von RouteForge bereinigen.")

        if effective_max_length > prefix_length + 2:
            max_length_risk = "broad"
            if status == "OK":
                status = "WARNING"
            recommendations.append("Max Length ist relativ breit gewählt; reduzieren Sie die Breite, um Hijack-Risiko zu senken.")

        suggested_roa = None if matching_roas else {"prefix": normalized_prefix, "origin_as": normalized_origin, "max_length": effective_max_length}
        if suggested_roa:
            recommendations.append("ROA-Vorschlag extern durch LIR/Operator prüfen und außerhalb von RouteForge umsetzen.")

        return {
            "status": status,
            "summary": summary,
            "recommendations": recommendations or ["Keine zusätzlichen Empfehlungen."],
            "details": {
                "prefix": normalized_prefix,
                "origin_as": normalized_origin,
                "max_length": max_length,
                "effective_max_length": effective_max_length,
                "prefix_length": prefix_length,
                "planned_validation_state": planned_validation_state,
                "matching_roas": matching_roas,
                "conflicting_roas": conflicting_roas,
                "suggested_roa": suggested_roa,
                "max_length_risk": max_length_risk,
                "recommendations": recommendations,
                "source_diagnostics": diagnostics,
            },
            "input": {"prefix": normalized_prefix, "origin_as": normalized_origin, "max_length": max_length},
        }

    def _unknown(self, prefix: str, origin_as: str, max_length: int | None, effective_max_length: int, prefix_length: int, diagnostics: list[dict]) -> dict:
        return {
            "status": "UNKNOWN",
            "summary": "RPKI-Datenquelle liefert aktuell keine belastbare Aussage.",
            "recommendations": ["Später erneut prüfen.", "Externe ROA-Quelle manuell validieren."],
            "details": {
                "prefix": prefix,
                "origin_as": origin_as,
                "max_length": max_length,
                "effective_max_length": effective_max_length,
                "prefix_length": prefix_length,
                "planned_validation_state": "unknown",
                "matching_roas": [],
                "conflicting_roas": [],
                "suggested_roa": {"prefix": prefix, "origin_as": origin_as, "max_length": effective_max_length},
                "max_length_risk": "unknown",
                "recommendations": ["Später erneut prüfen.", "Externe ROA-Quelle manuell validieren."],
                "source_diagnostics": diagnostics,
            },
            "input": {"prefix": prefix, "origin_as": origin_as, "max_length": max_length},
        }
