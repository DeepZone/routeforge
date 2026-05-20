from app.core.normalize import format_asn, normalize_asn, validate_prefix
from app.core.source_diagnostics import NO_DATA, UNKNOWN_STRUCTURE
from app.core.prefix_evaluation import evaluate_prefix_overall
from app.core.status import CheckStatus
from app.config import settings
from app.core.holder_extraction import extract_holder
from app.services.registry_checker import RegistryChecker
from app.services.routing_visibility_checker import RoutingVisibilityChecker
from app.services.ripe_db_client import RipeDbClient
from app.services.ripe_stat_client import RipeStatClient
from app.services.rpki_checker import RpkiChecker


class PrefixChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client
        self.ripe_db = RipeDbClient(client)
        self.rpki = RpkiChecker(client)
        self.registry = RegistryChecker()
        self.routing_visibility = RoutingVisibilityChecker()

    def check(self, prefix: str, origin_as: str | None) -> dict:
        normalized_prefix = validate_prefix(prefix)
        normalized_origin = format_asn(normalize_asn(origin_as)) if origin_as else None

        whois, whois_diag = self.client.get_with_diagnostics("whois", {"resource": normalized_prefix})
        whois = whois or {}
        routing_status, routing_diag = self.client.get_with_diagnostics("routing-status", {"resource": normalized_prefix})
        routing_status = routing_status or {}
        rpki_check = self.rpki.check(normalized_prefix, normalized_origin)
        registry_check = self.registry.check(normalized_prefix, normalized_origin, whois)
        routing_visibility_check = self.routing_visibility.check(normalized_prefix, normalized_origin, routing_status)

        source_diagnostics = [rpki_check.get("source_diagnostic"), whois_diag, routing_diag]
        if routing_visibility_check.get("raw", {}).get("structure_unknown"):
            routing_diag["status"] = UNKNOWN_STRUCTURE
            routing_diag["message"] = "Response received, but visible origins could not be extracted"
        if not whois.get("data") and not whois.get("error"):
            whois_diag["status"] = NO_DATA
            whois_diag["message"] = "No registry data available in response"

        warnings: list[str] = []
        if whois.get("error") or routing_status.get("error"):
            warnings.append("Mindestens eine zusätzliche Datenquelle war nicht erreichbar.")
        if rpki_check.get("status") == CheckStatus.UNKNOWN.value and rpki_check.get("raw", {}).get("error"):
            warnings.append("RPKI-Quelle nicht erreichbar oder unvollständig.")
        if routing_visibility_check.get("status") == CheckStatus.UNKNOWN.value:
            warnings.append("Routing-Sichtbarkeit konnte nicht belastbar bestimmt werden.")

        overall = evaluate_prefix_overall(rpki_check, registry_check, routing_visibility_check, normalized_prefix, normalized_origin)

        return {
            "status": overall["status"],
            "summary": overall["summary"],
            "explanation": overall["explanation"],
            "risk": overall["risk"],
            "recommendations": overall["recommendations"],
            "input": {"prefix": normalized_prefix, "origin_as": normalized_origin},
            "checks": {
                "rpki": {
                    "status": rpki_check["status"],
                    "summary": rpki_check["summary"],
                    "explanation": rpki_check["explanation"],
                    "risk": rpki_check["risk"],
                    "recommendations": rpki_check["recommendations"],
                    "raw": rpki_check.get("raw", {}),
                },
                "registry": {
                    "status": registry_check["status"],
                    "summary": registry_check["summary"],
                    "explanation": registry_check["explanation"],
                    "risk": registry_check["risk"],
                    "recommendations": registry_check["recommendations"],
                    "raw": registry_check.get("raw", {}),
                },
                "routing_visibility": {
                    "status": routing_visibility_check["status"],
                    "summary": routing_visibility_check["summary"],
                    "explanation": routing_visibility_check["explanation"],
                    "risk": routing_visibility_check["risk"],
                    "recommendations": routing_visibility_check["recommendations"],
                    "raw": routing_visibility_check.get("raw", {}),
                },
            },
            "details": {
                "whois": whois,
                "routing_status": routing_status,
                "resource_holder": extract_holder(
                    {"_source": "whois", **(whois if isinstance(whois, dict) else {})},
                    {"_source": "prefix-overview", **(routing_status.get("data", {}) if isinstance(routing_status, dict) and isinstance(routing_status.get("data"), dict) else {})},
                    {"_source": "registry", **(registry_check.get("raw", {}) if isinstance(registry_check.get("raw"), dict) else {})},
                ),
                "source_errors": {
                    "whois": whois.get("error"),
                    "routing_status": routing_status.get("error"),
                    "rpki": rpki_check.get("raw", {}).get("error") if isinstance(rpki_check.get("raw"), dict) else None,
                    "registry": registry_check.get("raw", {}).get("error") if isinstance(registry_check.get("raw"), dict) else None,
                    "routing_visibility": routing_visibility_check.get("raw", {}).get("routing_payload", {}).get("error") if isinstance(routing_visibility_check.get("raw"), dict) else None,
                },
                "warnings": warnings,
                "source_diagnostics": [d for d in source_diagnostics if isinstance(d, dict)],
                "demo_mode": settings.demo_mode,
            },
            "sources": ["RIPEstat rpki-validation", "RIPEstat routing-status", "RIPEstat whois", "RIPEstat routing visibility"],
        }
