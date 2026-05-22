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
                "summary": "Max length is smaller than the prefix length and is therefore invalid.",
                "recommendations": ["Set max_length to at least the prefix length.", "Check the prefix and inputs for typos."],
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
        summary = "No matching ROA found; a read-only proposal was created."
        max_length_risk = "none"

        if matching_roas:
            planned_validation_state = "valid"
            status = "OK"
            summary = "Geplantes Announcement ist durch mindestens eine passende ROA abgedeckt."
            recommendations.append("Existing ROA coverage is present; apply changes outside RouteForge only if needed.")

        if conflicting_roas and not matching_roas:
            planned_validation_state = "invalid"
            status = "CRITICAL"
            summary = "Konfliktierende ROAs deuten auf ein invalides geplantes Announcement hin."
            recommendations.append("Review origin AS or prefix planning; resolve existing ROA conflicts outside RouteForge.")

        if effective_max_length > prefix_length + 2:
            max_length_risk = "broad"
            if status == "OK":
                status = "WARNING"
            recommendations.append("Max length is relatively broad; reduce it to lower hijack risk.")

        suggested_roa = None if matching_roas else {"prefix": normalized_prefix, "origin_as": normalized_origin, "max_length": effective_max_length}
        if suggested_roa:
            recommendations.append("Review the ROA proposal externally with LIR/operator and implement it outside RouteForge.")

        return {
            "status": status,
            "summary": summary,
            "recommendations": recommendations or ["No additional recommendations."],
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
            "summary": "RPKI data source currently does not provide a reliable result.",
            "recommendations": ["Check again later.", "Manually validate against an external ROA source."],
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
                "recommendations": ["Check again later.", "Manually validate against an external ROA source."],
                "source_diagnostics": diagnostics,
            },
            "input": {"prefix": prefix, "origin_as": origin_as, "max_length": max_length},
        }
