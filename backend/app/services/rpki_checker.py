from app.core.normalize import normalize_asn
from app.core.recommendations import evaluate_rpki_status
from app.core.status import CheckStatus
from app.services.ripe_stat_client import RipeStatClient


class RpkiChecker:
    def __init__(self, client: RipeStatClient):
        self.client = client

    def check(self, prefix: str, origin_as: str | None) -> dict:
        if not origin_as:
            evaluation = evaluate_rpki_status(None, prefix, None)
            return {**evaluation, "raw_status": None, "raw": {}}

        asn_number = normalize_asn(origin_as)
        payload = self.client.get("rpki-validation", {"resource": str(asn_number), "prefix": prefix})
        status_raw = payload.get("data", {}).get("status") if isinstance(payload, dict) else None
        evaluation = evaluate_rpki_status(status_raw, prefix, origin_as)

        if isinstance(payload, dict) and payload.get("error"):
            evaluation = {
                "status": CheckStatus.UNKNOWN.value,
                "summary": "RPKI status could not be determined",
                "explanation": "The RIPEstat source was unavailable or returned unexpected data.",
                "risk": "The assessment is incomplete.",
                "recommendations": [
                    "Review the API raw data.",
                    "Repeat the check later.",
                    "Vergleiche bei Bedarf mit einer zweiten Quelle oder einem lokalen RPKI-Validator.",
                ],
            }

        return {**evaluation, "raw_status": status_raw, "raw": payload}
