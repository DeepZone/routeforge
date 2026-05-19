from app.core.normalize import format_asn, normalize_asn, validate_prefix
from app.core.status import CheckStatus
from app.services.ripe_db_client import RipeDbClient
from app.services.ripe_stat_client import RipeStatClient
from app.services.rpki_checker import RpkiChecker


class PrefixChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client
        self.ripe_db = RipeDbClient(client)
        self.rpki = RpkiChecker(client)

    def check(self, prefix: str, origin_as: str | None) -> dict:
        normalized_prefix = validate_prefix(prefix)
        whois = self.ripe_db.whois(normalized_prefix)
        routing_status = self.client.get("routing-status", {"resource": normalized_prefix})

        errors = []
        if "error" in whois or "error" in routing_status:
            errors.append("Mindestens eine Datenquelle war nicht erreichbar")

        if origin_as:
            oasn = normalize_asn(origin_as)
            rpki = self.rpki.check(normalized_prefix, oasn)
            status = CheckStatus(rpki["status"])
            recommendations = rpki["recommendations"]
            summary = f"Prefix {normalized_prefix} geprüft."
        else:
            rpki = {
                "status": CheckStatus.UNKNOWN.value,
                "explanation": "Für eine vollständige RPKI-Prüfung wird ein Origin-AS benötigt.",
                "raw_response": {},
            }
            status = CheckStatus.UNKNOWN
            summary = "Für eine vollständige RPKI-Prüfung wird ein Origin-AS benötigt."
            recommendations = ["Bitte Origin-AS ergänzen, zum Beispiel AS3333."]

        if errors and status == CheckStatus.OK:
            status = CheckStatus.UNKNOWN

        return {
            "status": status.value,
            "summary": summary,
            "recommendations": recommendations,
            "details": {
                "prefix": normalized_prefix,
                "origin_as": format_asn(normalize_asn(origin_as)) if origin_as else None,
                "rpki": rpki,
                "whois": whois.get("data", {}),
                "routing_status": routing_status.get("data", {}),
                "warnings": errors,
                "source_errors": {
                    "whois": whois.get("error"),
                    "routing_status": routing_status.get("error"),
                },
            },
            "sources": ["RIPEstat rpki-validation", "RIPEstat routing-status", "RIPEstat whois"],
        }
