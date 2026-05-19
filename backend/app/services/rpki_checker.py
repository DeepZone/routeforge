from app.core.recommendations import default_recommendations
from app.core.status import CheckStatus
from app.core.normalize import format_asn
from app.services.ripe_stat_client import RipeStatClient


VALID_EXPL = "Das Prefix-Origin-Paar ist durch einen passenden ROA abgedeckt."
INVALID_EXPL = "Das Prefix wird mit einem Origin-AS geprüft, das nicht durch einen passenden ROA gedeckt ist. Validierende Netze können diese Route verwerfen."
NOT_FOUND_EXPL = "Für dieses Prefix-Origin-Paar wurde kein passender ROA gefunden. Das ist nicht automatisch kaputt, aber schwächt die Routing-Sicherheit."
UNKNOWN_EXPL = "Der Status konnte nicht zuverlässig ermittelt werden."


def map_rpki(raw_status: str | None) -> CheckStatus:
    if not raw_status:
        return CheckStatus.UNKNOWN
    n = raw_status.lower().replace("-", "_")
    if n == "valid":
        return CheckStatus.OK
    if n == "invalid":
        return CheckStatus.CRITICAL
    if n in {"not_found", "notfound"}:
        return CheckStatus.WARNING
    return CheckStatus.UNKNOWN


class RpkiChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def check(self, prefix: str, origin_asn: int) -> dict:
        payload = self.client.get("rpki-validation", {"resource": prefix, "prefix": prefix, "origin": format_asn(origin_asn)})
        status_raw = payload.get("data", {}).get("status") if isinstance(payload, dict) else None
        status = map_rpki(status_raw)
        explanation = {
            CheckStatus.OK: VALID_EXPL,
            CheckStatus.CRITICAL: INVALID_EXPL,
            CheckStatus.WARNING: NOT_FOUND_EXPL,
            CheckStatus.UNKNOWN: UNKNOWN_EXPL,
        }[status]
        return {
            "status": status.value,
            "raw_status": status_raw,
            "explanation": explanation,
            "recommendations": default_recommendations(status),
            "raw_response": payload,
        }
