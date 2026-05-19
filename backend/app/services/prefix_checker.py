from app.core.normalize import format_asn, normalize_asn, validate_prefix
from app.core.prefix_evaluation import evaluate_prefix_overall
from app.core.status import CheckStatus
from app.config import settings
from app.services.registry_checker import RegistryChecker
from app.services.ripe_db_client import RipeDbClient
from app.services.ripe_stat_client import RipeStatClient
from app.services.rpki_checker import RpkiChecker


class PrefixChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client
        self.ripe_db = RipeDbClient(client)
        self.rpki = RpkiChecker(client)
        self.registry = RegistryChecker()

    def check(self, prefix: str, origin_as: str | None) -> dict:
        normalized_prefix = validate_prefix(prefix)
        normalized_origin = format_asn(normalize_asn(origin_as)) if origin_as else None

        whois = self.ripe_db.whois(normalized_prefix)
        routing_status = self.client.get("routing-status", {"resource": normalized_prefix})
        rpki_check = self.rpki.check(normalized_prefix, normalized_origin)
        registry_check = self.registry.check(normalized_prefix, normalized_origin, whois)

        warnings: list[str] = []
        if whois.get("error") or routing_status.get("error"):
            warnings.append("Mindestens eine zusätzliche Datenquelle war nicht erreichbar.")
        if rpki_check.get("status") == CheckStatus.UNKNOWN.value and rpki_check.get("raw", {}).get("error"):
            warnings.append("RPKI-Quelle nicht erreichbar oder unvollständig.")

        overall = evaluate_prefix_overall(rpki_check, registry_check, normalized_prefix, normalized_origin)

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
            },
            "details": {
                "whois": whois,
                "routing_status": routing_status,
                "source_errors": {
                    "whois": whois.get("error"),
                    "routing_status": routing_status.get("error"),
                    "rpki": rpki_check.get("raw", {}).get("error") if isinstance(rpki_check.get("raw"), dict) else None,
                    "registry": registry_check.get("raw", {}).get("error") if isinstance(registry_check.get("raw"), dict) else None,
                },
                "warnings": warnings,
                "demo_mode": settings.demo_mode,
            },
            "sources": ["RIPEstat rpki-validation", "RIPEstat routing-status", "RIPEstat whois"],
        }
