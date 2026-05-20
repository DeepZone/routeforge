from app.config import settings
from app.core.holder_extraction import extract_holder
from app.core.normalize import format_asn, normalize_asn, validate_prefix
from app.core.preflight_evaluation import evaluate_preflight
from app.services.registry_checker import RegistryChecker
from app.services.ripe_db_client import RipeDbClient
from app.services.ripe_stat_client import RipeStatClient
from app.services.routing_visibility_checker import RoutingVisibilityChecker
from app.services.rpki_checker import RpkiChecker


class PreflightChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client
        self.ripe_db = RipeDbClient(client)
        self.rpki = RpkiChecker(client)
        self.registry = RegistryChecker()
        self.routing_visibility = RoutingVisibilityChecker()

    def check(self, prefix: str, planned_origin_as: str) -> dict:
        normalized_prefix = validate_prefix(prefix)
        normalized_origin = format_asn(normalize_asn(planned_origin_as))

        whois = self.ripe_db.whois(normalized_prefix)
        routing_status = self.client.get("routing-status", {"resource": normalized_prefix})
        rpki_check = self.rpki.check(normalized_prefix, normalized_origin)
        registry_check = self.registry.check(normalized_prefix, normalized_origin, whois)
        routing_visibility_check = self.routing_visibility.check(normalized_prefix, normalized_origin, routing_status)

        visible_origins = sorted((routing_visibility_check.get("raw", {}) or {}).get("visible_origins", []))
        conflicts = [asn for asn in visible_origins if asn != normalized_origin]
        warnings: list[str] = []
        if not visible_origins:
            warnings.append("No visible origin was confirmed for this prefix.")
        if routing_visibility_check.get("status") == "UNKNOWN":
            warnings.append("Routing visibility could not be verified.")

        overall = evaluate_preflight(rpki_check, registry_check, routing_visibility_check, normalized_prefix, normalized_origin)
        decision_map = {"OK": "GO", "WARNING": "CAUTION", "CRITICAL": "NO-GO", "UNKNOWN": "UNKNOWN"}

        return {
            **overall,
            "input": {"prefix": normalized_prefix, "planned_origin_as": normalized_origin},
            "checks": {
                "rpki": rpki_check,
                "registry": registry_check,
                "routing_visibility": routing_visibility_check,
            },
            "details": {
                "preflight_mode": True,
                "preflight_decision": decision_map.get(overall.get("status"), "UNKNOWN"),
                "visible_origins": visible_origins,
                "planned_origin_as": normalized_origin,
                "resource_holder": extract_holder(
                    {"_source": "whois", **(whois if isinstance(whois, dict) else {})},
                    {"_source": "prefix-overview", **(routing_status.get("data", {}) if isinstance(routing_status, dict) and isinstance(routing_status.get("data"), dict) else {})},
                    {"_source": "registry", **(registry_check.get("raw", {}) if isinstance(registry_check.get("raw"), dict) else {})},
                ),
                "conflicts": conflicts,
                "source_errors": {
                    "whois": whois.get("error") if isinstance(whois, dict) else None,
                    "routing_status": routing_status.get("error") if isinstance(routing_status, dict) else None,
                    "rpki": rpki_check.get("raw", {}).get("error") if isinstance(rpki_check.get("raw"), dict) else None,
                    "registry": registry_check.get("raw", {}).get("error") if isinstance(registry_check.get("raw"), dict) else None,
                },
                "warnings": warnings,
                "demo_mode": settings.demo_mode,
            },
            "sources": ["RIPEstat rpki-validation", "RIPEstat whois", "RIPEstat routing-status"],
        }
