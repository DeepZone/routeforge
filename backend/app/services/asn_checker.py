from app.core.normalize import format_asn, normalize_asn
from app.core.status import CheckStatus
from app.services.ripe_stat_client import RipeStatClient


class AsnChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def check(self, asn_input: str) -> dict:
        asn = normalize_asn(asn_input)
        resource = format_asn(asn)
        overview = self.client.get("as-overview", {"resource": resource})
        prefixes = self.client.get("announced-prefixes", {"resource": resource})
        errors = []
        if "error" in overview:
            errors.append("as-overview nicht erreichbar")
        if "error" in prefixes:
            errors.append("announced-prefixes nicht erreichbar")
        status = CheckStatus.UNKNOWN.value if errors else CheckStatus.OK.value
        summary = f"ASN {resource} geprüft."
        return {
            "status": status,
            "summary": summary,
            "recommendations": ["Fehlende Datenquellen erneut abrufen."] if errors else ["Keine unmittelbare Aktion erforderlich."],
            "details": {
                "normalized_asn": asn,
                "resource": resource,
                "as_overview": overview.get("data", {}),
                "announced_prefixes": prefixes.get("data", {}),
                "warnings": errors,
                "source_errors": {
                    "as_overview": overview.get("error"),
                    "announced_prefixes": prefixes.get("error"),
                },
            },
            "sources": ["RIPEstat as-overview", "RIPEstat announced-prefixes"],
        }
